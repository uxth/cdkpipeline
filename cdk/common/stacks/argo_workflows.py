import json

import boto3
from aws_cdk import aws_eks as eks
from aws_cdk import core
from cdk.common.stacks.eks import EksStack
from utils import yamlParser
from utils.configBuilder import Config


class ArgoWorkflowsStack(core.Stack):
    def __init__(self, scope: core.Construct, construct_id: str, eks_stack: EksStack,
                 config: Config, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        username, password, host = self.get_secret(config)

        # install argo workflows
        eks.KubernetesManifest(
            self, id='argo-workflow-manifest',
            cluster=eks_stack.cluster,
            manifest=self.get_manifests(config, username=username, password=password, host=host),
            overwrite=True
        )

    def get_secret(self, config: Config):
        try:
            client = boto3.client('secretsmanager')
            args = {'SecretId': config.getValue('rds.admin_secret_name')}
            response = client.get_secret_value(**args)
            json_data = json.loads(response['SecretString'])
            password = json_data['password']
            host = json_data['host']
            username = json_data['username']
        except Exception as e:
            return 'username', 'password', 'host'

        return username, password, host

    def get_manifests(self, config: Config, username: str, password: str, host: str):
        manifest = yamlParser.readYaml(path=config.getValue('argo-workflow.secrets'))
        manifest['stringData']['password'] = password
        manifest['stringData']['username'] = username
        manifest['stringData']['host'] = host

        postgres = yamlParser.readYaml(path=config.getValue('argo-workflow.postgres_service'))
        postgres['spec']['externalName'] = host
        return [manifest, postgres]
