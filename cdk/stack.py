from typing import Optional
from aws_cdk import CfnOutput, Environment, Stack
from constructs import Construct
from .lambda_function import PythonLambdaFunction


class DemoStack(Stack):
    def __init__(
        self,
        scope: Construct,
        id: str,
        env: Optional[Environment] = None,
    ) -> None:
        super().__init__(scope, id, env=env)

        lambda_function = PythonLambdaFunction(self, "LambdaFunction")
        CfnOutput(
            self,
            "lambda",
            value=lambda_function.fn.function_name,
            description="lambda function name",
        )
