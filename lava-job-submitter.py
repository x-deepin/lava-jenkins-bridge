#!/usr/bin/python3 -u
# -*- coding: utf-8 -*-

import urllib.request
import csv
import sys
import os
from xmlrpc import client
import time
import hashlib
import codecs
import argparse


def wait_output(server, id, max_tries):
    for i in range(max_tries):
        try:
            return server.job_output(id).data.decode()
        except Exception as e:
            time.sleep(1)
            # print("Waiting job {} to run {}s/{}s (E: {})".format(
            #            id, i, max_tries, e))


def show_output_log(server, id):
    out = wait_output(server, id, 18000)
    if out == None:
        raise RuntimeError("Failed wait job %d.." % id)
    olen = 0
    end = None
    out = ""

    def md5(s):
        m = hashlib.md5()
        m.update(s.encode())
        return m.hexdigest()
    while end is None:
        nout = server.job_output(id, olen).data.decode()
        end = server.job_details(id)["end_time"]
        if md5(nout) != md5(out):
            out = nout
            olen = olen + len(out)
            # print("-----------------", olen, md5(out))
            # print(out)
        if end is None:
            time.sleep(0.5)


def show_bundle(server, id):
    result = False
    found_custom_test = False
    try:
        response = urllib.request.urlopen(
            "%s/export" % (server.job_details(id)["_results_link"]))

        row_format = "{:>15}" * 3
        print(row_format.format("test_name", "count_pass", "count_fail"))
        result = True
        for row in csv.DictReader(codecs.iterdecode(response, 'utf-8')):
            if row["test"] != "lava" and row["test"] != None:
                found_custom_test = True
            if int(row["count_fail"]) > 0:
                result = False
            print(
                row_format.format(row["test"], row["count_pass"], row["count_fail"]))
        return result and found_custom_test
    except Exception as e:
        print(e)
        return result and found_custom_test


def build_server(args):
    username = args.user
    hostname = args.host
    token = args.token
    if token == None or hostname == None or username == None:
        print("Please setup user, server and token arguments")
        exit(-1)

    return client.ServerProxy(
        "https://%s:%s@%s/RPC2" % (username, token, hostname)).scheduler


def main():
    parser = argparse.ArgumentParser(
        description="Submit lava job and output the result"
    )
    parser.add_argument(
        "job_file", nargs="?", default=sys.stdin, help="read job content from stdin default", type=argparse.FileType("rt"))
    parser.add_argument("--token", help="the lava authentication token")
    parser.add_argument(
        "--host", help="the lava api server", default="validation.deepin.io")
    parser.add_argument(
        "--user", help="the user to operation with lava api", default="admin")

    args = parser.parse_args()

    server = build_server(args)

    job_content = args.job_file.read()
    id = server.submit_job(job_content)

    if id == 0:
        print("Failed submit job {}".format(job_content))
        exit(-1)

    print("Submit job to https://{}/scheduler/job/{}".format(args.host, id))

    show_output_log(server, id)

    if not show_bundle(server, id):
        print(
            "Running failed, see https://{}/scheduler/job/{}".format(args.host, id))
        exit(-1)

main()
