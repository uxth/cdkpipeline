from aws_cdk import (
    core,
    aws_eks as eks,
    aws_ec2 as ec2,
    aws_iam as iam,
    aws_rds as rds,
    aws_secretsmanager as secretemanager
)
from utils.configBuilder import WmpConfig


class RdsStack(core.Stack):
    def __init__(self, scope: core.Construct, construct_id: str, vpc: ec2.Vpc, eksCluster: eks.Cluster,
                 config: WmpConfig, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        rdsInstance = rds.DatabaseInstance(
            self, 'MapData',
            database_name=config.getValue('rds.database_name'),
            engine=rds.DatabaseInstanceEngine.postgres(
                version=rds.PostgresEngineVersion.VER_13
            ),
            vpc=vpc,
            port=config.getValue('rds.port'),
            credentials=rds.Credentials.from_generated_secret(
                username=config.getValue('rds.admin_username'),
                secret_name=config.getValue('rds.admin_secret_name')
            ),
            instance_type=ec2.InstanceType.of(
                ec2.InstanceClass.BURSTABLE3,
                ec2.InstanceSize.MICRO
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
            removal_policy=core.RemovalPolicy.DESTROY
        )
        rdsInstance.connections.allow_from(
            other=eksCluster,
            port_range=ec2.Port.all_tcp()
        )
