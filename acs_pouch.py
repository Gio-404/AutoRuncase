#!usr/bin/env python3
# coding:utf-8
# Create Date:2019/6/6


import requests
import json
import runtask
import read_headers
import csv
import mylogger


class Pouch(object):
    def __init__(self, updateid):
        self.run = runtask.OpenCloudSinger()
        self.headers = read_headers.get_headers()
        self.updateid = updateid
        self.mylog = mylogger.mylogger()
        self.base_url = "https://fa022db3-07a2-4d6f-acad-c611de5895dc.mock.pstmn.io"

    # 从csv读取ip类
    @staticmethod
    def get_ip():
        ip_list = []
        with open("pouch_list.csv", "rb") as f:
            reader = f.readlines()
            for ip in reader:
                ip_list.append(ip.decode().split(",")[0])
        ip_list.remove("IP")
        return ip_list

    # 将结果写入csv
    @staticmethod
    def write_result(data):
        headers = ["IP", "RESULT", "COUNT"]
        with open("pouch_result.csv", "w", newline='') as f:
            writecsv = csv.DictWriter(f, headers)
            writecsv.writeheader()
            writecsv.writerows(data)

    def update_ip(self):
        ip_list = self.get_ip()
        data = []
        result_dict = {"IP": None, "RESULT": None, "COUNT": None}
        for ip in enumerate(ip_list):
            try:
                payload = {"addr": ip, "is_main_test_module": True}
                resp_url = requests.put(self.base_url + "/api/task/env/" + self.updateid, json=payload,   # 修改请求ip
                                        headers=self.headers)
                if resp_url.status_code == 200:
                    resp = json.loads(resp_url.text)["data"]
                    self.mylog.info("current ip: %s" % resp["addr"])
                    result = self.run.get_result()
                    result_dict["IP"] = resp["addr"]
                    result_dict["RESULT"] = result[0]
                    result_dict["COUNT"] = result[1]
                    data.append(result_dict)
            except requests.exceptions.RequestException as e:
                self.mylog.info(e)
        self.write_result(data)
