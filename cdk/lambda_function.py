# This construct show cases the following:
# - automatic usage of AWS REGION in lamdba functions
# - grant secretsmanager access to lambda function

from os import path

from aws_cdk import CfnOutput, aws_lambda as lambda_

from constructs import Construct


class PythonLambdaFunction(Construct):
    def __init__(self, scope: Construct, construct_id: str) -> None:
        super().__init__(scope, construct_id)

        __dirname = path.dirname(path.abspath(__file__))

        # Create a lambda function
        self.fn = lambda_.Function(
            self,
            "PythonLambdaFunction",
            runtime=lambda_.Runtime.PYTHON_3_9,
            handler="simple.handler",
            code=lambda_.Code.from_asset(path.join(__dirname, "lambda/runtime")),
            architecture=lambda_.Architecture.ARM_64,
            environment={},
        )
