# author : wangcwangc
# time : 2022/9/8 14:27
import json

import netifaces
import time
import configparser
import requests
import urllib3

urllib3.disable_warnings()


def get_host_ipv6():
    addresses = netifaces.ifaddresses("en0")
    ipv6_addr_list = addresses[netifaces.AF_INET6]
    for addr in ipv6_addr_list:
        ipv6 = addr["addr"]
        if str(ipv6).startswith("fe"):
            continue
        return ipv6


def loop_monitor():
    while True:
        main()
        time.sleep(60)  # 每分钟运行一次


def read_config():
    file = "config.ini"
    config = configparser.ConfigParser()
    config.read(file)
    webhook = config.get("url", "webhook")
    if webhook == "":
        print("请配置webhook地址")
        exit(0)
    ipv6 = config.get("ip", "ipv6")
    if ipv6 == "":
        ipv6 = get_host_ipv6()
        config.set("ip", "ipv6", ipv6)
        config.write(open("config.ini", "w"))
    return webhook, ipv6


def write_ipv6_to_config(ipv6):
    file = "config.ini"
    config = configparser.ConfigParser()
    config.read(file)
    config.set("ip", "ipv6", ipv6)
    config.write(open("config.ini", "w"))


def main():
    webhook, ipv6 = read_config()
    new_ipv6 = get_host_ipv6()
    if ipv6 != new_ipv6:
        print("ipv6 已变更！")
        print("old ipv6 : " + ipv6)
        print("new ipv6 : " + new_ipv6)
        ipv6 = new_ipv6
        write_ipv6_to_config(ipv6)
        notify_by_webhook(webhook, ipv6)


def notify_by_webhook(webhook, ipv6):
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36"
    }
    payload_message = {
        "msg_type": "post", "content": {"post": {"zh_cn": {"title": "你的公网IP变了", "content": [
            [{"tag": "text", "text": str("IPV6地址：http://[%s]" % ipv6)}]]}}}}

    try:
        res = requests.post(webhook, data=json.dumps(payload_message), verify=False, headers=headers)
        if res:
            ret_json = res.json()
            if "StatusMessage" in ret_json:
                msg = ret_json["StatusMessage"]
                print("ipv6 通知 : " + msg)
            else:
                print("通知失败")
    except Exception as e:
        print(e)


def first_notify_ipv6():
    webhook, ipv6 = read_config()
    ipv6 = get_host_ipv6()
    print("第一次运行")
    print("webhook : " + webhook)
    print("ipv6 : " + ipv6)
    notify_by_webhook(webhook, ipv6)
    write_ipv6_to_config(ipv6)


if __name__ == "__main__":
    first_notify_ipv6()
    loop_monitor()
