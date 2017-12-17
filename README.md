# Serverless Webhooks

[![license](https://img.shields.io/github/license/jloh/dotfiles.svg)]() [![serverless](https://img.shields.io/badge/language-python-brightgreen.svg)]() [![serverless](https://img.shields.io/badge/serverless-1.22.0+-green.svg)]()

Serverless Webhooks is a small python project that digests webhooks from services that don't easily support push notifications and turns them into Pushbullet pushes. Depending on the number of events this project should fit under the free tier on AWS.

At this stage it supports GitHub, Discourse and Mailerlite webhooks inbound and only Pushbullet for notifications. Eventually I would like to move the Pushbullet code out to be more portable and support other platforms.

## Setup

### Enncrypted Variables

This project uses [AWS SSM](https://serverless.com/framework/docs/providers/aws/guide/variables/#reference-variables-using-the-ssm-parameter-store) environment variables to store secret tokens. A below example shows how to store them using the AWS CLI tools:

```
aws ssm put-parameter --name /hooks/pushbullet_api_key --value <secure token in here> --type SecureString
```

### Requirments

Install `serverless` and `serverless-python-requirements`:

```
npm install -g serverless
sls plugin install serverless-python-requirements
```

Install python requirements  
**Note:** Its highly suggested you install the python requirments inside a virtualenv!

```
pip install -r requirements.txt
```

Now login to [Pushbullet](https://www.pushbullet.com/#settings) and generate an access token. This access token should be store as a [SSM variable](#requirments) under `/hooks/pushbullet_api_key`.

Now deploy your Serverless gateway:

```
sls deploy
```

### Endpoints

#### GitHub

1. Generate a [secret token](https://developer.github.com/webhooks/securing/)  
  You could use `ruby -rsecurerandom -e 'puts SecureRandom.hex(20)'`
1. Add your secret to [AWS SSM](#enncrypted-variables) under `/hooks/github_secret` eg:
    ```
    aws ssm put-parameter --name /hooks/github_secret --value a3f7b3d530ab15e2f07df0324f8255cfcade49cd --type SecureString
    ```
1. Confirm your gateway that serverless created above (check it via `sls info`)
1. Go to your repository settings -> [Webhooks](https://developer.github.com/webhooks/).
1. Add a new webhook:
   * Payload URL -> Your serverless POST endpoint for GitHub
   * Content Type -> `application/json`
   * Secret -> The secret you generated above
   * Events -> The events configured in `config.yaml`
1. Click add *Add Webhook*!

If you've done everything above correctly you should recieve a Ping event from GitHub via Pushbullet.

#### Discourse

1. Generate a secret to sign the payloads with
   You could use `ruby -rsecurerandom -e 'puts SecureRandom.hex(20)'`
1. Add your secret to [AWS SSM](#enncrypted-variables) under `/hooks/discourse_secret` eg:
    ```
    aws ssm put-parameter --name /hooks/discourse_secret --value a3f7b3d530ab15e2f07df0324f8255cfcade49cd --type SecureString
    ```
1. Confirm your gateway that serverless created above (check it via `sls info`)
1. Go to the [Discourse Admin interface](https://meta.discourse.org/t/49045) -> API -> Webhooks -> New Webhook
1. Enter your settings into Discourse:
   * Payload URL for the Discourse endpoint (`/v1/discourse`)
   * Content-Type -> `application/json`
   * Secret -> the one you generated above

If you've done everything above correctly try and send a ping event to your Discourse endpoint!

#### Mailerlite

Doco coming!

---

**Licence:** MIT
