from aws_cdk import aws_eks as eks
from aws_cdk import core
from cdk.common.stacks.eks import EksStack

from utils import yamlParser
from utils.configBuilder import Config


class KafkaStack(core.Stack):
    def __init__(self, scope: core.Construct, construct_id: str, eks_stack: EksStack, config: Config, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        # install kafka
        eks.HelmChart(
            self, id='wmp-kafka', cluster=eks_stack.cluster, chart='kafka',
            repository='https://charts.bitnami.com/bitnami',
            namespace='argo', release=config.getValue('wmp.kafka.release'),
            values=yamlParser.readYaml(path=config.getValue('wmp.kafka.valuesPath')),
            wait=True
        )
