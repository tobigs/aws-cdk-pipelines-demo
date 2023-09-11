from aws_cdk import core
from aws_cdk.assertions import Template
from pipeline.lambda_stack import LambdaStack
from config.config import get_config

def test_lambda_handler():

    # GIVEN
    app = core.App()
    config = get_config(app)

    # WHEN
    lambda_stack = LambdaStack(app, 'Stack', 'UnitTestTag', config)

    # THEN
    template = Template.from_stack(lambda_stack)
    template.resource_count_is("AWS::Lambda::Function", 1)

    template.has_resource_properties(
    "AWS::Lambda::Function",
    {
        "MemorySize": config.memory_size,
        "PackageType": "Image",
    },
    )