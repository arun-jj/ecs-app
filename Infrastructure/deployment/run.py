import cfn
import logging
import os


def create_or_update_stack(stack: cfn.CfnStack, stackname, template, parameters=None, iam=None):
    """
    create/update cloudformation stack
    """
    logging.info("Received request to create/update stack {!r} with parameters {!r}".format(stackname, str(parameters)))
    try:
        is_update = stack.is_stack_exist(stackname)
        if is_update:
            stack.update_stack(stackname=stackname, template=template,
                               parameters=parameters, iam=iam)
            logging.info("Updating stack: {}".format(stackname))
        else:
            logging.info("Creating stack: {}".format(stackname))
            stack.create_stack(stackname=stackname, template=template,
                               parameters=parameters, iam=iam)
    except cfn.StackException as err:
        logging.error(str(err))


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s -  %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

    stack = cfn.CfnStack('local')
    # vpc template
    stackname = 'my-network'
    vpc = open(os.path.join('../CFN', 'vpc.yaml')).read()

    create_or_update_stack(stack, stackname, vpc)
