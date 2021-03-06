import json
import os

import requests

from base_config import Base


class Slack(Base):

    def __init__(self):
        super(Slack, self).__init__()
        self.webhook = os.environ["SLACK_WEBHOOK"]

    def send_to_slack(self, ticket, descriptions, args, jira):
        payload = {
            "text": "{} deployment".format(args.projectfriendly),
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "<{}|{} - {}>\n> *Date*: {}\n>*Time*: {}"
                                "\n>*SRE*: {}\n>*TL*: {}\n>*QA*: {}\n>*Outage*: {}"
                                "\n_Tickets in this release_: \n{}".format(
                            jira.generate_ticket_link(ticket, False), args.projectfriendly,
                            args.version, self.current_date_friendly, self.current_time, args.sre,
                            args.tl, args.qa, args.outage,
                            jira.generate_ticket_list(descriptions) if bool(
                                descriptions) else "No additional tickets."
                        )
                    }
                },
                {
                    "type": "context",
                    "elements": [
                        {
                            "type": "mrkdwn",
                            "text": self.get_quote()
                        }
                    ]
                },
                {
                    "type": "divider"
                }
            ]
        }

        webhook_url = self.webhook
        response = requests.post(
            webhook_url, data=json.dumps(payload),
            headers={'Content-Type': 'application/json'}
        )

    def get_quote(self):
        response = requests.get(
            'https://andruxnet-random-famous-quotes.p.rapidapi.com/?cat=famous&count=10',
            headers={
                'x-rapidapi-host': 'andruxnet-random-famous-quotes.p.rapidapi.com',
                'x-rapidapi-key': '0a25acbb82msh84e2d715aeb6c3ap12a256jsnf57ef909ee2c',
                'User-agent': 'itsstupidihavetoprovidethisgoaway'
            }
        )
        # print(vars(response))
        # exit()
        response = response.json()
        return "{} - {}. Random quote generated by " \
               "https://rapidapi.com/andruxnet/api/random-famous-quotes".format(
            response[0]["quote"],
            response[0]["author"])
