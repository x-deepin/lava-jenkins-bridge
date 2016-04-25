# lava-output-wrap

客户端通过xmlrpc接口实时显示Job的Output从而让jenkins可以和lava任务串联起来

1. 根据job\_details["_results_link"]中的bundle信息 判断是否成功
2. 通过job\_output(id, offset)以及job_details["end\_time"] + sleep 去poll
   Job的output并输出到stdout

CI上目前是放在 https://ci.deepin.io/job/rr-checker-lava-bridge/ 上

触发可以传递JOB_NAME参数作为Job 定义 https://ci.deepin.io/job/rr-checker-lava-bridge/build?delay=0sec
具体的JOB_NAME取值请参考 https://github.com/x-deepin/lava-jenkins-bridge/tree/master/jobs 目录

rr-checker-lava-bridge 参考 https://github.com/linuxdeepin/developer-center/wiki/Repository-Review-checker-dev
规范配置的．　

整体效果

1. rr.deepin.io 提交/更新 review
2. 触发rr-checker-lava-bridge
3. 根据rr的review内容选择对应的JOB_NAME进行提交.


CI作为rr.deepin.io以及validation.deepin.io的桥梁进行
1. Job submit when repository try changing.
2. report lava job result to rr.deepin.io review page


# TODO

1. (DONE) 根据之后的lava job,tests仓库直接抓取job定义并执行.
2. (DONE) 根据rr之后提供的changelist进行分析是否执行job以及执行哪些job
3. (DONE) 根据实际执行结果判断是否Job是成功．替换之前的job\_details["status"] == "Complte"的判断方式．
