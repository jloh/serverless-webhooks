#!/usr/bin/env python3

# Gets our config from yaml and returns it!

import argparse, yaml

def parse_args():
    parser = argparse.ArgumentParser(description='Python Serverless Webhook server.')
    parser.add_argument('-c', '--config', type=argparse.FileType('r'), default='config.yaml',
            help='config file to load settings from')
    args, unknown = parser.parse_known_args()

    return args

def load_config(config_file):
    print('Loading config file {}'.format(config_file.name))
    try:
        config = yaml.load(config_file)
    except yaml.YAMLError as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print('Error loading YAML {} on line {}'.format(e, exc_tb.tb_lineno))

    return config

def return_config():
    """
    Gets our config from YAML and returns it
    """

    args   = parse_args()
    config = load_config(args.config)

    return(config)

if __name__ == "__main__":
    return_config()
