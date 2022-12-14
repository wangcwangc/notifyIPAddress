# author : wangcwangc
# time : 2022/9/8 14:27
import json
import os
from pathlib import Path

import netifaces
import time
import configparser
import requests
import urllib3

urllib3.disable_warnings()


def get_host_ipv6():
    addresses = netifaces.ifaddresses("en0")
    # addresses = netifaces.ifaddresses("bond0")  # docker
    ipv6_addr_list = addresses[netifaces.AF_INET6]
    for addr in ipv6_addr_list:
        ipv6 = addr["addr"]
        if str(ipv6).startswith("fe"):
            continue
        return ipv6


def get_host_ipv4():
    ipv4 = requests.get('https://checkip.amazonaws.com').text.strip()
    return ipv4


def loop_monitor():
    while True:
        main()
        time.sleep(600)  # 每10分钟运行一次


def read_config():
    path = Path(__file__)
    root_dir = path.parent.absolute()
    config_path = os.path.join(root_dir, "config.ini")
    # file = "config.ini"
    config = configparser.ConfigParser()
    config.read(config_path)
    webhook = config.get("url", "webhook")
    if webhook == "":
        print("请配置webhook地址")
        exit(0)
    ipv6 = config.get("ip", "ipv6")
    ipv4 = config.get("ip", "ipv4")
    if ipv6 == "" or ipv4 == "":
        ipv6 = get_host_ipv6()
        ipv4 = get_host_ipv4()
        config.set("ip", "ipv6", ipv6)
        config.set("ip", "ipv4", ipv4)
        config.write(open(config_path, "w"))
    return webhook, ipv6, ipv4


def write_ip_to_config(ipv6, ipv4):
    path = Path(__file__)
    root_dir = path.parent.absolute()
    config_path = os.path.join(root_dir, "config.ini")
    # file = "config.ini"
    config = configparser.ConfigParser()
    config.read(config_path)
    config.set("ip", "ipv6", ipv6)
    config.set("ip", "ipv4", ipv4)
    config.write(open(config_path, "w"))


def main():
    webhook, ipv6, ipv4 = read_config()
    new_ipv6 = get_host_ipv6()
    new_ipv4 = get_host_ipv4()
    if ipv6 != new_ipv6 or ipv4 != new_ipv4:
        print("ip 已变更！")
        print("old ipv6 : " + ipv6)
        print("new ipv6 : " + new_ipv6)
        print("old ipv4 : " + ipv4)
        print("new ipv4 : " + new_ipv4)
        ipv6 = new_ipv6
        ipv4 = new_ipv4
        write_ip_to_config(ipv6, ipv4)
        notify_by_webhook(webhook, ipv6, ipv4)
    else:
        print("ipv6 未变更！ 地址为 : " + new_ipv6)


def notify_by_webhook(webhook, ipv6, ipv4):
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36"
    }
    payload_message = {
        "msg_type": "post",
        "content": {
            "post": {
                "zh_cn": {
                    "title": "你的公网IP变了",
                    "content": [[{
                        "tag": "text",
                        "text": "IPV6 HTTP地址： http://[%s] \n"
                                "IPV6 地址： %s \n"
                                "IPV4 地址： %s" % (ipv6, ipv6, ipv4)
                    }]]
                }
            }
        }
    }

    try:
        res = requests.post(webhook, data=json.dumps(payload_message), verify=False, headers=headers)
        if res:
            ret_json = res.json()
            if "StatusMessage" in ret_json:
                msg = ret_json["StatusMessage"]
                print("ipv6 通知 : " + msg)
            else:
                print("通知失败")
                print(res.json())
    except Exception as e:
        print(e)


def first_notify_ipv6():
    webhook, ipv6, ipv4 = read_config()
    ipv6 = get_host_ipv6()
    ipv4 = get_host_ipv4()
    print("第一次运行")
    print("webhook : " + webhook)
    print("ipv6 : " + ipv6)
    print("ipv4 : " + ipv4)
    notify_by_webhook(webhook, ipv6, ipv4)
    write_ip_to_config(ipv6, ipv4)


if __name__ == "__main__":
    first_notify_ipv6()
    loop_monitor()
