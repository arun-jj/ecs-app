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

    stack = cfn.CfnStack('default')
    # vpc template
    vpc_stackname = 'my-network'
    vpc = open(os.path.join('../CFN', 'vpc.yaml')).read()

    create_or_update_stack(stack, vpc_stackname, vpc)

    # create ecs cluster
    ecs_stackname = 'ecs-cluster'
    ecs_tmpl = open(os.path.join('../CFN', 'ecs.yaml')).read()
    vpc_outpts = stack.stack_output(vpc_stackname)
    ecs_params = [
        {'ParameterKey': 'ClusterName', 'ParameterValue': 'backend-ecs'},
        {'ParameterKey': 'VpcId', 'ParameterValue': vpc_outpts['VPCId']},
        {'ParameterKey': 'Subnets',
         'ParameterValue': '{}, {}'.format(vpc_outpts['Subnet1Id'], vpc_outpts['Subnet2Id'])},
        {'ParameterKey': 'MinCapacity', 'ParameterValue': '0'},
        {'ParameterKey': 'MaxCapacity', 'ParameterValue': '2'},
        {'ParameterKey': 'DesiredCapacity', 'ParameterValue': '1'},
        {'ParameterKey': 'InstanceType', 'ParameterValue': 't2.small'},
        {'ParameterKey': 'KeyName', 'ParameterValue': 'ecs_key'}
    ]

    create_or_update_stack(stack, ecs_stackname, ecs_tmpl, ecs_params, 'CAPABILITY_IAM')

    # application deployment
    app_stackname = 'flaskapp-rules'
    app_tmpl = open(os.path.join('../CFN', 'app.yaml')).read()
    ecs_outputs = stack.stack_output(ecs_stackname)
    docker_url = 'dkr.ecr.us-west-2.amazonaws.com/flaskapp:latest'
    app_params = [
        {'ParameterKey': 'ECSClusterName', 'ParameterValue': ecs_outputs['ECSCluster']},
        {'ParameterKey': 'ECSTaskName', 'ParameterValue': 'flaskapp'},
        {'ParameterKey': 'DockerImage', 'ParameterValue': docker_url}
    ]

    create_or_update_stack(stack, app_stackname, app_tmpl, app_params, 'CAPABILITY_IAM')
