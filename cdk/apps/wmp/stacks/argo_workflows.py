from aws_cdk import aws_eks as eks
from aws_cdk import core
from cdk.common.stacks.eks import EksStack
from cdk.common.stacks.rds import RdsStack
from aws_cdk import aws_secretsmanager as secretmanager
from utils import yamlParser
from utils.configBuilder import Config


class ArgoWorkflowsStack(core.Stack):
    def __init__(self, scope: core.Construct, construct_id: str, eks_stack: EksStack, config: Config, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        secret_arn = secretmanager.Secret.from_secret_name(
            self, 'rds_secret',
            secret_name=config.getValue('rds.admin_secret_name')
        ).secret_arn
        manifest = yamlParser.readYaml(path=config.getValue('wmp.argo-workflow.secrets'))
        manifest['stringData']['password'] = core.SecretValue.secrets_manager(
            secret_id=secret_arn,
            # secret_id='arn:aws:secretsmanager:us-west-2:711208530951:secret:map_rds_admin-1prLs8',
            json_field='password').to_string()

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
        yaml['controller']['persistence']['postgresql']['host'] = core.SecretValue.secrets_manager(
            secret_id=secret_arn,
            json_field='host').to_string()
        helm = eks.HelmChart(
            self, id='wmp-argo-workflows', cluster=eks_stack.cluster, chart='argo-workflows',
            repository='https://argoproj.github.io/argo-helm',
            namespace='argo', release=config.getValue('wmp.argo-workflow.release'),
            values=yaml,
            wait=True
        )