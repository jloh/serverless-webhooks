#!/usr/bin/env python3

from util import generate_config, funcs
from pushbullet import Pushbullet
import json, os

config = generate_config.return_config()

# Get our GitHub Secret used to sign requests
gh_secret = os.getenv('github_secret')

# PB Key
pb_key    = os.getenv('pushbullet_api_key')

def handler(event, context):

    # GitHub event, signature and payload
    gh_event     = event['headers']['X-GitHub-Event']
    gh_signature = event['headers'].get('X-Hub-Signature')
    gh_body      = event['body']
    gh_payload   = json.loads(gh_body)

    # If we don't have a signature abort!
    if gh_signature is None:
        response = {
            "statusCode": 403,
            "body": json.dumps({"error": "'X-Hub-Signature' was not sent"})
        }
        return response

    # No secret means we can't authenticate, abort!
    if gh_secret is None:
        response = {
            "statusCode": 500,
            "body": json.dumps({"error": "env variable 'github_secret' not set"})
        }
        return response

    # Split our signature and digest method
    digest, gh_signature = gh_signature.split('=')

    # Verify our signature and deny if it fails!
    if not funcs.verify_signature(gh_secret, gh_body, gh_signature, digest):
        response = {
            "statusCode": 403,
            "body": json.dumps({"error": "Signature mismatch"})
        }
        return response

    # Check our event is defined, otherwise we just wont do anything
    if gh_event in config['github']['events']:
        # Get our current event into a more sensible context
        event = config['github']['events'][gh_event]

        # If our event doesn't have 'always' set to true send a notification
        # Otherwise, if the sender of the event is in the ignore list don't notify
        if event['pushbullet'].get('always', False) is True or gh_payload['sender']['login'] not in config['github']['ignore']:
            pb_payload = event['pushbullet']

            title = pb_payload['title'].format(**gh_payload)
            body  = pb_payload['body'].format(**gh_payload)
            link  = pb_payload['link'].format(**gh_payload)

            # Generate our pushbullet instance
            pb = Pushbullet(pb_key)

            # Shot notification
            notification = pb.push_link(title, link, body)

            response = {
                "statusCode": 200,
                "body": json.dumps({"status": "OK", "notification": "pushed", "pb_id": notification['iden']})
            }
            return response
        else:
            response = {
                "statusCode": 200,
                "body": json.dumps({"status": "OK", "notification": "skipped", "reason": "user in ignore list"})
            }
            return response
    else:
        response = {
            "statusCode": 200,
            "body": json.dumps({"status": "OK", "notification": "skipped", "reason": "no entry configured for event"})
        }
        return response

    response = {
        "statusCode": 200,
        "body": json.dumps({"status": "OK", "event": gh_event})
    }
    return response
