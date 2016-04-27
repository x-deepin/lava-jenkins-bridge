#!/usr/bin/python3
# -*- coding: utf-8 -*-


import json
import sys
import argparse

parser = argparse.ArgumentParser()

parser.add_argument(
    "--nfsrootfs", help="overwrite the actions.deploy_linaro_kernel.parameters.nfsrootfs",
    default="https://validation.deepin.io/tftpboot/deepin.tar.gz")

parser.add_argument(
    "--kernel", help="overwrite the actions.deploy_linaro_kernel.parameters.kernel",
    default="https://validation.deepin.io/tftpboot/vmlinuz")

parser.add_argument(
    "--ramdisk", help="overwrite the actions.deploy_linaro_kernel.parameters.ramdisk",
    default="https://validation.deepin.io/tftpboot/initrd.img")

args = parser.parse_args()

job = json.loads(sys.stdin.read())
for idx, action in enumerate(job["actions"]):
    if action["command"] == "deploy_linaro_kernel":
        if args.kernel != "":
            action["parameters"]["kernel"] = args.kernel

        if args.ramdisk != "":
            action["parameters"]["ramdisk"] = args.ramdisk

        if args.nfsrootfs != "":
            action["parameters"]["nfsrootfs"] = args.nfsrootfs

        job["actions"][idx] = action

print(json.dumps(job))
