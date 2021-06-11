from aws_cdk import (
    core,
    aws_eks as eks,
    aws_ec2 as ec2,
    aws_iam as iam,
    aws_rds as rds,
    aws_secretsmanager as secretemanager
)

from utils import yamlParser
from utils.configBuilder import WmpConfig
from workflow_cdk.stacks.eks_stack import EksStack
from workflow_cdk.stacks.vpc_stack import VpcStack


class RdsStack(core.Stack):
    def __init__(self, scope: core.Construct, construct_id: str, vpc_stack: VpcStack, eks_cluster: EksStack,
                 config: WmpConfig, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        security_group = ec2.SecurityGroup(
            self,
            'SanDiegoOfficeSG',
            vpc=vpc_stack.vpc,
            security_group_name='SanDiegoOfficeSG'
        )
        security_group.add_ingress_rule(
            ec2.Peer.ipv4('64.187.215.19/32'),
            ec2.Port.all_tcp()
        )

        rds_cluster = rds.DatabaseCluster(
            self,
            config.getValue('rds.database_name'),
            default_database_name=config.getValue('rds.database_name'),
            engine=rds.DatabaseClusterEngine.aurora_postgres(
                version=rds.AuroraPostgresEngineVersion.VER_12_4
            ),
            credentials=rds.Credentials.from_generated_secret(
                username=config.getValue('rds.admin_username'),
                secret_name=config.getValue('rds.admin_secret_name')
            ),
            instances=config.getValue('rds.instances'),
            instance_props=rds.InstanceProps(
                vpc=vpc_stack.vpc,
                allow_major_version_upgrade=False,
                auto_minor_version_upgrade=False,
                delete_automated_backups=True,
                publicly_accessible=True,
                security_groups=[security_group],
                instance_type=ec2.InstanceType(config.getValue('rds.instanceType'))
            ),
            iam_authentication=True,
            port=config.getValue('rds.port'),
            subnet_group=rds.SubnetGroup(
                self,
                'rds_subnet_group',
                subnet_group_name='rds_subnet_group',
                vpc=vpc_stack.vpc,
                removal_policy=core.RemovalPolicy.DESTROY,
                vpc_subnets=ec2.SubnetSelection(
                    subnet_type=ec2.SubnetType.PUBLIC
                )
            )
        )
        rds_cluster.connections.allow_from(
            other=eks_cluster.cluster,
            port_range=ec2.Port.all_tcp()
        )

        manifests = yamlParser.readManifest(config.getValue('rds.manifest.files'))
        postgres_service = yamlParser.readYaml(config.getValue('rds.postgres_service'))
        postgres_service['spec']['externalName'] = rds_cluster.cluster_endpoint.hostname
        manifests.append(postgres_service)

        eks.KubernetesManifest(
            self,
            id='rds-manifests',
            cluster=eks_cluster.cluster,
            manifest=manifests,
            overwrite=True
        )
