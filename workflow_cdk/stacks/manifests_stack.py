from aws_cdk import (
    core,
    aws_eks as eks
)

from utils.configBuilder import WmpConfig
from workflow_cdk.stacks.eks_stack import EksStack
from utils import yamlParser


class ManifestsStack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, eks_stack: EksStack, config: WmpConfig,
                 **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        eks.KubernetesManifest(
            self,
            id='wmp-manifest',
            cluster=eks_stack.cluster,
            manifest=yamlParser.readManifest(
                paths=config.getValue('manifests.files')
            ),
            overwrite=True
        )
