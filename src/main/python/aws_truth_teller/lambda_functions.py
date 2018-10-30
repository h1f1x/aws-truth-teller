from aws_truth_teller.logging import Log
import aws_truth_teller.cloudformation as cf

log = Log()

CF_STACK_NAME = 'att-lamdba-test'
TEMPLATE_FILE = 'cfn/lambda/logging.yaml'


def how_lambda_logs_to_cloudwatch():
    deploy_cloudformation(CF_STACK_NAME)


def deploy_cloudformation(stack_name):
    with open(TEMPLATE_FILE, 'r') as template:
        template_body = template.read()
    if cf.cf_stack_exists(stack_name):
        log.info('stack exists - updating stack ...')
        cf.update_stack(stack_name, template_body)
    else:
        log.info('creating stack ...')
        cf.create_stack(stack_name, template_body)


if __name__ == '__main__':
    deploy_cloudformation(CF_STACK_NAME)
