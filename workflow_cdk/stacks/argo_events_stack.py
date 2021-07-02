from aws_cdk import (
    core,
    aws_eks as eks
)

from utils.configBuilder import WmpConfig
from workflow_cdk.stacks.eks_stack import EksStack
from utils import yamlParser


class ArgoEventsStack(core.Stack):
    def __init__(self, scope: core.Construct, construct_id: str, eks_stack: EksStack, config: WmpConfig, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        # install argo events
        eks.HelmChart(
            self,
            id='wmp-argo-events',
            cluster=eks_stack.cluster,
            chart='argo-events',
            repository='https://argoproj.github.io/argo-helm',
            namespace='argo', release=config.getValue('argo-events.release'),
            values=yamlParser.readYaml(path=config.getValue('argo-events.valuesPath')),
            wait=True
        )

