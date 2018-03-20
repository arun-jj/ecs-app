import logging
from cfn.cfn import StackException, CfnStack

logging.getLogger(__name__).addHandler(logging.NullHandler())
