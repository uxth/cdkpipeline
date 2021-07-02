from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_eks as eks
from aws_cdk import aws_iam as iam
from aws_cdk import core
from cdk.common.stacks.vpc import VpcStack

from utils.configBuilder import Config
from utils.randGenerator import stringGenerator


class EksStack(core.Stack):
    def __init__(self, scope: core.Construct, construct_id: str, vpc_stack: VpcStack, config: Config, **kwargs) -> \
            None:
        super().__init__(scope, construct_id, **kwargs)
        eks_user = iam.User(
            self, id="map-eks-user",
            user_name=config.getValue('eks.admin_username'),
            password=core.SecretValue.plain_text(stringGenerator(24))  # this need to be changed
        )
        policy = iam.Policy(
            self, id='map-eks-policy',
            policy_name='EKSFullAccessPolicy',
            statements=[
                iam.PolicyStatement(
                    sid='EKSFullAccess',
                    effect=iam.Effect.ALLOW,
                    actions=['eks:*'],
                    resources=['*']
                )
            ],
            users=[eks_user]
        )

        eks_role = iam.Role(
            self, id="map-eks-admin",
            assumed_by=iam.ArnPrincipal(arn=eks_user.user_arn),
            role_name='map-eks-cluster-role'
        )

        self.cluster = eks.Cluster(
            self, id='map-eks-cluster',
            cluster_name=config.getValue('eks.cluster_name'),
            version=eks.KubernetesVersion.V1_19,
            vpc=vpc_stack.vpc,
            vpc_subnets=[ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE)],
            default_capacity=0,
            masters_role=eks_role
        )

        self.cluster.add_nodegroup_capacity(
            'map-eks-nodegroup',
            instance_types=[ec2.InstanceType(config.getValue('eks.nodegroup.instance_type'))],
            disk_size=config.getValue('eks.nodegroup.disk_size'),
            min_size=config.getValue('eks.nodegroup.min_size'),
            max_size=config.getValue('eks.nodegroup.max_size'),
            desired_size=config.getValue('eks.nodegroup.desired_size'),
            subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE),
            capacity_type=eks.CapacityType.SPOT
        )
