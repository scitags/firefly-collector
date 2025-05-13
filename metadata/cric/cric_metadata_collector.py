#!/bin/env python3

####
# Name: CRIC metadata Collector
# Description:
#   This script generates a MMDB file that collects relevant CRIC metadata
#
# Output Files:
#   cric.mmdb :
#       File Format: MMDB
#       Key: IP Range institute
#       Value:
#           name: The name of the CRIC site (e.g. AGLT2)
#           latitude: The latitude of the site (e.g. 43.101)
#           longitude: The longitude of the site (e.g. -81.111)
#           rc_country: A short name for the organization (e.g. United States)
#           rc_site: A long version of the organization name (e.g. AGLT2)
#           rc_tier_level: A list of types that apply to this organization (e.g. 2)

import time
import logging
import requests
import argparse
import os
from netaddr import IPSet
from json import dumps
#pip install -U git+https://github.com/VimT/MaxMind-DB-Writer-python
from mmdb_writer import MMDBWriter


DEFAULT_CRIC_URL="http://wlcg-cric.cern.ch/api/core/rcsite/query/?json"

class CRICMetadataCollector:

    def __init__(self):
        self.log = None
        self.collection = "cric_metadata"

    def _write_mmdb(self, args, writer):
        outfile = args.output_mmdb
        if outfile:
            writer.to_db_file(outfile)

    def _get_cric_json(self, url):
        self.log.debug(f"Getting url {url}")
        result = requests.get(url,verify=False)
        #just exit if there are exceptions for now
        result_json = None
        try:
            result.raise_for_status()
            result_json = result.json()
        except requests.exceptions.HTTPError as e:
            self.log.error("HTTP error {0}".format(e))
            return
        except requests.exceptions.RequestException as e:
            self.log.error("Request error {0}".format(e))
        except ConnectionError as e:
            self.log.error("Connection error {0}".format(e))
        except ValueError as e:
            self.log.error("Invalid JSON returned. Make sure the URL is correct. {0}".format(e))
        except:
            self.log.error("Unhandled exception")

        return result_json

    def collect(self, args):
        url = DEFAULT_CRIC_URL
        mmdb = MMDBWriter(ip_version=6, ipv4_compatible=True, database_type="GeoLite2-City")

        if url:
            result_json = self._get_cric_json(url)
            if result_json:
                for result in result_json.values():
                    cric_vals = {"cric":{}}
                    # this will create 'location' if it doesn't exist so we don't run into keyerror
                    cric_vals.setdefault("location", { "lat": 0.0, "lon": 0.0 })

                    # add all relevant metadata for the ATLAS-CRIC sites that we care about
                    # add name
                    if result.get("name", None):
                        cric_vals["name"] = result["name"]
                    # add latitude
                    if result.get("latitude", None):
                        cric_vals["location"]["lat"] = result["latitude"]
                    # add longitude
                    if result.get("longitude", None):
                        cric_vals["location"]["lon"]  = result["longitude"]
                    # add rc_country
                    if result.get("country", None):
                        cric_vals["rc_country"] = result["country"]
                    # add rc_tier_level
                    if result.get("rc_tier_level", None):
                        cric_vals["tier"] = result["rc_tier_level"]

                    for netr in result.get("netroutes", {}).values():
                        cric_vals["net_site"] = netr.get("name", "unknown")
                        ip_prefixes = []
                        for key, prefixes in netr.get("networks", {}).items():
                            for prefix in prefixes:
                                ip_prefixes.append(prefix)
                        self.log.debug(cric_vals)
                        self.log.debug(ip_prefixes)
                        #Record format:
                        # {"city": {"names": { "en": "JSON_TEXT_GOES_HERE"}},"location": {"latitude": 0.0, "longitude": 0.0 }}
                        # We have to have location or it won't work, we can strip it out in logstash as well
                        mmdb.insert_network(IPSet(ip_prefixes), { "city": { "names":{ "en": dumps(cric_vals) } }, "location": { "latitude": 0.0, "longitude": 0.0 } })

        #write to MMDB file
        self._write_mmdb(args, mmdb)

    def add_cmdline_args(self, parser):
        parser.add_argument('--output_mmdb', dest='output_mmdb', default=None, type=str, help='As optional filepath where MMDB metadata will be stored')

    def check_cmdline_args(self, args):
        if not args.output_mmdb:
            args.output_mmdb= os.environ.get('CRIC_META_OUTPUT_MMDB', None)

    def build_arg_parser(self):
        #Parse command-line args
        parser = argparse.ArgumentParser(description='CRIC metadata collector that gathers information an stores in cache for measurement ingest')
        parser.add_argument('--cric_url', dest='cric_url', default=None, type=str, help='The base CRIC URL to query')
        parser.add_argument('--log-config', dest='log_config', default=None, type=str, help='A logging configuration file to give to python logging')
        parser.add_argument('--verbose', dest='verbose', action='store_true', help='Give more output')
        parser.add_argument('--periodic', dest='periodic', default=0, type=int, help='Run this action periodically every number of seconds specified.')
        self.add_cmdline_args(parser)

        return parser

    def check_args(self, args):
        #check for environment variables
        if not args.cric_url:
            args.cric_url = os.environ.get('CRIC_URL', DEFAULT_CRIC_URL)
        if not args.log_config:
            args.log_config = os.environ.get('CRIC_META_LOG_CONFIG', None)
        if not args.verbose:
            args.verbose = os.environ.get('CRIC_META_VERBOSE', False)
        if not args.periodic:
            args.periodic = int(os.environ.get('CRIC_META_PERIODIC', 0))

        #subclass hook to add more checks
        self.check_cmdline_args(args)

        #Setup logging
        if args.log_config:
            logging.config.fileConfig(args.log_config)
            self.log = logging.getLogger()
        else:
            logging.basicConfig(format="time=%(asctime)s level=%(levelname)s %(message)s")
            self.log = logging.getLogger()
            if args.verbose:
                self.log.setLevel(logging.DEBUG)
            else:
                self.log.setLevel(logging.INFO)

    def run(self):
        parser= self.build_arg_parser()
        args = parser.parse_args()
        self.check_args(args)

        #Get down to business
        if args.periodic > 0:
            self.log.info("collection={0} msg=Started".format(self.collection))
        while True:
            self.log.info("collection={0} msg=Collection started".format(self.collection))
            self.collect(args)
            self.log.info("collection={0} msg=Collection complete".format(self.collection))
            # if periodic, sleep, otherwise we are done
            if args.periodic > 0:
                self.log.info("collection={0} msg=Sleeping for {1} seconds".format(self.collection, args.periodic))
                time.sleep(args.periodic)
            else:
                break

#Main function
if __name__ == "__main__":
    CRICMetadataCollector().run()
