import boto3
import botocore
import logging

session = boto3.session.Session(profile_name='local')

client = session.client('cloudformation')


def create_cfn_stack(stack, stackname, template, cfnclient, parameters=None, iam=None):
    """
    create/update cloudformation stack
    """
    logging.info("Received request to create/update stack {!r} with parameters {!r}".format(stackname, str(parameters)))
    try:
        cfnclient.describe_stacks(StackName=stackname)
        logging.info("{!r} stack already exists. Checking if update is needed...".format(stackname))

        updateneed = stack.updatestack(stackname=stackname, template=template,
                                       parameters=parameters, cfnclient=cfnclient, iam=iam)
        if updateneed:
            stack.stackstatuswaiter(stackname=stackname,
                                    status="stack_update_complete",
                                    cfnclient=cfnclient)
            logging.info("Stack {!r} update completed.".format(stackname))
        else:
            logging.info("Stack {!r} needs no update.".format(stackname))
    except botocore.exceptions.ClientError as err:
        logging.info("Creating stack {!r} now...".format(stackname))
        stack.createstack(stackname=stackname, template=template,
                          parameters=parameters, cfnclient=cfnclient, iam=iam)
        stack.stackstatuswaiter(stackname=stackname,
                                status="stack_create_complete",
                                cfnclient=cfnclient)
        logging.info("Stack {!r} creation completed.".format(stackname))
