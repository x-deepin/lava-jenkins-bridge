#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import copy
import itertools
import functools
import json
import sys
import argparse
import urllib.request
from xmlrpc import client
from html.parser import HTMLParser


class DeviceInfo(HTMLParser):

    def __init__(self, hostname, name):
        HTMLParser.__init__(self)
        self.in_tag = False
        self.tags = []
        response = urllib.request.urlopen(
            "https://%s/scheduler/device/%s" % (hostname, name))
        self.feed(str(response.read().decode('utf-8')))

    def handle_starttag(self, tag, attrs):
        if tag != "dd":
            return
        for attr in attrs:
            if attr[1] == "tag-name":
                self.in_tag = True

    def handle_endtag(self, tag):
        if tag != "dd":
            return

        if self.in_tag:
            self.in_tag = False

    def handle_data(self, data):
        import re
        if self.in_tag:
            self.tags.append(re.sub('\\n|\s+', '', data))


def cache_device_info(username, hostname, token):
    s = client.ServerProxy(
        "https://%s:%s@%s/RPC2" % (username, token, hostname))
    infos = []
    for dev in s.scheduler.all_devices():
        dinfo = DeviceInfo(hostname, dev[0])
        infos.append({
            "hostname": dev[0],
            "tags": dinfo.tags,
            "status": dev[2],
        })
    return infos


class JobTemplate:

    def __init__(self, device_infos, kernel, ramdisk, nfsrootfs, submitter):
        self.device_infos = device_infos
        self.kernel = kernel
        self.ramdisk = ramdisk
        self.nfsrootfs = nfsrootfs
        self.submitter = submitter
        self.jobs_by_target = {}
        self.jobs = []

    def feed(self, data):
        job = json.loads(data)
        # split testdef by target
        for idx, tdef in enumerate(job["testdef_repos"]):
            mtags = tdef["minimal_tags"]
            targets = [dinfo["hostname"]
                       for dinfo in self.device_infos if set(mtags).issubset(dinfo["tags"])]
            if len(targets) == 0:
                raise ResourceWarning("Can't match any targets for this job" +
                                      ", which require %s" % mtags)

            for target in targets:
                if target not in self.jobs_by_target:
                    self.jobs_by_target[target] = []

                t = copy.deepcopy(job)
                new_tdef = copy.deepcopy(tdef)
                del new_tdef["minimal_tags"]
                t["testdef_repos"] = [new_tdef]
                t["idx"] = idx
                self.jobs_by_target[target].append(t)

    def generate(self):
        for target, jobs in self.jobs_by_target.items():
            for k, group in itertools.groupby(jobs, lambda j: j["stream"]):
                group = list(group)
                job = copy.deepcopy(group[0])
                for t in group[1:]:
                    if t["timeout"] > job["timeout"]:
                        job["timeout"] = t["timeout"]
                    job["testdef_repos"] += t["testdef_repos"]

                self.jobs.append(
                    self.render(
                        "%s_%s_%d" % (target, job["name"],  job["idx"]),
                        job["testdef_repos"],
                        target,
                        job["stream"],
                        job["timeout"],
                    )
                )

        return self.jobs

    def render(self, name, test_defs, target, stream, timeout):
        job = {
            "actions": [
                {
                    "command": "deploy_linaro_kernel",
                    "parameters": {
                        "bootloadertype": "ipxe",
                        "kernel": self.kernel,
                        "ramdisk": self.ramdisk,
                        "nfsrootfs": self.nfsrootfs,
                        "target_type": "deepin",
                    },
                },
                {
                    "command": "boot_linaro_image",
                },
                {
                    "command": "lava_test_shell",
                    "parameters": {
                        "testdef_repos": test_defs,
                    },
                },
                {
                    "command": "submit_results",
                    "parameters": {
                        "server": "https://validation.deepin.io/RPC2/",
                        "stream": stream,
                    },
                },
            ],
            "job_name": name,
            "device_type": "x86_skip_ipxe",
            "target": target,
            "timeout": timeout,
        }
        if self.submitter != None:
            job["submitter"] = self.submitter
        return job


parser = argparse.ArgumentParser(
    description="Load lava job definition from stdin and overwrite values accord the arguments")


parser.add_argument(
    "--list-devices", help="Dump the lava devices information and exit.", default=False, type=bool)

parser.add_argument(
    "--nfsrootfs", help="overwrite the actions.deploy_linaro_kernel.parameters.nfsrootfs",
    default="https://validation.deepin.io/tftpboot/deepin.tar.gz")

parser.add_argument(
    "--kernel", help="overwrite the actions.deploy_linaro_kernel.parameters.kernel",
    default="https://validation.deepin.io/tftpboot/vmlinuz")

parser.add_argument(
    "--ramdisk", help="overwrite the actions.deploy_linaro_kernel.parameters.ramdisk",
    default="https://validation.deepin.io/tftpboot/initrd.img")

parser.add_argument(
    "--username", help="the username communicate with lava server",
    default="admin")

parser.add_argument("--token", help="the token communicate with lava server")

parser.add_argument(
    "--output", default="./output", help="generate job files")

parser.add_argument(
    "--hostname", help="the hostname of lava server",
    default="validation.deepin.io")

parser.add_argument(
    "--submitter", help="indicator who created this job?", default=None)

parser.add_argument(
    "job_file", nargs="*", default=sys.stdin, help="read job content from stdin default", type=argparse.FileType("rt"))

args = parser.parse_args()

dinfos = cache_device_info(args.username, args.hostname, args.token)

if args.list_devices:
    print(json.dumps(dinfos))
    print("\n")
    sys.exit(0)

jt = JobTemplate(dinfos, args.kernel,
                 args.ramdisk, args.nfsrootfs, args.submitter)


for f in args.job_file:
    jt.feed(f.read())


if not os.path.exists(args.output):
    os.makedirs(args.output)

for job in jt.generate():
    with open("%s/%s.json" % (args.output, job["job_name"]), "w") as f:
        f.write(json.dumps(job))
