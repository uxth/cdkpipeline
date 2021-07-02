from aws_cdk import core
from aws_cdk import aws_s3 as s3
from cdk.common.stacks.vpc import VpcStack
from utils.configBuilder import Config


class S3Stack(core.Stack):
    def __init__(self, scope: core.Construct, construct_id: str, vpc_stack: VpcStack, config: Config, **kwargs) -> None:
        s3.Bucket(
            self,
            'release_manager',
            bucket_name=config.getValue('release_manager.s3_bucket_name')
        )
