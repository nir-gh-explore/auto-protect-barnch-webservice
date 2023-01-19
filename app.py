import json  # pylint: disable=import-error
import os  # pylint: disable=import-error
import time  # pylint: disable=import-error

import requests  # pylint: disable=import-error
from flask import Flask, request  # pylint: disable=import-error

app = Flask(__name__)


@app.route("/", methods=["POST"])
def webhook():
    # Store incoming json data from webhook
    payload = request.get_json()

    
    if payload is None:
        print("POST was not formatted in JSON")

    # Verify the repo was created
    try:
        if payload["action"] == "created":
            # Delay needed for server to be create the page, otherwise a 404 returns
            #time.sleep(1) # commenting this for now looks like some tests are working without this sleep
            # Create branch protection for the main branch of the repo
            branch_protection = {
                "required_status_checks": {"strict": True, "contexts": ["default"]},
                "enforce_admins": False,
                "required_pull_request_reviews": None,
                "restrictions": None,
            }
            user = os.environ["GH_USER"]
            cred = os.environ["GH_TOKEN"] #testing a 'mistakenly' committed secret for GHAS secret scanning testing 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

            session = requests.session()
            session.auth = (user, cred)
            subdomain="https://api.github.com/repos/"
            print("DEBUG subdomain:",subdomain)
            print("DEBUG: fullname:", payload["repository"]["full_name"],)
            
            
            response_1 = session.put(
                subdomain + payload["repository"]["full_name"] +"/branches/main/protection",
                json.dumps(branch_protection),
            )
            if response_1.status_code == 200:
                print(
                    "Branch protection created successfully. Status code: ",
                    response_1.status_code,
                )

                # Create issue in repo notifying user of branch protection
                try:
                    if payload["repository"]["has_issues"]:
                        issue = {
                            "title": "New Protection Added",
                            "body": "@"
                            + user
                            + " A new branch protection was added to the master branch.",
                        }
                        session = requests.session()
                        session.auth = (user, cred)
                        response_2 = session.post(
                            payload["repository"]["url"] + "/issues", json.dumps(issue)
                        )
                        if response_2.status_code == 201:
                            print(
                                "Issue created successfully. Status code: ",
                                response_2.status_code,
                            )
                        else:
                            print(
                                "Unable to create issue. Status code: ",
                                response_2.status_code,
                            )
                    else:
                        print(
                            "This repo has no issues so one cannot be created at this time."
                        )
                except KeyError:
                    # Request did not contain information about if the repository has issues enabled
                    pass
            else:
                print(response_1.content)
                print(
                    "Unable to create branch protection. Status code: ",
                    response_1.status_code,
                )
    except KeyError:
        # Ignore POST payload since it is not a create action
        pass

    return "OK"


if __name__ == "__main__":
    app.run()
