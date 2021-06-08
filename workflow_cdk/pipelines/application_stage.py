
from aws_cdk import (
    core
)

from utils.configBuilder import WmpConfig
from workflow_cdk.stacks.argo_events_stack import ArgoEventsStack
from workflow_cdk.stacks.argo_workflows_stack import ArgoWorkflowsStack
from workflow_cdk.stacks.eks_stack import EksStack
from workflow_cdk.stacks.kafka_stack import KafkaStack
from workflow_cdk.stacks.manifests_stack import ManifestsStack
from workflow_cdk.stacks.rds_stack import RdsStack
from workflow_cdk.stacks.vpc_stack import VpcStack


class WmpApplicationStage(core.Stage):
    def __init__(self, scope: core.Construct, id: str, config: WmpConfig, **kwargs):
        super().__init__(scope, id, **kwargs)
        env = core.Environment(
            account=config.getValue('AWSAccountID'),
            region=config.getValue('AWSProfileRegion')
        )
        vpc_stack = VpcStack(
            self, "wmp-vpc",
            config=config,
            env=env)

        eks_stack = EksStack(
            self, 'wmp-eks',
            vpc=vpc_stack.vpc,
            config=config,
            env=env)
        eks_stack.add_dependency(vpc_stack)

        rds_stack = RdsStack(
            self, 'map-rds',
            vpc=vpc_stack.vpc,
            eksCluster=eks_stack.cluster,
            config=config,
            env=env
        )
        rds_stack.add_dependency(eks_stack)

        kafka_stack = KafkaStack(
            self, 'wmp-kafka',
            eks_stack=eks_stack,
            config=config,
            env=env)
        kafka_stack.add_dependency(eks_stack)

        argo_workflows_stack = ArgoWorkflowsStack(
            self, 'wmp-argo-workflows',
            eks_stack=eks_stack,
            config=config,
            env=env)
        argo_workflows_stack.add_dependency(eks_stack)

        argo_events_stack = ArgoEventsStack(
            self, 'wmp-argo-events',
            eks_stack=eks_stack,
            config=config,
            env=env)
        argo_events_stack.add_dependency(argo_workflows_stack)
        argo_events_stack.add_dependency(kafka_stack)

        manifests_stack = ManifestsStack(
            self, 'wmp-manifests',
            eks_stack=eks_stack,
            config=config,
            env=env)
        manifests_stack.add_dependency(argo_events_stack)
