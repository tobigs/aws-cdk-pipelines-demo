from collections import namedtuple
import json
import os

# Set environment variables


def get_config(app):
    context = app.node.try_get_context("context")
    if not context:
        with open("cdk.json") as config:
            cdk_context = json.load(config)
            context = cdk_context['context']

    env = context["env"]
    if not env:
        env = os.getenv('env')

    
    Config = namedtuple("Config", "env memory_size")
    config = Config(env, context[env]["memory_size"])

    return config
    