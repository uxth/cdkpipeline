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
        secret = secretmanager.Secret.from_secret_name_v2(
            self, 'rds_secret',
            secret_name=config.getValue('rds.admin_secret_name')
        )
        manifest = yamlParser.readYaml(path=config.getValue('wmp.argo-workflow.secrets'))
        json = secret.secret_value.to_json()
        manifest['stringData']['password'] = json['password']
        # manifest['stringData']['password'] = core.SecretValue.secrets_manager(
        #     secret_id=config.getValue('wmp.argo-workflow.secret_arn'),
        #     json_field='password').to_string()
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
        yaml['controller']['persistence']['postgresql']['host'] = json['host']
        # yaml['controller']['persistence']['postgresql']['host'] = core.SecretValue.secrets_manager(
        #     secret_id=config.getValue('wmp.argo-workflow.secret_arn'),
        #     json_field='host').to_string()
        helm = eks.HelmChart(
            self, id='wmp-argo-workflows', cluster=eks_stack.cluster, chart='argo-workflows',
            repository='https://argoproj.github.io/argo-helm',
            namespace='argo', release=config.getValue('wmp.argo-workflow.release'),
            values=yaml,
            wait=True
        )
