from aws_cdk import (
    core,
    aws_codepipeline as codepipeline,
    aws_codepipeline_actions as codepipeline_actions,
    pipelines as pipelines,
    aws_sns as sns
)
from cloudcomponents import (
    cdk_chatops as chatops,
    cdk_developer_tools_notifications as notifications
)
from utils.configBuilder import WmpConfig
from workflow_cdk.pipelines.application_stage import WmpApplicationStage


class WmpPipelineStack(core.Stack):

    def __init__(self, scope: core.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        source_artifact = codepipeline.Artifact()
        cloud_assembly_artifact = codepipeline.Artifact()

        pipeline = pipelines.CdkPipeline(
            self, "Pipeline",
            pipeline_name="Wmp_Infrastructure_Codepipeline",
            cloud_assembly_artifact=cloud_assembly_artifact,
            source_action=codepipeline_actions.BitBucketSourceAction(
                action_name='SourceCode_Download',
                connection_arn='arn:aws:codestar-connections:us-west-2:711208530951:connection/'
                               '8b570e8a-f02c-426d-897a-90838859eff8',
                output=source_artifact,
                owner='uxth',
                repo='cdkpipeline',
                branch='main'
            ),
            synth_action=pipelines.SimpleSynthAction(
                action_name='SourceCode_Synthesis',
                synth_command='cdk synth',
                cloud_assembly_artifact=cloud_assembly_artifact,
                source_artifact=source_artifact,
                install_commands=[
                    "mkdir -p wmp_cdk",
                    "npm install -g aws-cdk",
                    "pip install -r requirements.txt"
                ]
            ),
            self_mutating=True
        )

        teststage = pipeline.add_application_stage(
            WmpApplicationStage(
                self,
                'Test-Stage',
                config=WmpConfig('workflow_cdk/config/test.json', 'config')
            ),
            manual_approvals=False
        )
        teststage.add_manual_approval_action(action_name='Ready_To_Move_To_Next_Stage')

        devstage = pipeline.add_application_stage(
            WmpApplicationStage(
                self,
                'Dev-Stage',
                config=WmpConfig('workflow_cdk/config/dev.json', 'config')
            )
        )

        snsTopic = sns.Topic(
            self,
            'SnsTopic',
            topic_name='SnsTopic',
            display_name='WMP Automation Notifications'
        )
        emailSubscription = sns.Subscription(
            self,
            'EmailSubscription',
            topic=snsTopic,
            endpoint='mapawsnotification@tusimple.ai',
            protocol=sns.SubscriptionProtocol.EMAIL
        )
        notifications.PipelineNotificationRule(
            self,
            'PipelineNotificationRule',
            name='PipelineNotificationRule',
            pipeline=pipeline.code_pipeline,
            events=[
                # notifications.PipelineEvent.PIPELINE_EXECUTION_STARTED,
                notifications.PipelineEvent.PIPELINE_EXECUTION_FAILED,
                notifications.PipelineEvent.PIPELINE_EXECUTION_SUCCEEDED,
                # notifications.PipelineEvent.ACTION_EXECUTION_STARTED,
                # notifications.PipelineEvent.ACTION_EXECUTION_SUCCEEDED,
                notifications.PipelineEvent.ACTION_EXECUTION_FAILED,
                notifications.PipelineEvent.MANUAL_APPROVAL_NEEDED,
                notifications.PipelineEvent.MANUAL_APPROVAL_SUCCEEDED,
                # notifications.PipelineEvent.MANUAL_APPROVAL_FAILED,
                # notifications.PipelineEvent.STAGE_EXECUTION_STARTED,
                notifications.PipelineEvent.STAGE_EXECUTION_SUCCEEDED,
                notifications.PipelineEvent.STAGE_EXECUTION_FAILED,
            ],
            targets=[
                # notifications.SlackChannel(chatops.SlackChannelConfiguration(
                #     self,
                #     'Slack',
                #     configuration_name='Slack',
                #     slack_workspace_id='TGK603YCB',
                #     slack_channel_id='C023X8XKCF8'
                # ))
                notifications.SnsTopic(snsTopic)
            ]
        )
