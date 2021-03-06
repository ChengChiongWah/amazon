#!/usr/bin/env python3.5
# coding:utf-8
import time

log_config = {
    'file': 'logs.txt'
}


def set_log_path():
    fmt = '%Y%m%d%H%M%S'
    value = time.localtime(int(time.time()))
    dt = time.strftime(fmt, value)
    log_config['file'] = 'logs/log.{}.txt'.format(dt)


class Log(object):
    def log(*args, **kwargs):
        # time.time() 返回 unix time
        # 如何把 unix time 转换为普通人类可以看懂的格式呢？
        fmt = '%Y/%m/%d %H:%M:%S'
        value = time.localtime(int(time.time()))
        dt = time.strftime(fmt, value)
        # 这样确保了每次运行都有一个独立的 path 存放 log
        path = log_config.get('file')
        if path is None:
            set_log_path()
            path = log_config['file']
        with open(path, 'a', encoding='utf-8') as f:
            print(dt, *args, file=f, **kwargs)
