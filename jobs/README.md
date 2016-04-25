# Lava Jobs in deepin

# 当前定义的
- [network](network.json)  网络相关测试
- [vide_card](video_card.json) 显卡相关测试

# 维护方式
本目录下的所有json文件均是一个job定义. 文件名即JOB_NAME. 
[rr-checker-lav-bridge](https://ci.deepin.io/job/rr-checker-lava-bridge/build?delay=0sec) 触发时需要选择有效的
JOB_NAME

默认情况下rr-checker-lava-bridge会自动去查找本目录下所有的auto文件自动选择需要提交的测试.

# auto 格式
auto文件为一个有效的shell文件. 通过以下形式调用
```
./JOB_NAME.auto $(changelist)
```
并判断$?为0来决定使用对应的JOB_NAME.json.


一般可以通过以下方式来编写filter
```
echo $* | grep -e network -e wifi -e iw
```

# TODO
重构JOB_NAME.json文件. 抽取公共部分. 简化编写JOB的同时支持多个JOB同时被选择.


