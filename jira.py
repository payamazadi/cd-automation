import json
import os
from datetime import date

import requests

from base_config import Base


class Jira(Base):
    def __init__(self):
        super(Jira, self).__init__()
        self.base_url = 'https://fng-jira.fox.com'
        self.base_url_api = '{}/rest/api/2'.format(self.base_url)
        self.username = os.environ["JIRA_USERNAME"]
        self.password = os.environ["JIRA_PASSWORD"]
        self.current_date = date.today().strftime("%Y-%m-%d")

    def generate_ticket_list(self, descriptions):
        text = ""

        for ticket, description in descriptions.items():
            text += "<{}|{}> {}".format(self.generate_ticket_link(ticket, False), ticket,
                                        description) + "\n"
            # text += "<{}/browse/{}".format(jira_base_url_api, ticket) + "|" + ticket + "> " +
            # description + "\n"

        return text

    def generate_ticket_link(self, ticket, use_api=True):
        if use_api is True:
            return "{}/browse/{}".format(self.base_url_api, ticket)
        else:
            return "{}/browse/{}".format(self.base_url, ticket)

    def send_to_jira(self, payload, ep, verb="post"):
        # I wish there was a better way to do this..
        # (I don't mean switching, I mean passing the verb as a param..)
        # Careful to keep the code the same between the two verbs here.

        verb_method = {"post": requests.post,
                       "put": requests.put,
                       "get": requests.get
                       }
        return verb_method[verb](url='{}/{}/'.format(self.base_url_api, ep),
                                 # eg https://fng-jira.fox.com/rest/api/2/issue/
                                 auth=requests.auth.HTTPBasicAuth(self.username, self.password),
                                 data=json.dumps(payload),
                                 headers={'content-type': 'application/json'}, )

    def create_deployment_ticket(self, release_info, args, bamboo):
        payload = {
            "fields": {
                "project": {
                    "key": args.project
                },
                "summary": "{} - {}".format(args.projectfriendly, args.version),
                "description":
                    "Deploy: {} ({})\nRollback: {}".format(args.version,
                                                           bamboo.format_bamboo_release(
                                                               release_info["deployment"]),
                                                           bamboo.format_bamboo_release(
                                                               release_info["rollback"])),
                "duedate": self.current_date,
                "issuetype": {
                    "name": "Code Deployment"
                },
            }
        }

        response = self.send_to_jira(payload, "issue")
        return response.json()["key"]

    def create_fix_version(self, args):
        payload = {
            "description": "{}".format(args.description),
            "name": args.version,
            "archived": "false",
            "released": "true",
            "releaseDate": self.current_date,
            "project": args.project
        }
        response = self.send_to_jira(payload, 'version')
        try:
            return response.json()["name"]
        except:
            print("Couldn't create fix version. Error:" + response.json()["errors"]["name"])

    def add_version_to_tickets(self, tickets, args):
        payload = {
            "update": {
                "fixVersions": [
                    {
                        "set":
                            [
                                {"name": args.version}
                            ]
                    }
                ]
            }
        }

        # I wasn't able to find a way to update multiple tickets with one API call.
        # So we do one call per ticket :(
        for ticket in tickets:
            response = self.send_to_jira(payload, "issue/{}".format(ticket), "put")
            # print(vars(response))
            # print("\n\n\n")

    def get_ticket_descriptions(self, tickets):
        tickets_to_descriptions = {}

        for ticket in tickets:
            print("looping through ticket ")
            print(ticket)
            response = self.send_to_jira("", "issue/{}".format(ticket), "get")
            response = response.json()
            tickets_to_descriptions[ticket] = response["fields"]["summary"]

        return tickets_to_descriptions

    def link_tickets_to_deployment(self, deployment_ticket_key, tickets):
        print("Not yet implemented")
