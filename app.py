import os
from typing import Final

from aws_cdk import App, Environment, Stack, Tags

from cdk.stack import DemoStack

REGION: Final[str] = os.environ["CDK_DEFAULT_REGION"]
ACCOUNT: Final[str] = os.environ["CDK_DEFAULT_ACCOUNT"]
ENVIRONMENT: Final[Environment] = Environment(account=ACCOUNT, region=REGION)

app = App()

Tags.of(app).add("owner", os.environ.get("USER", "unknown"))

stack = DemoStack(app, id="aws-truth-teller", env=ENVIRONMENT)

app.synth()
