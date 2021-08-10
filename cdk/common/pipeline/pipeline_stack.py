from aws_cdk import aws_codepipeline as codepipeline
from aws_cdk import aws_codepipeline_actions as codepipeline_actions
from aws_cdk import aws_sns as sns
from aws_cdk import aws_iam as iam
from aws_cdk import core
from aws_cdk import pipelines as pipelines
from cdk.common.pipeline.application_stage import ApplicationStage
from cloudcomponents import (
    cdk_developer_tools_notifications as notifications
)

from utils.configBuilder import Config


class PipelineStack(core.Stack):

    def __init__(self, scope: core.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        source_artifact = codepipeline.Artifact()
        cloud_assembly_artifact = codepipeline.Artifact()
        pipeline = pipelines.CdkPipeline(
            self, "MapCdkPipeline",
            cloud_assembly_artifact=cloud_assembly_artifact,
            pipeline_name='Map_Infrastructure_CodePipeline',
            source_action=codepipeline_actions.CodeStarConnectionsSourceAction(
                action_name='SourceCode',
                connection_arn='arn:aws:codestar-connections:us-west-2:192878884426:connection/81711257-3407'
                               '-4781-bc43-5e5f7db2fadc',
                output=source_artifact,
                owner='TuSimple',
                repo='map-aws-infra',
                branch='ningxu/argo_cd',
                role=iam.Role.from_role_arn(
                    self, 'cross_account_role',
                    role_arn='arn:aws:iam::192878884426:role/Cross_Account_Role'
                ),
                trigger_on_push=True
            ),
            synth_action=pipelines.SimpleSynthAction(
                action_name='SourceCode_Synthesis',
                synth_command='cdk synth',
                cloud_assembly_artifact=cloud_assembly_artifact,
                source_artifact=source_artifact,
                role_policy_statements=[iam.PolicyStatement(
                    sid='SecretsManagerFullAccess',
                    effect=iam.Effect.ALLOW,
                    actions=['secretsmanager:*'],
                    resources=['*']
                )],
                install_commands=[
                    "mkdir -p map_cdk",
                    "npm install -g aws-cdk",
                    "pip install -r requirements.txt"
                ]
            ),
            self_mutating=True
        )

        teststage = pipeline.add_application_stage(
            ApplicationStage(
                self,
                'Test-Stage',
                config=Config('config/test.json')
            ),
            manual_approvals=False
        )
        teststage.add_manual_approval_action(action_name='Promote')

        devstage = pipeline.add_application_stage(
            ApplicationStage(
                self,
                'Dev-Stage',
                config=Config('config/dev.json')
            )
        )

        snsTopic = sns.Topic(
            self,
            'SnsTopic',
            topic_name='SnsTopic',
            display_name='Map_Automation_Notifications'
        )
        emailSubscription = sns.Subscription(
            self,
            'EmailSubscription',
            topic=snsTopic,
            endpoint='ning.xu@tusimple.ai',
            protocol=sns.SubscriptionProtocol.EMAIL
        )
        notifications.PipelineNotificationRule(
            self,
            'MapCdkPipelineNotificationRule',
            name='MapCdkPipelineNotificationRule',
            pipeline=pipeline.code_pipeline,
            events=[
                # notifications.PipelineEvent.ACTION_EXECUTION_SUCCEEDED,
                notifications.PipelineEvent.ACTION_EXECUTION_FAILED,
                # notifications.PipelineEvent.ACTION_EXECUTION_CANCELED,
                # notifications.PipelineEvent.ACTION_EXECUTION_STARTED,
                notifications.PipelineEvent.STAGE_EXECUTION_STARTED,
                notifications.PipelineEvent.STAGE_EXECUTION_SUCCEEDED,
                # notifications.PipelineEvent.STAGE_EXECUTION_RESUMED,
                # notifications.PipelineEvent.STAGE_EXECUTION_CANCELED,
                notifications.PipelineEvent.STAGE_EXECUTION_FAILED,
                notifications.PipelineEvent.PIPELINE_EXECUTION_FAILED,
                # notifications.PipelineEvent.PIPELINE_EXECUTION_CANCELED,
                notifications.PipelineEvent.PIPELINE_EXECUTION_STARTED,
                # notifications.PipelineEvent.PIPELINE_EXECUTION_RESUMED,
                notifications.PipelineEvent.PIPELINE_EXECUTION_SUCCEEDED,
                # notifications.PipelineEvent.PIPELINE_EXECUTION_SUPERSEDED,
                # notifications.PipelineEvent.MANUAL_APPROVAL_FAILED,
                notifications.PipelineEvent.MANUAL_APPROVAL_NEEDED,
                notifications.PipelineEvent.MANUAL_APPROVAL_SUCCEEDED,
            ],
            targets=[notifications.SnsTopic(snsTopic)]
        )
