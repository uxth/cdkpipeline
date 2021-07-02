#!/usr/bin/env python3

# For consistency with TypeScript code, `cdk` is the preferred import name for
# the CDK's core module.  The following line also imports it as `core` for use
# with examples from the CDK Developer's Guide, which are in the process of
# being updated to use `cdk`.  You may delete this import if you don't need it.
import os

from aws_cdk import core
from cdk.common.pipeline.pipeline_stack import PipelineStack

app = core.App()
PipelineStack(
    app,
    'PipelineStack',
    env=core.Environment(
        account=os.environ['CDK_DEFAULT_ACCOUNT'],
        region=os.environ['CDK_DEFAULT_REGION']
    )
)
app.synth()
