#!/usr/bin/python -u
# -*- coding: utf-8 -*-

import urllib2
import csv
import sys
import os
import xmlrpclib
import time
import md5

def wait_output(server, id, max_tries, retries=-1):
    if retries == -1:
        retries = max_tries
    if retries == 0 :
        return None
    try:
        d = server.job_output(id).data
        return d
    except Exception as e:
        time.sleep(1)
        print "Waiting job %d to run %ds/%ds (E: %s)" % (id, retries, max_tries, e)
        return wait_output(server, id, max_tries, retries-1)

def show_output_log(server, id):
    out = wait_output(server, id, 100)
    if out == None:
        raise RuntimeError("Failed wait job %d.." % id)
    olen=0
    end=None
    out=""
    while end is None:
        nout=server.job_output(id,olen).data
        end=server.job_details(id)["end_time"]
        if md5.new(nout).digest() != md5.new(out).digest():
            out = nout
            olen=olen+len(out)
            #print "-----------------", olen, md5.new(out).hexdigest()
            print out

        if end is None:
            time.sleep(0.5)



def parse_flags():
    id=int(os.getenv("JOB_ID", 0))
    if id != 0:
        return id, True

    if len(sys.argv) < 2:
        return 0, False

    submit= sys.argv[1] == "-s"
    if submit:
        return int(sys.argv[2]), submit
    else:
        return int(sys.argv[1]), submit


def status_is_complete(server, id):
    return server.job_details(id)["status"]=="Complete"

def show_bundle(server, id):
    result=False
    try:
        response=urllib2.urlopen("%s/export" % (server.job_details(id)["_results_link"]))
        row_format="{:>15}" * 3
        print row_format.format("test", "count_pass", "count_fail")
        result=True
        for row in csv.DictReader(response, delimiter=','):
            if int(row["count_fail"]) > 0:
                result = False
            print row_format.format(row["test"], row["count_pass"], row["count_fail"])
        return result
    except Exception as e:
        print e
        return result


def main():
    username=os.getenv("LAVA_USERNAME", "admin")
    hostname=os.getenv("LAVA_HOSTNAME", "validation.deepin.io")
    token=os.getenv("LAVA_TOKEN")

    if token == None or hostname == None or username == None:
        print "Please setup LAVA_USRNAME, LAVA_HOSTNAME, LAVA_TOKEN environment"
        exit(-1)

    server = xmlrpclib.ServerProxy("http://%s:%s@%s/RPC2" % (username, token, hostname)).scheduler

    id, submit = parse_flags()
    if id == 0:
        print "Usage: %s [-s] job_id" % sys.argv[0]
        exit(-1)

    if submit:
        nid=server.resubmit_job(id)
        print "Submit job %d from %d" % (nid, id)
        print "See also http://%s/scheduler/job/%d" % (hostname, id)
        id=nid

    show_output_log(server, id)

    if not show_bundle(server, id):
        exit(-1)
    print "See also http://%s/scheduler/job/%d" % (hostname, id)


open("running", 'a').close()
main()
os.remove("running")
