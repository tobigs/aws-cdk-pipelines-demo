#!/usr/bin/env python3

from aws_cdk import App, Aspects
from cdk_nag import AwsSolutionsChecks

#from pipeline.ecr_repo import ECRRepoDeploy
from pipeline.pipeline_stack import PipelineStack
from config.config import get_config

app = App()
# Aspects.of(app).add(AwsSolutionsChecks(verbose=True))

config = get_config(app)
print(config)

PipelineStack(app, "cdk-pipelines-demo", config)

app.synth()
