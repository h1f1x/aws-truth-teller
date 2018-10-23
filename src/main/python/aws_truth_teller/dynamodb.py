import boto3
from datetime import datetime, timedelta
import time

from botocore.exceptions import ClientError

from aws_truth_teller.logging import Log
import aws_truth_teller.cloudformation as cf


CF_STACK_NAME = 'ddb-backup-restore-test'
TEMPLATE_FILE = 'cfn/dynamodb/restore.yaml'

log = Log()


def how_to_restore_a_cloudformation_managed_table():
    cf_stack_name = CF_STACK_NAME
    log.info('deploying stack: {} ...'.format(cf_stack_name))
    deploy_cloudformation(cf_stack_name)
    table_name = cf.get_stack_output(cf_stack_name)['TableName']
    attributes = get_table_attributes(table_name)
    log.info('backing up table ...')
    backup_arn = backup(table_name)

    log.info('deleting original table ...')
    delete(table_name)
    log.info('restoring table ...')
    restore(table_name, backup_arn)
    log.info('comparing attributes of restored table ....')
    restored_attributes = get_table_attributes(table_name)
    print_attributes_diff(attributes, restored_attributes)
    log.info('now redeploying cloudformation ...')
    deploy_cloudformation(cf_stack_name)

    log.info('comparing attributes of restored table ....')
    restored_attributes = get_table_attributes(table_name)
    print_attributes_diff(attributes, restored_attributes)


def print_attributes_diff(old, new):
    diff = compare_attributes(old, new)
    for d in diff:
        print('!! difference in: {}'.format(d[0]))
        print('-> {}'.format(d[1][0]))
        print('+> {}'.format(d[1][1]))
    return diff


def cleanup():
    log.info('deleting stack: {} ...'.format(CF_STACK_NAME))
    delete_cloudformation_stack(CF_STACK_NAME)


def deploy_cloudformation(name):
    with open(TEMPLATE_FILE, 'r') as template:
        template_body = template.read()
    if cf.cf_stack_exists(name):
        log.info('stack exists - updating stack ...')
        update_stack(name, template_body)
    else:
        log.info('creating stack ...')
        create_stack(name, template_body)


def delete_cloudformation_stack(name):
    if cf.cf_stack_exists(name):
        log.info('deleting stack ...')
        cf.delete_stack(name)


def get_table_attributes(name):
    client = boto3.client('dynamodb')
    response = client.describe_table(TableName=name)
    return response['Table']


def create_stack(name, template_body):
    client = boto3.client('cloudformation')
    response = client.create_stack(
        StackName=name,
        TemplateBody=template_body,
        ResourceTypes=[
            'AWS::*',
        ],
        OnFailure='DELETE',
        Tags=[
            {
                'Key': 'usecase',
                'Value': 'test'
            },
        ]
    )
    cf.wait_for_completion(name)
    return response['StackId']


def update_stack(name, template_body):
    client = boto3.client('cloudformation')
    try:
        response = client.update_stack(
            StackName=name,
            TemplateBody=template_body,
            ResourceTypes=[
                'AWS::*',
            ],
            Parameters=[{
                'ParameterKey': 'Tag',
                'ParameterValue': str(datetime.now())
            }]
        )
    except ClientError as e:
        if cf.is_boto_no_update_required_exception(e):
            log.info("Stack {0} does not need an update".format(name))
            return

    cf.wait_for_completion(name)
    return response['StackId']


def backup(table_name):
    client = boto3.client('dynamodb')
    name = '{}-backup'.format(table_name)
    response = client.create_backup(TableName=table_name,
                                    BackupName=name)
    arn = response['BackupDetails']['BackupArn']
    wait_for_completion_of_backup(arn)
    return arn


def wait_for_completion_of_backup(backup_arn):
    client = boto3.client('dynamodb')
    start = datetime.now()
    timeout = 300
    while datetime.now() < (start + timedelta(seconds=int(timeout))):
        response = client.describe_backup(BackupArn=backup_arn)
        if response['BackupDescription']['BackupDetails']['BackupStatus'] == 'AVAILABLE':
            return True
        time.sleep(10)
    log.warn('Timeout while waiting for completion of backup.')
    return False


def restore(original_table_name, backup_arn):
    client = boto3.client('dynamodb')
    client.restore_table_from_backup(
        TargetTableName=original_table_name, BackupArn=backup_arn)
    wait_for_completion_of_restore(original_table_name)
    return original_table_name


def delete(table_name):
    client = boto3.client('dynamodb')
    client.delete_table(TableName=table_name)
    waiter = client.get_waiter('table_not_exists')
    waiter.wait(TableName=table_name)


def compare_attributes(old_table_attributes, new_table_attributes):
    # remove fields we know that they change on restore
    ignore_attributes = ('CreationDateTime', 'TableId')
    diff = get_diff_attributes(old_table_attributes, new_table_attributes)
    return [(k, diff[k]) for k in diff if k not in ignore_attributes]


def get_diff_attributes(this, other):
    diff = dict()
    diffkeys = []
    diffkeys.extend([k for k in this if k not in other or this[k] != other[k]])
    diffkeys.extend([k for k in other if k not in this])
    for k in diffkeys:
        diff[k] = (this.get(k, 'key not found'), other.get(k, 'key not found'))
    return diff


def wait_for_completion_of_restore(table_name):
    wait_for_table_status(table_name, is_table_restoring, False)


def wait_for_completion_of_delete(table_name):
    wait_for_table_status(table_name, is_table_status_deleting, False)


def is_table_restoring(response_of_describe_table):
    attributes = response_of_describe_table['Table']
    return 'RestoreSummary' in attributes and attributes['RestoreSummary']['RestoreInProgress']


def is_table_active(response_of_describe_table):
    return response_of_describe_table['Table']['TableStatus'] == 'ACTIVE'


def is_table_status_deleting(response_of_describe_table):
    return response_of_describe_table['Table']['TableStatus'] == 'DELETING'


def wait_for_table_status(table_name, check_callback, is_check=True, timeout=2000, sleep=15):
    client = boto3.client('dynamodb')
    start = datetime.now()
    while datetime.now() < (start + timedelta(seconds=int(timeout))):
        try:
            response = client.describe_table(TableName=table_name)
        except client.exceptions.ResourceNotFoundException:
            return
        try:  # TODO: Remove try catch block
            if check_callback(response) == is_check:
                return True
        except Exception as e:
            log.debug(response)
            print(e)
            return
        time.sleep(sleep)
    log.warn('Timeout while waiting for desired status of table.')
    return False


if __name__ == '__main__':
    print(update_stack(CF_STACK_NAME))
