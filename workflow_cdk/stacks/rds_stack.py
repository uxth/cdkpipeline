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
        rdsInstance = rds.DatabaseInstance(
            self, 'MapData',
            database_name=config.getValue('rds.database_name'),
            engine=rds.DatabaseInstanceEngine.postgres(
                version=rds.PostgresEngineVersion.VER_12
            ),
            vpc=vpc_stack.vpc,
            port=config.getValue('rds.port'),
            credentials=rds.Credentials.from_generated_secret(
                username=config.getValue('rds.admin_username'),
                secret_name=config.getValue('rds.admin_secret_name')
            ),
            instance_type=ec2.InstanceType.of(
                ec2.InstanceClass(config.getValue('rds.instanceClass')),
                ec2.InstanceSize(config.getValue('rds.instanceSize'))
            ),
            multi_az=False,
            allocated_storage=config.getValue('rds.allocated_storage'),
            max_allocated_storage=config.getValue('rds.max_allocated_storage'),
            allow_major_version_upgrade=False,
            auto_minor_version_upgrade=False,
            backup_retention=core.Duration.days(0),
            delete_automated_backups=True,
            deletion_protection=False,
            publicly_accessible=False,
            removal_policy=core.RemovalPolicy(config.getValue('rds.removalPolicy')),
            iam_authentication=True
        )
        rdsInstance.connections.allow_from(
            other=eks_cluster.cluster,
            port_range=ec2.Port.all_tcp()
        )

        manifests = yamlParser.readManifest(config.getValue('rds.manifest.files'))
        postgres_Service = yamlParser.readYaml(config.getValue('rds.postgres_service'))
        postgres_Service['spec']['externalName'] = rdsInstance.instance_endpoint.hostname
        manifests.append(postgres_Service)

        eks.KubernetesManifest(
            self,
            id='rds-manifests',
            cluster=eks_cluster.cluster,
            manifest=manifests,
            overwrite=True
        )
