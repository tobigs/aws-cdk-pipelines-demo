from aws_cdk import core
from pipeline.lambda_stack import LambdaStack
from config.config import get_config

def test_lambda_handler():

    # GIVEN
    app = core.App()
    config = get_config(app)

    # WHEN
    LambdaStack(app, 'Stack', 'UnitTestTag', config)

    # THEN
    template = app.synth().get_stack_by_name('Stack').template
    functions = [resource for resource in template['Resources'].values()
                if resource['Type'] == 'AWS::Lambda::Function']

    assert len(functions) == 1
    assert functions[0]['Properties']['MemorySize'] == config.memory_size #1024
    assert functions[0]['Properties']['PackageType'] == 'Image'
    assert functions[0]['Properties']['Timeout'] == 30