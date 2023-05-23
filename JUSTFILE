all: build deploy test

init:
    cdk bootstrap

@build:
    cdk synth

@deploy:
   cdk deploy --require-approval never

test:
    #!/usr/bin/env bash
    function_name=$(aws cloudformation describe-stacks --query 'Stacks[?StackName==`aws-truth-teller`][].Outputs[?OutputKey==`lambda`].OutputValue' --output text)
    echo "[*] Invoking $function_name ..."
    aws lambda invoke --function-name $function_name lambda.out --log-type Tail --query 'LogResult' --output text |  base64 -d