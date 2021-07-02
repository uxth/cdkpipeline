from aws_cdk import aws_eks as eks
from aws_cdk import core
from cdk.common.stacks.eks import EksStack

from utils import yamlParser
from utils.configBuilder import Config


class ArgoWorkflowsStack(core.Stack):
    def __init__(self, scope: core.Construct, construct_id: str, eks_stack: EksStack, config: Config, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        # install argo workflows
        eks.KubernetesManifest(
            self, id='manifest',
            cluster=eks_stack.cluster,
            manifest=yamlParser.readManifest(paths=config.getValue('wmp.argo-workflow.manifests')),
            overwrite=True
        )

        eks.HelmChart(
            self, id='wmp-argo-workflows', cluster=eks_stack.cluster, chart='argo-workflows',
            repository='https://argoproj.github.io/argo-helm',
            namespace='argo', release=config.getValue('wmp.argo-workflow.release'),
            values=yamlParser.readYaml(path=config.getValue('wmp.argo-workflow.valuesPath')),
            wait=True)
