from aws_cdk import core
from aws_cdk import aws_cassandra as cassandra

from utils.configBuilder import Config


class CassandraStack(core.Stack):
    def __init__(self, scope: core.Construct, construct_id: str, config: Config, **kwargs) -> \
            None:
        super().__init__(scope, construct_id, **kwargs)
        cassandra.CfnKeyspace(
            self,
            'cassandra_keyspace',
            keyspace_name=config.getValue('cassandra.keyspace_name')
        )