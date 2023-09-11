from aws_cdk import Stack, App, Fn, Duration, aws_lambda as _lambda, aws_ecr as _ecr
import datetime

class LambdaStack(Stack):

    def __init__(self, app: App, id: str, tag, config, **kwargs):
        super().__init__(app, id, **kwargs)

        ecr_repo_name = Fn.import_value("ecr-repo-name") 

        func = _lambda.DockerImageFunction(
            self, "LambdaContainerFunction",
            code=_lambda.DockerImageCode.from_ecr(
                _ecr.Repository.from_repository_name(self, 'lambda_container_pipeline', 
                repository_name=ecr_repo_name), tag=tag),
            memory_size=config.memory_size,
            description="Function generated on {}".format(datetime.datetime.now()),
            timeout=Duration.seconds(30),
            )



