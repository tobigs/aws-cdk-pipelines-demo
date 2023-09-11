from collections import namedtuple

def get_config(app):
    context = app.node.try_get_context("context")
    env = app.node.try_get_context("env")

    Config = namedtuple("Config", "memory_size")
    config = Config(context[env]["memory_size"])

    return config
    