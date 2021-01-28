#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Written by Payam Azadi with help from Steve Rodriguez, August 2019, NGP Product & Tech (DTCI)

# Must add JIRA service account to the project you're trying to create stuff in,
# otherwise this will fail
# Set environment variables for bamboo, jira, slack when running this locally

# Todo
# Move tickets to Staged for release
# Link tickets to SREO ticket
# Move SREO ticke to "On Production"
# Link deployment ticket to prior deploy ticket (via fix version)
# Integrate into a Lambda, with commandline options coming from querystring/POST body
# Expose Lambda and integrate with Slack so you can deploy to prod from Slack


from bamboo import Bamboo
from cli_manager import CLI
from jira import Jira
from slack import Slack

"""
Main Routine
"""
bamboo = Bamboo()
jira = Jira()
slack = Slack()
cli = CLI()

cli.validate_parser_args()

tickets = bamboo.get_tickets(cli.args)
print("Tickets are : ")
print(tickets)

if cli.args.version is not None:
    jira.create_fix_version(cli.args)

if cli.args.updatetickets is not None:
    jira.add_version_to_tickets(tickets, cli.args)

if cli.args.deploy is not None:
    release_info = bamboo.deploy(cli.args)
else:
    release_info = {"deployment": cli.args.release,
                    "rollback": cli.args.rollback}

if cli.args.createdeployticket is not None and cli.args.deployticket is None:
    deployment_ticket_key = jira.create_deployment_ticket(release_info,
                                                          cli.args, bamboo)
else:
    deployment_ticket_key = cli.args.deployticket

if (cli.args.createdeployticket is not None or cli.args.deployticket is not None) and \
        cli.args.updatetickets is not None:
    jira.link_tickets_to_deployment(deployment_ticket_key, tickets)

if cli.args.sendtoslack is not None:
    if deployment_ticket_key == "":
        print("Cannot send to slack, failed to get deployment_ticket_key.")
    else:
        slack.send_to_slack(deployment_ticket_key, jira.get_ticket_descriptions(tickets), cli.args,
                            jira)
