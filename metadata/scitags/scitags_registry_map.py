#!/bin/env python3

####
# Name: Scitags API Collector
# Description:
#   This script generates a YAML files from the relevant Scitags API
#
# Output Files:
#   experiments_map.yml:
#       File Format: YAML
#       Key: experiment ID       
#       Value: experiment name
#   activities_map.yml:
#       File Format: YAML
#       Key: experimentID_activityID
#       Value: activity name
#

import json
import yaml
import requests
import argparse
import logging
import os
import time

DEFAULT_SCITAGS_URL = "http://scitags.docs.cern.ch/api.json"


class ScitagsCollector:

    def __init__(self):
        self.log = None
        self.experiments_map = {}
        self.activities_map = {}
        self.collection = "scitags-map"

    def write_scitags(self, args):
        exp_p = os.path.join(args.output_yaml, "experiments_map.yml")
        with open(exp_p, 'w') as f:
            yaml.dump(self.experiments_map, f, sort_keys=True)
            self.log.info(
                f"Successfully written {exp_p}")

        act_p = os.path.join(args.output_yaml, "activities_map.yml")
        with open(act_p, 'w') as f:
            yaml.dump(self.activities_map, f, sort_keys=True)
            self.log.info(
                f"Successfully generated {act_p}")

    def _get_scitags(self):
        try:
            req = requests.get(DEFAULT_SCITAGS_URL)
            req.raise_for_status()
            data = json.loads(req.text)
        except requests.exceptions.HTTPError as e:
            self.log.error("HTTP error {0}".format(e))
            return
        except requests.exceptions.RequestException as e:
            self.log.error("Request error {0}".format(e))
        except ConnectionError as e:
            self.log.error("Connection error {0}".format(e))
        except ValueError as e:
            self.log.error(
                "Invalid JSON returned. Make sure the URL is correct. {0}".format(e))
        except:
            self.log.error("Unhandled exception")

        return data

    def collect(self, args):
        self.experiments_map = {}
        self.activities_map = {}
        data = self._get_scitags()

        for experiment in data.get('experiments', []):
            exp_id = experiment.get('expId')
            exp_name = experiment.get('expName')

            if exp_id is not None and exp_name is not None:
                self.experiments_map[str(exp_id)] = exp_name

                for activity in experiment.get('activities', []):
                    act_id = activity.get('activityId')
                    act_name = activity.get('activityName')

                    if act_id is not None and act_name is not None:
                        # Create a composite key: experimentID_activityID
                        composite_key = f"{exp_id}_{act_id}"
                        self.activities_map[composite_key] = act_name
        # write
        self.write_scitags(args)

    def add_cmdline_args(self, parser):
        parser.add_argument('--output-yaml', dest='output_yaml', default=None,
                            type=str, help='As optional filepath where YAML files will be stored')

    def check_cmdline_args(self, args):
        if not args.output_yaml:
            args.output_mmdb = os.environ.get('SCITAGS_OUTPUT_YAML', None)

    def build_arg_parser(self):
        # Parse command-line args
        parser = argparse.ArgumentParser(
            description='Scitags  collector that gathers information on experiments/activities mappings')
        parser.add_argument('--scitags_url', dest='scitags_url', default=None,
                            type=str, help='The base CRIC URL to query')
        parser.add_argument('--log-config', dest='log_config', default=None,
                            type=str, help='A logging configuration file to give to python logging')
        parser.add_argument('--verbose', dest='verbose',
                            action='store_true', help='Give more output')
        parser.add_argument('--periodic', dest='periodic', default=0, type=int,
                            help='Run this action periodically every number of seconds specified.')
        self.add_cmdline_args(parser)

        return parser

    def check_args(self, args):
        # check for environment variables
        if not args.scitags_url:
            args.cric_url = os.environ.get('SCITAGS_URL', DEFAULT_SCITAGS_URL)
        if not args.log_config:
            args.log_config = os.environ.get('SCITAGS_LOG_CONFIG', None)
        if not args.verbose:
            args.verbose = os.environ.get('SCITAGS_VERBOSE', False)
        if not args.periodic:
            args.periodic = int(os.environ.get('SCITAGS_PERIODIC', 0))

        # subclass hook to add more checks
        self.check_cmdline_args(args)

        # Setup logging
        if args.log_config:
            logging.config.fileConfig(args.log_config)
            self.log = logging.getLogger()
        else:
            logging.basicConfig(
                format="time=%(asctime)s level=%(levelname)s %(message)s")
            self.log = logging.getLogger()
            if args.verbose:
                self.log.setLevel(logging.DEBUG)
            else:
                self.log.setLevel(logging.INFO)

    def run(self):
        parser = self.build_arg_parser()
        args = parser.parse_args()
        self.check_args(args)

        # Get down to business
        if args.periodic > 0:
            self.log.info("collection={0} msg=Started".format(self.collection))
        while True:
            self.log.info(
                "collection={0} msg=Collection started".format(self.collection))
            self.collect(args)
            self.log.info(
                "collection={0} msg=Collection complete".format(self.collection))
            # if periodic, sleep, otherwise we are done
            if args.periodic > 0:
                self.log.info("collection={0} msg=Sleeping for {1} seconds".format(
                    self.collection, args.periodic))
                time.sleep(args.periodic)
            else:
                break


# Main function
if __name__ == "__main__":
    ScitagsCollector().run()

