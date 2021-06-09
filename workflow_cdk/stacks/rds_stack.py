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
                # instance_type=ec2.InstanceType.of(
                #     ec2.InstanceClass(config.getValue('rds.instanceClass')),
                #     ec2.InstanceSize(config.getValue('rds.instanceSize'))
                # )
                instance_type=ec2.InstanceType('db.t3.medium')
            ),
            iam_authentication=True,
            port=config.getValue('rds.port')
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
