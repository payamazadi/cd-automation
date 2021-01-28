import json
import os

import requests

from base_config import Base


class Bamboo(Base):
    def __init__(self):
        super(Bamboo, self).__init__()
        self.base_url = 'https://bamboo.ngeo.com'
        self.base_url_api = '{}/rest/api/latest'.format(self.base_url)
        self.username = os.environ["BAMBOO_USERNAME"]
        self.password = os.environ["BAMBOO_PASSWORD"]
        print(self.username)

    def deploy(self, args):
        release_id = ""
        releases = {}

        if args.release is None:
            stage = self.bamboo_get_deployed_info(args.stagingenv)
            release_id = stage["version"]
        else:
            release = args.release
            release_id = release.split("=")[1]

        prod = self.bamboo_get_deployed_info(args.productionenv)
        releases["rollback"] = prod["version"]
        releases["deployment"] = release_id

        print("Will release " + str(release_id) + " to env " + args.productionenv + ".")
        response = \
            self.send_to_bamboo("", "queue/deployment/?environmentId={}&versionId={}"
                                .format(args.productionenv, release_id),
                                "post")
        print(response.json())
        print("Deployed " + str(release_id) + " to prod!")
        return releases

    def get_tickets(self, args):
        if args.tickets is not None:
            tickets_set = set()
            for ticket in args.tickets.split(","):
                tickets_set.add(ticket)
            return tickets_set
        else:
            try:
                tickets = self.bamboo_get_tickets_diff(args)
                return tickets
            except:
                print("Tickets were not passed with --tickets. Tried to infer tickets by "
                      "comparing --stagingenv and --productionenv but failed. All operations "
                      "for associating tickets will be skipped.")

    def send_to_bamboo(self, payload, ep, verb="get"):
        verb_method = {
            "post": requests.post,
            "get": requests.get
        }

        return verb_method[verb]('{}/{}'.format(self.base_url_api, ep),
                                 # https://bamboo.ngeo.com/rest/api/latest/deploy/environment/82640897/results
                                 auth=requests.auth.HTTPBasicAuth(self.username, self.password),
                                 data=json.dumps(payload),
                                 headers={'content-type': 'application/json',
                                          'accept': 'application/json'
                                          }
                                 )

    def bamboo_get_deployed_info(self, environment_id):
        response = self.send_to_bamboo("", "deploy/environment/{}/results".format(environment_id))
        results = response.json()
        latest_deploy = results["results"][0]
        latest_deploy_build_key = latest_deploy["deploymentVersion"]["items"][0]["planResultKey"][
            "key"]
        latest_deploy_branch_name = latest_deploy["deploymentVersion"]["planBranchName"]
        return {"branch": latest_deploy_branch_name, "key": latest_deploy_build_key,
                "version": latest_deploy["deploymentVersion"]["id"]}

    def bamboo_get_tickets_diff(self, args):
        # stage
        stage = self.bamboo_get_deployed_info(args.stagingenv)
        prod = self.bamboo_get_deployed_info(args.productionenv)
        print(stage)
        print(prod)
        ticket_set = set()
        if stage["branch"] != prod["branch"]:
            print(
                "Since you did not pass tickets, trying to determine tickets by comparing stage "
                "and prod. But cannot compare - it appears the branches deployed to them are "
                "different. Must be the same in order to compare.")
            exit()

        start_key = prod["key"]
        end_key = stage["key"]
        start_key_num = int(start_key.split("-")[2])
        end_key_num = int(end_key.split("-")[2])
        key_root_split = start_key.split("-")
        key_root = "{}-{}".format(key_root_split[0], key_root_split[1])

        # the +1 is buggy here when prod is one step away from staging.. need more diagnosis
        for num in range(start_key_num + 1, end_key_num):
            build_info = self.send_to_bamboo("",
                                             "result/{}-{}?expand=jiraIssues".format(key_root,
                                                                                     num)).json()
            all_issues = build_info["jiraIssues"]["issue"]

            for jirakey in all_issues:
                ticket_set.add(jirakey["key"])

        return ticket_set

    def format_bamboo_release(self, release_id):
        return "{}{}{}".format(self.base_url, '/deploy/viewDeploymentVersion.action?versionId=',
                               release_id)
