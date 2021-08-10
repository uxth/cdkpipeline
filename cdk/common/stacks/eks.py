import boto3
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_eks as eks
from aws_cdk import aws_iam as iam
from aws_cdk import core

from utils import yamlParser
from utils.configBuilder import Config
from utils.randGenerator import stringGenerator


class EksStack(core.Stack):
    def __init__(self, scope: core.Construct, construct_id: str, config: Config, **kwargs) -> \
            None:
        super().__init__(scope, construct_id, **kwargs)
        vpc = ec2.Vpc.from_lookup(
            self, 'defaultVpc',
            vpc_id=config.getValue('vpc.vpc_id')
        )
        eks_user = iam.User(
            self, id="map-eks-user",
            user_name=config.getValue('eks.admin_username'),
            password=core.SecretValue.plain_text(stringGenerator(24))
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
            role_name=config.getValue('eks.cluster_role_name')
        )

        security_group = ec2.SecurityGroup(
            self,
            'EKS_SG',
            vpc=vpc,
            security_group_name='EKS_SG',
            allow_all_outbound=True
        )

        self.cluster = eks.Cluster(
            self, id='map-eks-cluster',
            cluster_name=config.getValue('eks.cluster_name'),
            version=eks.KubernetesVersion.V1_19,
            vpc=vpc,
            vpc_subnets=[ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PRIVATE,
                one_per_az=True
            )],
            default_capacity=0,
            masters_role=eks_role,
            security_group=security_group,
            endpoint_access=eks.EndpointAccess.PUBLIC_AND_PRIVATE
        )

        node_group = self.cluster.add_nodegroup_capacity(
            'map-eks-nodegroup',
            instance_types=[ec2.InstanceType(config.getValue('eks.nodegroup.instance_type'))],
            disk_size=config.getValue('eks.nodegroup.disk_size'),
            min_size=config.getValue('eks.nodegroup.min_size'),
            max_size=config.getValue('eks.nodegroup.max_size'),
            desired_size=config.getValue('eks.nodegroup.desired_size'),
            subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PRIVATE,
                one_per_az=True
            ),
            capacity_type=eks.CapacityType.SPOT
        )
        node_group.role.add_managed_policy(
            iam.Policy(
                self, id='node-group-policy',
                policy_name='NodeGroupPolicy',
                statements=[
                    iam.PolicyStatement(
                        sid='S3FullAccess',
                        effect=iam.Effect.ALLOW,
                        actions=['s3:*'],
                        resources=['*']
                    ),
                    iam.PolicyStatement(
                        sid='SecretManagerFullAccess',
                        effect=iam.Effect.ALLOW,
                        actions=['secretsmanager:*'],
                        resources=['*']
                    ),
                    iam.PolicyStatement(
                        sid='RDSFullAccess',
                        effect=iam.Effect.ALLOW,
                        actions=['rds:*'],
                        resources=['*']
                    ),
                    iam.PolicyStatement(
                        sid='EKSFullAccess',
                        effect=iam.Effect.ALLOW,
                        actions=['eks:*'],
                        resources=['*']
                    ),
                ],
                users=[eks_user]
            )
        )
        eks.KubernetesManifest(
            self, id='namespaces',
            cluster=self.cluster,
            manifest=yamlParser.readManifest(config.getValue('eks.manifests'))
        )


