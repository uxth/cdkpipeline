import json

import boto3
from aws_cdk import aws_eks as eks
from aws_cdk import core
from cdk.common.stacks.eks import EksStack
from utils import yamlParser
from utils.configBuilder import Config


class ArgoCDStack(core.Stack):
    def __init__(self, scope: core.Construct, construct_id: str, eks_stack: EksStack, config: Config, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        eks.KubernetesManifest(
            self, id='repo-secret',
            cluster=eks_stack.cluster,
            manifest=self.get_manifests(config),
            overwrite=True
        )
        values = yamlParser.readYaml(path=config.getValue('argocd.valuesPath'))
        eks.HelmChart(
            self, id='argo-cd',
            cluster=eks_stack.cluster, chart='argo-cd',
            repository='https://argoproj.github.io/argo-helm',
            namespace='argo', release='argocd',
            values=values,
            wait=True
        )


    def get_manifests(self, config: Config):
        repo_secret = yamlParser.readYaml(config.getValue('argocd.repo-secrets'))
        repo_secret['stringData']['sshPrivateKey'] = self.get_ghe_ssh_key()
        manifests = [repo_secret]
        return manifests


    def get_ghe_ssh_key(self):
        try:
            client = boto3.client('secretsmanager')
            args = {'SecretId': 'ghe_ssh_key'}
            response = client.get_secret_value(**args)
            res = response['SecretString']
        except Exception as e:
            return ''
        return res
