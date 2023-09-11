from aws_cdk import pipelines as _pipelines
from aws_cdk import aws_codebuild as _codebuild
from aws_cdk import aws_iam as _iam
from aws_cdk import aws_ecr as _ecr
from aws_cdk import aws_ssm as _ssm
import aws_cdk.aws_secretsmanager as secrets
from aws_cdk import Stage, CfnOutput, Stack
from constructs import Construct

import uuid

from .lambda_stack import LambdaStack
from .BuildSpec import buildspec as buildContainerBuildSpec

image_tag=f'latest-{str(uuid.uuid4()).split("-")[-1]}'


class ApplicationStageLambda1(Stage):
  def __init__(self, scope:Construct, id: str, config, **kwargs):
    super().__init__(scope, id, **kwargs)

    LambdaStack(self, 'Demo-Lambda1', image_tag, config)

class ApplicationStageLambda2(Stage):
  def __init__(self, scope:Construct, id: str, config, **kwargs):
    super().__init__(scope, id, **kwargs)

    LambdaStack(self, 'Demo-Lambda2', image_tag, config)

class PipelineStack(Stack):

    def __init__(self, scope: Construct, id: str, config, **kwargs):
        super().__init__(scope, id, **kwargs)

        ecr_repo = _ecr.Repository(self, "lambda_container_pipeline")

        ecr_output_name = CfnOutput(self, 'ecr_repo_name', 
                value=ecr_repo.repository_name,
                export_name="ecr-repo-name")

        ecr_output_uri = CfnOutput(self, 'ecr_repo_uri', 
                value=ecr_repo.repository_uri,
                export_name="ecr-repo-uri")

        github_repo='tobigs/aws-cdk-pipelines-demo'

        secret_value = secrets.Secret.from_secret_name_v2(
            self,
            id='github-token',
            secret_name="github-token"
        ).secret_value
        git_hub_commit = _pipelines.CodePipelineSource.git_hub(
                    github_repo,
                    "main",
                    authentication=secret_value

        )

        pipeline = _pipelines.CodePipeline(self, "Container_Pipeline",
            synth=_pipelines.ShellStep("Synth",
                input=git_hub_commit,
                env={"env": config.env},
                commands=["npm install -g aws-cdk && pip install -r requirements.txt", 
                            "cdk synth",
                            "pytest unittests"]
                )
        )

        build_spec = _codebuild.BuildSpec.from_object(buildContainerBuildSpec)

        buildContainerProject = _pipelines.CodeBuildStep("ContainerBuild",
            build_environment = _codebuild.BuildEnvironment(
                                build_image=_codebuild.LinuxBuildImage.STANDARD_4_0,
                                privileged=True
                                ),
            input = git_hub_commit,
            partial_build_spec=build_spec,
            commands=[],
            env={
                "IMAGE_TAG": image_tag,
                "AWS_ACCOUNT_ID": self.account,
                "IMAGE_REPO_NAME": ecr_repo.repository_uri     
            }
        )
        
        lambda_function1 = ApplicationStageLambda1(self, 'Container-CDK-Pipeline-Lambda-Stage1', config)
        lambda_function_stage1 = pipeline.add_stage(lambda_function1, pre=[buildContainerProject])

        #lambda_function2 = ApplicationStageLambda2(self, 'Container-CDK-Pipeline-Lambda-Stage2', config)
        #lambda_function_stage2 = pipeline.add_stage(lambda_function2, pre=[buildContainerProject])


        pipeline.build_pipeline()

        ecr_repo_actions = ["ecr:PutImage", 
                            "ecr:BatchCheckLayerAvailability", 
                            "ecr:CompleteLayerUpload",
                            "ecr:InitiateLayerUpload",
                            "ecr:UploadLayerPart"]

        for perm in ecr_repo_actions:
            ecr_repo.grant(buildContainerProject, perm)

        _iam.Grant.add_to_principal(
            actions=["ecr:GetAuthorizationToken"],
            resource_arns=["*"],
            grantee=buildContainerProject
        )

