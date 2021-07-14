from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_rds as rds
from aws_cdk import core
from aws_cdk import aws_secretsmanager as secretmanager
from cdk.common.stacks.eks import EksStack
from cdk.common.stacks.vpc import VpcStack

from utils.configBuilder import Config


class RdsStack(core.Stack):
    def __init__(self, scope: core.Construct, construct_id: str, vpc_stack: VpcStack, eks_cluster: EksStack,
                 config: Config, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        security_group = ec2.SecurityGroup(
            self,
            'SanDiegoOfficeSG',
            vpc=vpc_stack.vpc,
            security_group_name='SanDiegoOfficeSG'
        )

        security_group.add_ingress_rule(
            ec2.Peer.ipv4('10.160.0.0/16'),
            ec2.Port.tcp(config.getValue('rds.port'))
        )

        security_group.add_ingress_rule(
            ec2.Peer.ipv4('10.162.0.0/16'),
            ec2.Port.tcp(config.getValue('rds.port'))
        )

        security_group.add_ingress_rule(
            ec2.Peer.ipv4('10.161.48.0/22'),
            ec2.Port.tcp(config.getValue('rds.port'))
        )
        self.credentials = rds.Credentials.from_generated_secret(
            username=config.getValue('rds.admin_username'),
            secret_name=config.getValue('rds.admin_secret_name')
        )
        self.rds_cluster = rds.DatabaseCluster(
            self,
            config.getValue('rds.database_name'),
            default_database_name=config.getValue('rds.database_name'),
            engine=rds.DatabaseClusterEngine.aurora_postgres(
                version=rds.AuroraPostgresEngineVersion.VER_12_4
            ),
            credentials=self.credentials,
            instances=config.getValue('rds.instances'),
            instance_props=rds.InstanceProps(
                vpc=vpc_stack.vpc,
                allow_major_version_upgrade=False,
                auto_minor_version_upgrade=False,
                delete_automated_backups=True,
                publicly_accessible=False,
                security_groups=[security_group],
                instance_type=ec2.InstanceType(config.getValue('rds.instanceType'))
            ),
            iam_authentication=True,
            port=config.getValue('rds.port'),
            subnet_group=rds.SubnetGroup(
                self,
                'rds_subnet_group',
                subnet_group_name='rds_subnet_group',
                description='This is the subnet group for TuSimple Office access.',
                vpc=vpc_stack.vpc,
                removal_policy=core.RemovalPolicy.DESTROY,
                vpc_subnets=ec2.SubnetSelection(
                    subnet_type=ec2.SubnetType.PRIVATE
                )
            )
        )
        self.rds_cluster.connections.allow_from(
            other=eks_cluster.cluster,
            port_range=ec2.Port.all_tcp()
        )
        self.secret_arn = self.format_arn(
            service="secretmanager",
            resource="secret",
            resource_name=config.getValue('rds.admin_secret_name'),
            sep=':'
        )
