#!usr/bin/env python3
# coding:utf-8
# Create Date:2019/6/6


import json


# 读取header
def get_headers():
    with open("headers.txt", "r", encoding="utf-8") as f:
        content = f.read()
        headers = json.loads(content)

    return headers
