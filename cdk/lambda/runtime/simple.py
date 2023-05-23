import os


def handler(event, context):
    print(os.getenv("AWS_REGION"))
    return "If you reach this line, the test was successful."
