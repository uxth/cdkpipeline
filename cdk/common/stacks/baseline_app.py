import json

import boto3
from aws_cdk import aws_eks as eks
from aws_cdk import core
from cdk.common.stacks.eks import EksStack
from utils import yamlParser
from utils.configBuilder import Config


class BaselineAppStack(core.Stack):
    def __init__(self, scope: core.Construct, construct_id: str, eks_stack: EksStack, config: Config, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        eks.KubernetesManifest(
            self, id='argocd_manifest',
            cluster=eks_stack.cluster,
            manifest=yamlParser.readManifest(config.getValue('argocd.manifests')),
            overwrite=True
        )