#!/usr/bin/env python3

from util import generate_config, funcs
from pushbullet import Pushbullet
import json, os

config = generate_config.return_config()

# Get our MailerLite Secret used to sign requests
mailerlite_secret = os.getenv('mailerlite_secret')

# PB Key
pb_key    = os.getenv('pushbullet_api_key')

def handler(event, context):

    # MailerLite signature and payload
    mailerlite_signature = event['headers'].get('X-MailerLite-Signature')
    mailerlite_body      = event['body']
    mailerlite_payload   = json.loads(mailerlite_body)

    # If we don't have a signature abort!
    if mailerlite_signature is None:
        response = {
            "statusCode": 403,
            "body": json.dumps({"error": "'X-MailerLite-Signature' was not sent"})
        }
        return response

    # No secret means we can't authenticate, abort!
    if mailerlite_secret is None:
        response = {
            "statusCode": 500,
            "body": json.dumps({"error": "env variable 'mailerlite_secret' not set"})
        }
        return response

    # Split our signature and digest method
    digest, mailerlite_signature = mailerlite_signature.split('=')

    # Verify our signature and deny if it fails!
    if not funcs.verify_signature(mailerlite_secret, mailerlite_body, mailerlite_signature, digest):
        response = {
            "statusCode": 403,
            "body": json.dumps({"error": "Signature mismatch"})
        }
        return response

    # MailerLite can bulk send webhooks, so wrap it in a for
    for event in mailerlite_body['events']:
        mailerlite_event = event['type']
        # Check our event is defined, otherwise we just wont do anything
        if mailerlite_event in config['mailerlite']['events']:

            pb_payload = config['mailerlite']['events'][mailerlite_event]['pushbullet']

            title = pb_payload['title'].format(**mailerlite_payload)
            body  = pb_payload['body'].format(**mailerlite_payload)
            link  = pb_payload['link'].format(**mailerlite_payload)

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
