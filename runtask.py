#!usr/bin/env python3
# coding:utf-8
# Create Date:2019/4/29

import requests
import json
import os
import time
import mylogger
from datetime import datetime

base_dir = os.getcwd()
# 获取当前目录下的请求头文件
with open(base_dir+"\\headers.txt", "r", encoding="utf-8") as f:
    content = f.read()
    headers = json.loads(content)

result = os.path.join("result")
if not os.path.exists(result):
    os.mkdir(result)
resultpath = os.path.join(result, str(datetime.now().strftime("%y%m%d")))
if not os.path.exists(resultpath):
    os.mkdir(resultpath)


class OpenCloudSinger(object):
    def __init__(self):
        self.base_url = "https://fa022db3-07a2-4d6f-acad-c611de5895dc.mock.pstmn.io"
        self.mylog = mylogger.mylogger()

    def run_task(self):
        i = 0
        while i < 10:
            try:
                time.sleep(2)
                resp_run = requests.post(self.base_url+"/api/task/1623/running", headers=headers, timeout=5)  # 执行任务
                self.mylog.info(resp_run.status_code)
                if resp_run.status_code == 200:
                    json_dict_run = json.loads(json.loads(resp_run.content)["data"])
                    running_id = str(json_dict_run["task_running_id"])  # 获取任务运行id
                    return running_id
                else:
                    i += 1                                        # 出现异常时进行重试
            except requests.exceptions.RequestException as e:
                i += 1
                self.mylog.info(e)

    def get_report(self):
        i = 0
        run_id = self.run_task()
        while i < 30:
            try:
                time.sleep(2)
                resp_report = requests.get(self.base_url + "/api/task/running/" + run_id + "/summary",     # 查看任务执行结果
                                           headers=headers, timeout=5)
                self.mylog.info("Status code:%s Response content:%s" % (resp_report.status_code, resp_report.content))
                if resp_report.status_code == 200:
                    json_dict_report = json.loads(resp_report.content)["data"]
                    if json_dict_report["duration"] == "0":                # 判断是否已经执行完毕，如果没有执行完成再次查询
                        i += 1
                    else:
                        return json_dict_report["case_summary"]
            except requests.exceptions.RequestException as e:        # 出现异常时重试
                i += 1
                self.mylog.info(e)

    def get_result(self):
        report = self.get_report()
        success_count = 0
        fail_count = 0
        reportpath = os.path.join(resultpath, "report_" + datetime.now().strftime("%H%M%S") + ".txt")
        for i in report:
            if i["pass_rate"] == "FAIL(0/1/1)":    # 校验case是否通过
                fail_count += 1
                with open(reportpath, "a") as file:
                    file.writelines("case_id:%d" % (i["case_id"]) + "  case_name:%s" % (i["case_name"]) +
                                    "  test_result:failed" + "\n")
            else:
                success_count += 1
                with open(reportpath, "a") as file:
                    file.writelines("case_id:%d" % (i["case_id"]) + "  case_name:%s" % (i["case_name"]) +
                                    "  test_result:successful" + "\n")
        with open(reportpath, "a") as file:
            file.writelines("Test Failed: %d Test Successful: %d" % (fail_count, success_count))
        if fail_count > 0:
            return False, str(fail_count)
        else:
            return True, str(len(report))

