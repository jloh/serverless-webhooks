#!/usr/bin/env python3

from util import generate_config, funcs
from pushbullet import Pushbullet
import json, os

config = generate_config.return_config()

# Get our Discourse Secret used to sign requests
discourse_secret = os.getenv('discourse_secret')

# PB Key
pb_key    = os.getenv('pushbullet_api_key')

def handler(event, context):

    # Discourse event, signature and payload
    discourse_event     = event['headers']['X-Discourse-Event']
    discourse_signature = event['headers'].get('X-Discourse-Event-Signature')
    discourse_body      = event['body']
    discourse_payload   = json.loads(discourse_body)

    # If we don't have a signature abort!
    if discourse_signature is None:
        response = {
            "statusCode": 403,
            "body": json.dumps({"error": "'X-Discourse-Event-Signature' was not sent"})
        }
        return response

    # No secret means we can't authenticate, abort!
    if discourse_secret is None:
        response = {
            "statusCode": 500,
            "body": json.dumps({"error": "env variable 'discourse_secret' not set"})
        }
        return response

    # Split our signature and digest method
    digest, discourse_signature = discourse_signature.split('=')

    # Verify our signature and deny if it fails!
    if not funcs.verify_signature(discourse_secret, discourse_body, discourse_signature, digest):
        response = {
            "statusCode": 403,
            "body": json.dumps({"error": "Signature mismatch"})
        }
        return response

    # Check our event is defined, otherwise we just wont do anything
    if discourse_event in config['discourse']['events']:
        # Get our current event into a more sensible context
        event = config['discourse']['events'][discourse_event]

        pb_payload = event['pushbullet']

        title = pb_payload['title'].format(**discourse_payload)
        body  = pb_payload['body'].format(**discourse_payload)
        link  = pb_payload['link'].format(**discourse_payload)

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
        resposne = {
            "statusCode": 200,
            "body": json.dumps({"status": "OK", "notification": "skipped", "reason": "no entry configured for event"})
        }
        return response
