from aws_cdk import (
     aws_ec2 as ec2,
     core
)

from utils.configBuilder import WmpConfig


class VpcStack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, config: WmpConfig, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # The code that defines your stack goes here
        # self.vpc = ec2.Vpc(
        #     self,
        #     "wmp-vpc",
        #     cidr=config.getValue('vpc.cidr')
        # )
        self.vpc = ec2.Vpc.from_lookup(
            self, 'defaultVpc',
            vpc_id=config.getValue('vpc.vpc_id'),
            vpc_name=config.getValue('vpc.vpc_name')
        )
