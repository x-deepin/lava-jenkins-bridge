# lava-jenkins-bridge

本项目由三部分组成

1. rr-checker-lava-bridge CI项目的执行脚本.
2. lava-job-builder 生成需要的job描述文件
2. lava-job-submitter  提交job描述文件到lava服务器去,并实时反馈输出.


# rr-checker-lava-bridge

作为 [rr-checker-lava-bridge](https://ci.deepin.io/job/rr-checker-lava-bridge/) 项目的实际运行脚本

触发可以传递JOB_NAME参数作为Job 定义 https://ci.deepin.io/job/rr-checker-lava-bridge/build?delay=0sec
具体的JOB_NAME取值请参考 https://github.com/x-deepin/lava-jenkins-bridge/tree/master/jobs 目录

rr-checker-lava-bridge 参考 https://github.com/linuxdeepin/developer-center/wiki/Repository-Review-checker-dev
规范配置的．　


整体效果
1. rr.deepin.io 提交/更新 review
2. 触发rr-builder-rootfs 接着触发rr-checker-lava-bridge
3. 根据rr的review内容选择对应的JOB_NAME进行提交.

CI作为rr.deepin.io以及validation.deepin.io的桥梁进行
1. Job submit when repository try changing.
2. report lava job result to rr.deepin.io review page

## 配置方式

1. 直接在jenkins中运行本脚本
2. 设置合适的JOB_NAME. 目前是通过传递CI参数进行
3. 设置合适的$ROOTFS环境变量. 目前通过copy上游项目的parms.env并在其中进行设置.

# lava-job-submitter

通过xmlrpc接口实时显示Job的Output从而让jenkins可以和lava任务串联起来

1. 根据job\_details["_results_link"]中的bundle信息 判断是否成功
2. 通过job\_output(id, offset)以及job_details["end\_time"] + sleep 去poll
   Job的output并输出到stdout

```
usage: lava-job-submitter.py [-h] [--token TOKEN] [--host HOST] [--user USER]
                              [job_file]

Submit lava job and output the result

positional arguments:
  job_file       read job content from stdin default

optional arguments:
  -h, --help     show this help message and exit
  --token TOKEN  the lava authentication token
  --host HOST    the lava api server
  --user USER    the user to operation with lava api
```

# lava-job-builder

```
 % ./lava-job-builder.py -h
usage: lava-job-builder.py [-h] [--nfsrootfs NFSROOTFS] [--kernel KERNEL]
                           [--ramdisk RAMDISK]

Load lava job definition from stdin and overwrite values accord the arguments

optional arguments:
  -h, --help            show this help message and exit
  --nfsrootfs NFSROOTFS
                        overwrite the
                        actions.deploy_linaro_kernel.parameters.nfsrootfs
  --kernel KERNEL       overwrite the
                        actions.deploy_linaro_kernel.parameters.kernel
  --ramdisk RAMDISK     overwrite the
                        actions.deploy_linaro_kernel.parameters.ramdisk
```						


# TODO
1. (DONE) 根据之后的lava job,tests仓库直接抓取job定义并执行.
2. (DONE) 根据rr之后提供的changelist进行分析是否执行job以及执行哪些job
3. (DONE) 根据实际执行结果判断是否Job是成功．替换之前的job\_details["status"] == "Complte"的判断方式．
