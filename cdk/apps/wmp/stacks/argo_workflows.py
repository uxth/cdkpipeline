from aws_cdk import aws_eks as eks
from aws_cdk import core
from cdk.common.stacks.eks import EksStack
from cdk.common.stacks.rds import RdsStack

from utils import yamlParser
from utils.configBuilder import Config


class ArgoWorkflowsStack(core.Stack):
    def __init__(self, scope: core.Construct, construct_id: str, eks_stack: EksStack, rds_stack: RdsStack, config: Config, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        manifest = yamlParser.readYaml(path=config.getValue('wmp.argo-workflow.secrets'))

        manifest['stringData']['password'] = core.SecretValue.secrets_manager(
            secret_id=rds_stack.format_arn(
                service='secretmanager',
                resource='secret',
                sep=':',
                resource_name=config.getValue('rds.admin_secret_name'),
                account=config.getValue('common.AWSAccountID'),
                region=config.getValue('common.AWSProfileRegion')
            ),
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

        yaml = yamlParser.readYaml(path=config.getValue('wmp.argo-workflow.valuesPath'))
        yaml['controller']['persistence']['postgresql']['host'] = rds_stack.rds_cluster.cluster_endpoint
        helm = eks.HelmChart(
            self, id='wmp-argo-workflows', cluster=eks_stack.cluster, chart='argo-workflows',
            repository='https://argoproj.github.io/argo-helm',
            namespace='argo', release=config.getValue('wmp.argo-workflow.release'),
            values=yaml,
            wait=True
        )
