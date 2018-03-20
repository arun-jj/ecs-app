import boto3
import botocore
import logging


class StackException(Exception):
    pass


class CfnStack:

    def __init__(self, profile_name):
        session = boto3.session.Session(profile_name=profile_name)
        self._client = session.client('cloudformation')

    def is_stack_exist(self, stackname):
        try:
            self._client.describe_stacks(StackName=stackname)
            return True
        except botocore.exceptions.ClientError:
            logging.error('The stack {} doesn not exist'.format(stackname))
            return False

    def stack_output(self, stackname):
        try:
            response = self._client.describe_stacks(StackName=stackname)
            outputs = response['Stacks'][0]['Outputs']
            result = {}
            for output in outputs:
                result[output['OutputKey']] = output['OutputValue']
            return result
        except botocore.exceptions.ClientError:
            msg = 'The stack {} doesn not exist'.format(stackname)
            logging.error(msg)
            raise StackException(msg)

    def create_stack(self, stackname, template, parameters=None, iam=None):
        try:
            params = {
                'StackName': stackname,
                'TemplateBody': template,
                'OnFailure': 'ROLLBACK'
            }
            if parameters:
                params.update({'Parameters': parameters})
            if iam:
                if iam not in ['CAPABILITY_IAM', 'CAPABILITY_NAMED_IAM']:
                    msg = 'Invalid value {} for iam'.format(iam)
                    logging.error(msg)
                    raise StackException(msg)
                params.update({'Capabilities': [iam]})

            self._client.create_stack(**params)

            # create waiter
            waiter = self._client.get_waiter('stack_create_complete')
            waiter.wait(StackName=stackname)
        except botocore.exceptions.ClientError as err:
            msg = 'The Stack({}) creation failed: {}'.format(stackname, err)
            logging.error(msg)
            raise StackException(msg)

    def update_stack(self, stackname, template, parameters=None, iam=None):
        try:
            params = {
                'StackName': stackname,
                'TemplateBody': template
            }
            if parameters:
                params.update({'Parameters': parameters})
            if iam:
                if iam not in ['CAPABILITY_IAM', 'CAPABILITY_NAMED_IAM']:
                    msg = 'Invalid value {} for iam'.format(iam)
                    logging.error(msg)
                    raise StackException(msg)
                params.update({'Capabilities': [iam]})

            self._client.update_stack(**params)

            # create waiter
            waiter = self._client.get_waiter('stack_update_complete')
            waiter.wait(StackName=stackname)
        except botocore.exceptions.ClientError as err:
            msg = 'The Stack({}) update failed: {}'.format(stackname, err)
            logging.error(msg)
            raise StackException(msg)

    def delete_stack(self, stackname):
        try:
            self._client.delete_stack(StackName=stackname)

            waiter = self._client.get_waiter('stack_delete_complete')
            waiter.wait(StackName=stackname)
        except botocore.exceptions.ClientError as err:
            msg = 'The Stack({}) delete failed: {}'.format(stackname, err)
            logging.error(msg)
            raise StackException(msg)
