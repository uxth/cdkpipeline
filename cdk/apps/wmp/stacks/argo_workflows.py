import json

import boto3
from aws_cdk import aws_eks as eks
from aws_cdk import core
from cdk.common.stacks.eks import EksStack
from cdk.common.stacks.rds import RdsStack
from aws_cdk import aws_secretsmanager as secretmanager
from utils import yamlParser
from utils.configBuilder import Config


class ArgoWorkflowsStack(core.Stack):
    def __init__(self, scope: core.Construct, construct_id: str, eks_stack: EksStack, rds_stack: RdsStack,
                 config: Config, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        client = boto3.client('secretsmanager')
        args = {'SecretId': config.getValue('rds.admin_secret_name')}
        response = client.get_secret_value(**args)
        json_data = json.loads(response['SecretString'])
        password = json_data['password']
        host = json_data['host']
        username = json_data['username']
        manifest = yamlParser.readYaml(path=config.getValue('wmp.argo-workflow.secrets'))

        manifest['stringData']['password'] = password
        manifest['stringData']['username'] = username
        manifests = yamlParser.readManifest(paths=config.getValue('wmp.argo-workflow.manifests'))
        manifests.append(manifest)
        # install argo workflows
        eks.KubernetesManifest(
            self, id='manifest',
            cluster=eks_stack.cluster,
            manifest=manifests,
            overwrite=True
        )

        yaml = yamlParser.readYaml(path=config.getValue('wmp.argo-workflow.valuesPath'))
        yaml['controller']['persistence']['postgresql']['host'] = host
        helm = eks.HelmChart(
            self, id='wmp-argo-workflows', cluster=eks_stack.cluster, chart='argo-workflows',
            repository='https://argoproj.github.io/argo-helm',
            namespace='argo', release=config.getValue('wmp.argo-workflow.release'),
            values=yaml,
            wait=True
        )
