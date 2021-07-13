from aws_cdk import aws_eks as eks
from aws_cdk import core
from cdk.common.stacks.eks import EksStack
from cdk.common.stacks.rds import RdsStack

from utils import yamlParser
from utils.configBuilder import Config


class ArgoWorkflowsStack(core.Stack):
    def __init__(self, scope: core.Construct, construct_id: str, eks_stack: EksStack, rds_stack: RdsStack, config: Config, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        yaml = yamlParser.readYaml(path=config.getValue('wmp.argo-workflow.valuesPath'))
        yaml['controller']['persistence']['postgresql']['host'] = rds_stack.rds_cluster.cluster_endpoint

        manifest = yamlParser.readYaml(path=config.getValue('wmp.argo-workflow.secrets'))
        manifest['stringData']['password'] = core.SecretValue.secrets_manager('password',
            json_field='password').to_string()
        print(manifest)
        manifests = yamlParser.readManifest(paths=config.getValue('wmp.argo-workflow.manifests'))
        manifests.append(manifest)
        # install argo workflows
        eks.KubernetesManifest(
            self, id='manifest',
            cluster=eks_stack.cluster,
            manifest=manifests,
            overwrite=True
        )
        eks.HelmChart(
            self, id='wmp-argo-workflows', cluster=eks_stack.cluster, chart='argo-workflows',
            repository='https://argoproj.github.io/argo-helm',
            namespace='argo', release=config.getValue('wmp.argo-workflow.release'),
            values=yaml,
            wait=True)
