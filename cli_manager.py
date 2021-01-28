import argparse
import json
from collections import namedtuple

from base_config import Base


class CLI(Base):

    def __init__(self):
        super(CLI, self).__init__()
        self.args = self.load_args()

    def cli_args(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('--version', help='The name of the fix version you want to create')
        parser.add_argument('--createdeployticket', help='Pass 1 to create the deploy ticket')
        parser.add_argument('--deployticket',
                            help='Pass jira.py ticket key to deployment ticket eg NGPYS-xxxx. When passed, will not create deploy ticket even if --createdeployticket is passed. Will allow you to use --sendtoslack without --createdeployticket')
        parser.add_argument('--updatetickets',
                            help='Must pass --version. Attempt to add fix version to tickets. If --createdeployticket, attempt to link code tickets to deploy ticket. Will use tickets from --tickets if passed, otherwise, will try to infer tickets by comparing deployment of --stagingenv and --productionenv.')
        parser.add_argument('--sendtoslack',
                            help='When passed, will generate slack notification messsage which will send to webhook url configured in this file/env. Must also pass --createdeployticket')
        parser.add_argument('--user',
                            help='The JIRA username of the user initiating this script and owning the deployment')
        parser.add_argument('--release',
                            help='URL of the release being deployed. If provided, and --deploy is also, will deploy this version, instead of what\'s on staging')
        parser.add_argument('--rollback', help='Name of the version to be rolled back to')
        parser.add_argument('--project',
                            help='Short key of the project the ticket is to be made in, e.g. NGPYS or NGPAPI')
        parser.add_argument('--tickets',
                            help='Comma separated list of tickets, e.g. "NGPYS-xxxx,NGPYS-yyyy". If provided, will not auto determine tickets')
        parser.add_argument('--stagingenv',
                            help='ID of staging deployment environment, from release of which will be deployed if --deploy is passed')
        parser.add_argument('--productionenv',
                            help='ID of production deployment environment, to which release will be deployed if --deploy is passed')
        parser.add_argument('--deploy',
                            help='When provided, will release the value of --release to prod. If no --release, will take the release on staging and deploy it to production.')
        parser.add_argument('--projectfriendly',
                            help='Friendly name of the project, e.g. Your Shot')
        parser.add_argument('--sre', help='Slack handle for SRE')
        parser.add_argument('--tl', help='Slack handle for TL')
        parser.add_argument('--qa', help='Slack handle for QAL')
        parser.add_argument('--outage', help='Outage message')
        parser.add_argument('--description', help="Description for the newly created fix version")
        return vars(parser.parse_args())

    def merge_arguments(self, dict1, dict2):
        # this method ensure that dict2 dictionary
        # will not replace truty values from the dict1 (deployrc in exec)
        res = {k: v for team in (dict1, dict2)
               for k, v in team.items()
               if v is not None or k not in dict1.keys()}
        return res

    def load_args(self):
        try:
            with open(".deployrc", 'r') as f:
                return json.loads(json.dumps(self.merge_arguments(json.load(f), self.cli_args())),
                                  object_hook=lambda d: namedtuple('config_data', d.keys())(
                                      *d.values()))
        except Exception:
            print('\nNo config File')
            return self.cli_args()

    def validate_parser_args(self):
        if self.args.deploy != None:
            if self.args.productionenv is None:
                exit("You passed --deploy, so you must pass --productionenv.")
            if self.args.stagingenv is None and self.args.release is None:
                exit(
                    "You passed --deploy, but you did not pass either --stagingenv or --release. "
                    "How do I know what to deploy!?")
        if self.args.updatetickets != None and self.args.version is None:
            exit(
                "You asked to updaet tickets (e.g. add fix version), but did not pass "
                "in --version.")
        if self.args.sendtoslack != None and self.args.createdeployticket is None and \
                self.args.deployticket is None:
            exit(
                "You asked to send to slack, but you did not ask to create a ticket and did not "
                "pass one in with args.deployticket. Can't send a slack without a ticket!")
