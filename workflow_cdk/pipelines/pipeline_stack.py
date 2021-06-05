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
                'Test_Stage',
                config=WmpConfig('workflow_cdk/config/test.json', 'config')
            ),
            manual_approvals=False
        )
        teststage.add_manual_approval_action(action_name='Ready_To_Move_To_Next_Stage')

        devstage = pipeline.add_application_stage(
            WmpApplicationStage(
                self,
                'Dev_Stage',
                config=WmpConfig('workflow_cdk/config/dev.json', 'config')
            )
        )
