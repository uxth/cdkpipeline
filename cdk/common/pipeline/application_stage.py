
from aws_cdk import core
from cdk.apps.was.stacks.manifests import ManifestsStack as WasManifestsStack
from cdk.apps.wmp.stacks.argo_events import ArgoEventsStack
from cdk.apps.wmp.stacks.manifests import ManifestsStack as WmpManifestsStack
from cdk.apps.wmp.stacks.argo_workflows import ArgoWorkflowsStack
from cdk.common.stacks.cassandra import CassandraStack
from cdk.common.stacks.eks import EksStack
from cdk.apps.wmp.stacks.kafka import KafkaStack
from cdk.common.stacks.rds import RdsStack
from cdk.common.stacks.vpc import VpcStack
from cdk.common.stacks.s3 import S3Stack

from utils.configBuilder import Config


class ApplicationStage(core.Stage):
    def __init__(self, scope: core.Construct, id: str, config: Config, **kwargs):
        super().__init__(scope, id, **kwargs)
        env = core.Environment(
            account=config.getValue('common.AWSAccountID'),
            region=config.getValue('common.AWSProfileRegion')
        )
        vpc_stack = VpcStack(
            self, "map-vpc",
            config=config,
            env=env,
        )
        cassandra_stack = CassandraStack(
            self, "map-cassandra",
            config=config,
            env=env
        )
        eks_stack = EksStack(
            self, 'map-eks',
            vpc_stack=vpc_stack,
            config=config,
            env=env)
        eks_stack.add_dependency(vpc_stack)

        rds_stack = RdsStack(
            self, 'map-rds',
            vpc_stack=vpc_stack,
            eks_cluster=eks_stack,
            config=config,
            env=env
        )
        rds_stack.add_dependency(eks_stack)

        kafka_stack = KafkaStack(
            self, 'kafka',
            eks_stack=eks_stack,
            config=config,
            env=env)
        kafka_stack.add_dependency(eks_stack)

        argo_workflows_stack = ArgoWorkflowsStack(
            self, 'argo-workflows',
            eks_stack=eks_stack,
            rds_stack=rds_stack,
            config=config,
            env=env)
        argo_workflows_stack.add_dependency(eks_stack)
        argo_workflows_stack.add_dependency(rds_stack)

        argo_events_stack = ArgoEventsStack(
            self, 'argo-events',
            eks_stack=eks_stack,
            config=config,
            env=env)
        argo_events_stack.add_dependency(argo_workflows_stack)
        argo_events_stack.add_dependency(kafka_stack)

        s3_stack = S3Stack(
            self, 's3',
            config=config,
            env=env)

        was_manifests_stack = WasManifestsStack(
            self, 'was-manifests',
            eks_stack=eks_stack,
            config=config,
            env=env)
        was_manifests_stack.add_dependency(eks_stack)

        wmp_manifests_stack = WmpManifestsStack(
            self, 'wmp-manifests',
            eks_stack=eks_stack,
            config=config,
            env=env)
        wmp_manifests_stack.add_dependency(argo_events_stack)
