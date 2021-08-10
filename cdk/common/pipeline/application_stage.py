
from aws_cdk import core
from cdk.common.stacks.argo_workflows import ArgoWorkflowsStack
from cdk.common.stacks.argo_cd import ArgoCDStack
from cdk.common.stacks.baseline_app import BaselineAppStack
from cdk.common.stacks.cassandra import CassandraStack
from cdk.common.stacks.eks import EksStack
from cdk.common.stacks.iam import IamStack
from cdk.common.stacks.rds import RdsStack
from cdk.common.stacks.s3 import S3Stack

from utils.configBuilder import Config


class ApplicationStage(core.Stage):
    def __init__(self, scope: core.Construct, id: str, config: Config, **kwargs):
        super().__init__(scope, id, **kwargs)
        env = core.Environment(
            account=config.getValue('common.AWSAccountID'),
            region=config.getValue('common.AWSProfileRegion')
        )
        cassandra_stack = CassandraStack(
            self, "map-cassandra",
            config=config,
            env=env
        )
        eks_stack = EksStack(
            self, 'map-eks',
            config=config,
            env=env)

        argo_cd_stack = ArgoCDStack(
            self, 'argo-cd',
            eks_stack=eks_stack,
            config=config,
            env=env
        )
        argo_cd_stack.add_dependency(eks_stack)

        baseline_app_stack = BaselineAppStack(
            self, 'baseline-app',
            eks_stack=eks_stack,
            config=config,
            env=env
        )
        baseline_app_stack.add_dependency(argo_cd_stack)

        rds_stack = RdsStack(
            self, 'map-rds',
            config=config,
            env=env
        )

        argo_workflows_stack = ArgoWorkflowsStack(
            self, 'argo-workflows',
            eks_stack=eks_stack,
            config=config,
            env=env)
        argo_workflows_stack.add_dependency(eks_stack)
        argo_workflows_stack.add_dependency(rds_stack)

        s3_stack = S3Stack(
            self, 's3',
            config=config,
            env=env
        )

        iam_stack = IamStack(
            self, 'iam-users',
            config=config,
            eks_stack=eks_stack,
            env=env
        )
        iam_stack.add_dependency(eks_stack)

