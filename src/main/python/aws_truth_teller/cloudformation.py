import boto3
from datetime import datetime, timedelta
import time

from botocore.exceptions import ClientError

from .logging import Log

log = Log()


def get_stack_output(stack_name):
    client = boto3.client('cloudformation')
    response = client.describe_stacks(StackName=stack_name)
    log.debug(response)
    return {e['OutputKey']: e['OutputValue'] for e in response["Stacks"][0]["Outputs"]}


def delete_stack(name):
    client = boto3.client('cloudformation')
    client.delete_stack(StackName=name)
    wait_for_completion_of_delete_stack(name)


def is_boto_no_update_required_exception(exception):
    if isinstance(exception, ClientError):
        if exception.response["Error"]["Message"] == "No updates are to be performed.":
            return True
        else:
            return False
    else:
        return False


def wait_for_completion(stack_name):
    wait_for_cloudformation(stack_name, is_cf_complete_or_failed)


def wait_for_completion_of_delete_stack(stack_name):
    client = boto3.client('cloudformation')
    waiter = client.get_waiter('stack_delete_complete')
    waiter.wait(StackName=stack_name)


def wait_for_cloudformation(stack_name, check_callback, timeout=600):
    client = boto3.client('cloudformation')
    start = datetime.now()
    while datetime.now() < (start + timedelta(seconds=int(timeout))):
        response = client.describe_stacks(StackName=stack_name)
        describe_stack_response = response["Stacks"][0]
        if check_callback(describe_stack_response):
            return True
        time.sleep(10)
    log.warn('Timeout while waiting for completion of the cf stack.')
    return False


def is_cf_complete_or_failed(response_of_describe_stack):
    status = response_of_describe_stack['StackStatus']
    log.debug(status)
    return status.endswith('_COMPLETE') or status.endswith('_FAILED')


def is_cf_deleted(response_of_describe_stack):
    status = response_of_describe_stack['StackStatus']
    log.debug(status)
    return status == 'DELETE_COMPLETE' or status == 'DELETE_FAILED'


def cf_stack_exists(name):
    client = boto3.client('cloudformation')
    for stacks in client.get_paginator('list_stacks').paginate():
        for stack in stacks['StackSummaries']:
            if stack['StackName'] == name and stack['StackStatus'] != 'DELETE_COMPLETE':
                return True
    return False
