from aws_cdk import (
    core,
    aws_eks as eks
)

from utils.configBuilder import WmpConfig
from workflow_cdk.stacks.eks_stack import EksStack
from utils import yamlParser


class KafkaStack(core.Stack):
    def __init__(self, scope: core.Construct, construct_id: str, eks_stack: EksStack, config: WmpConfig, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        # install kafka
        eks.HelmChart(
            self, id='wmp-kafka', cluster=eks_stack.cluster, chart='kafka',
            repository='https://charts.bitnami.com/bitnami',
            namespace='argo', release=config.getValue('kafka.release'),
            values=yamlParser.readYaml(path=config.getValue('kafka.valuesPath')),
            wait=True
        )
