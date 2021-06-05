from aws_cdk import (
    core,
    aws_codepipeline as codepipeline,
    aws_codepipeline_actions as codepipeline_actions,
    pipelines as pipelines
)

from utils.configBuilder import WmpConfig
from workflow_cdk.pipelines.application_stage import WmpApplicationStage


class WmpPipelineStack(core.Stack):

    def __init__(self, scope: core.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        source_artifact = codepipeline.Artifact()
        cloud_assembly_artifact = codepipeline.Artifact()
        # #
        # cpp = codepipeline.Pipeline(
        #     self,
        #     'Wmp-CodePipeline',
        #     pipeline_name='Wmp-Codepipeline',
        #     # artifact_bucket=s3.Bucket(self, 'artifact_bucket', encryption=s3.BucketEncryption.KMS),
        #     role=iam.Role(
        #         self,
        #         'Codepipeline-Role',
        #         assumed_by=iam.CompositePrincipal(
        #             iam.ServicePrincipal('eks.amazonaws.com'),
        #             iam.ServicePrincipal('s3.amazonaws.com'),
        #             iam.ServicePrincipal('codepipeline.amazonaws.com')
        #         ),
        #         role_name='wmp-pipeline-role',
        #         managed_policies=[
        #             iam.ManagedPolicy.from_aws_managed_policy_name(managed_policy_name='AmazonS3FullAccess')
        #         ]
        #     )
        # )
        #
        # #
        # sourceStage = cpp.add_stage(stage_name='Source', actions=[
        #     # codepipeline_actions.GitHubSourceAction(
        #     #     action_name="GitHub_SourceCode_Download",
        #     #     output=source_artifact,
        #     #     # oauth_token=SecretValue.plain_text('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'),
        #     #     oauth_token=SecretValue.secrets_manager('github_cdkpipeline'),
        #     #     trigger=codepipeline_actions.GitHubTrigger.POLL,
        #     #     owner="uxth",
        #     #     repo="cdkpipeline",
        #     #     branch='main'
        #     # )
        #     codepipeline_actions.BitBucketSourceAction(
        #         action_name='Github_sourcecode_download',
        #         connection_arn='arn:aws:codestar-connections:us-west-2:711208530951:connection/8b570e8a-f02c-426d-897a-90838859eff8',
        #         output=source_artifact,
        #         owner='uxth',
        #         repo='cdkpipeline',
        #         branch='main'
        #     )
        # ])
        # #
        # buildStage = cpp.add_stage(
        #     stage_name='Build',
        #     actions=[
        #         codepipeline.SimpleSynthAction(
        #             synth_command='cdk synth',
        #             cloud_assembly_artifact=cloud_assembly_artifact,
        #             source_artifact=source_artifact,
        #             install_commands=[
        #                 "mkdir -p wmp_cdk",
        #                 "npm install -g aws-cdk",
        #                 "pip install -r requirements.txt",
        #                 "python setup.py install"
        #             ]
        #         )
        #     ],
        #     placement=codepipeline.StagePlacement(just_after=sourceStage)
        # )
        #
        # pipeline = pipelines.CdkPipeline(
        #     self, "Wmp-CdkPipeline1",
        #     cloud_assembly_artifact=cloud_assembly_artifact,
        #     code_pipeline=cpp,
        #     self_mutating=True
        # )
        #
        pipeline = pipelines.CdkPipeline(
            self, "Pipeline",
            pipeline_name="Wmp-Codepipeline",
            cloud_assembly_artifact=cloud_assembly_artifact,
            source_action=
            # codepipeline_actions.GitHubSourceAction(
            #     action_name="GitHub_SourceCode_Download",
            #     output=source_artifact,
            #     # oauth_token=SecretValue.plain_text('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'),
            #     oauth_token=core.SecretValue.secrets_manager('github_cdkpipeline'),
            #     trigger=codepipeline_actions.GitHubTrigger.POLL,
            #     owner="uxth",
            #     repo="cdkpipeline",
            #     branch='main'
            # ),
            codepipeline_actions.BitBucketSourceAction(
                action_name='Github_sourcecode_download',
                connection_arn='arn:aws:codestar-connections:us-west-2:711208530951:connection/8b570e8a-f02c-426d-897a-90838859eff8',
                output=source_artifact,
                owner='uxth',
                repo='cdkpipeline',
                branch='main'
            ),
            synth_action=pipelines.SimpleSynthAction(
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
                'test-stage',
                config=WmpConfig('workflow_cdk/config/config.json', 'test')
            ),
            manual_approvals=False
        )
        teststage.add_manual_approval_action(action_name='Deploy_Dev')

        devstage = pipeline.add_application_stage(
            WmpApplicationStage(
                self,
                'dev-stage',
                config=WmpConfig('workflow_cdk/config/config.json', 'dev')
            )
        )
