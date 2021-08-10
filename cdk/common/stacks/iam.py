from aws_cdk import core
from aws_cdk import aws_iam as iam
from aws_cdk import aws_eks as eks
from cdk.common.stacks.eks import EksStack
from utils import yamlParser
from utils.configBuilder import Config
from utils.randGenerator import stringGenerator


class IamStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, config: Config, eks_stack: EksStack, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        username = 'map-app-user'
        password = stringGenerator(24)
        iam_user = iam.User(
            self, id="map-app-user",
            user_name=username,
            password=core.SecretValue.plain_text(password)
        )
        policy = iam.Policy(
            self, id='map-app-policy',
            policy_name='S3FullAccessPolicy',
            statements=[
                iam.PolicyStatement(
                    sid='S3FullAccess',
                    effect=iam.Effect.ALLOW,
                    actions=['s3:*'],
                    resources=['*']
                ),
                iam.PolicyStatement(
                    sid='SecretManagerFullAccess',
                    effect=iam.Effect.ALLOW,
                    actions=['secretsmanager:*'],
                    resources=['*']
                ),
                iam.PolicyStatement(
                    sid='RDSFullAccess',
                    effect=iam.Effect.ALLOW,
                    actions=['rds:*'],
                    resources=['*']
                )
            ],
            users=[iam_user]
        )
        access_key = iam.CfnAccessKey(
            self, 'map-apps-user',
            user_name=iam_user.user_name
        )
        access_key_id = access_key.ref
        secret_access_key = access_key.attr_secret_access_key

        manifests = [self.get_manifest(config, namespace=namespace, username=username, password=password,
            access_key_id=access_key_id, secret_access_key=secret_access_key) for
                     namespace in config.getValue('app.namespaces')]

        eks.KubernetesManifest(
            self, id='manifest',
            cluster=eks_stack.cluster,
            manifest=manifests,
            overwrite=True
        )

    def get_manifest(self, config: Config, namespace: str, username: str, password: str, access_key_id: str,
                     secret_access_key: str):
        manifest = yamlParser.readYaml(path=config.getValue('app.secret_manifest'))
        manifest['metadata']['namespace'] = namespace
        manifest['stringData']['IAM_USERNAME'] = username
        manifest['stringData']['IAM_PASSWORD'] = password
        manifest['stringData']['AWS_ACCESS_KEY_ID'] = access_key_id
        manifest['stringData']['AWS_SECRET_ACCESS_KEY'] = secret_access_key
        return manifest
