from aws_cdk import core
from aws_cdk import aws_cassandra as cassandra

from utils.configBuilder import Config


class CassandraStack(core.Stack):
    def __init__(self, scope: core.Construct, construct_id: str, config: Config, **kwargs) -> \
            None:
        super().__init__(scope, construct_id, **kwargs)
        keySpace = cassandra.CfnKeyspace(
            self,
            'cassandra_keyspace',
            keyspace_name=config.getValue('cassandra.keyspace_name')
        )
        # Data types
        # https://docs.aws.amazon.com/keyspaces/latest/devguide/cql.elements.html?cmpid=docs_keyspaces_hp-table#cql.data-types
        cassandra.CfnTable(
            self,
            'cassandra_table',
            keyspace_name=keySpace.keyspace_name,
            table_name=config.getValue('cassandra.table_name'),
            partition_key_columns=[cassandra.CfnTable.ColumnProperty(column_name='test', column_type='TEXT')]
        )