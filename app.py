#!/usr/bin/env python3

from aws_cdk import core

#from pipeline.ecr_repo import ECRRepoDeploy
from pipeline.pipeline_stack import PipelineStack
from config.config import get_config

app = core.App()

config = get_config(app)
print(config)

PipelineStack(app, "cdk-pipelines-demo", config)

app.synth()
