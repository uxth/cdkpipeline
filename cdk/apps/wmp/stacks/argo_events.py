from aws_cdk import aws_eks as eks
from aws_cdk import core
from cdk.common.stacks.eks import EksStack

from utils import yamlParser
from utils.configBuilder import Config


class ArgoEventsStack(core.Stack):
    def __init__(self, scope: core.Construct, construct_id: str, eks_stack: EksStack, config: Config, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        # install argo events
        eks.HelmChart(
            self,
            id='wmp-argo-events',
            cluster=eks_stack.cluster,
            chart='argo-events',
            repository='https://argoproj.github.io/argo-helm',
            namespace='argo', release=config.getValue('wmp.argo-events.release'),
            values=yamlParser.readYaml(path=config.getValue('wmp.argo-events.valuesPath')),
            wait=True
        )

