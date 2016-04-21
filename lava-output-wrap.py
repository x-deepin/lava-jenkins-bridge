#!/usr/bin/python -u

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
    except:
        time.sleep(1)
        print "Waiting job %d to run %ds/%ds" % (id, retries, max_tries)
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




def try_get_job_id():
    try:
        id=int(os.environ["JOB_ID"])
        if id != 0:
            return id
    except:
        return 0

def xx():
    id = try_get_job_id()
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

def main():
    username = "admin"
    token = "li401l4uy3qjdym7gqjukr1f6lz83jabsbk6ykzgm5wxaq4oagq4cfehfwl6mwze6uhud9q5xmiepr5oxdiu9bp0r45kjhwh8m7dcu2058id04usn3r0e1wr24frafh5"
    hostname = "lava.deepin.io"
    hostname="10.0.3.133"
    server = xmlrpclib.ServerProxy("http://%s:%s@%s/RPC2" % (username, token, hostname)).scheduler

    id, submit = xx()
    if id == 0:
        print "Usage: %s [-s] job_id" % sys.argv[0]
        exit(-1)
     
    if submit:
        nid=server.resubmit_job(id)
        print "submit job %d from %d" % (nid, id)
        id=nid

    print "see also : http://%s/scheduler/job/%d" % (hostname, id)
    show_output_log(server, id)

    if not status_is_complete(server, id):
        exit(-1)
    print "see also : http://%s/scheduler/job/%d" % (hostname, id)

main()
