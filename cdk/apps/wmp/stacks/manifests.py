from aws_cdk import aws_eks as eks
from aws_cdk import core
from cdk.common.stacks.eks import EksStack

from utils import yamlParser
from utils.configBuilder import Config


class ManifestsStack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, eks_stack: EksStack, config: Config,
                 **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        eks.KubernetesManifest(
            self,
            id='wmp-manifest',
            cluster=eks_stack.cluster,
            manifest=yamlParser.readManifest(
                paths=config.getValue('wmp.manifests.files')
            ),
            overwrite=True
        )
