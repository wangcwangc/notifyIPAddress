# author : wangcwangc
# time : 2022/9/8 14:27
import netifaces
import time
import configparser


def get_host_ipv6():
    addresses = netifaces.ifaddresses('en0')
    ipv6_addr_list = addresses[netifaces.AF_INET6]
    ipv6_list = []
    for addr in ipv6_addr_list:
        ipv6 = addr['addr']
        if str(ipv6).startswith('fe'):
            continue
        return ipv6


def loop_monitor():
    while True:
        get_host_ipv6()
        time.sleep(60)  # 每分钟运行一次


def read_config():
    file = 'config.ini'
    config = configparser.ConfigParser()
    config.read(file)
    webhook = config.get('url', 'webhook')
    print(webhook)
    if webhook == '':
        print('请配置webhook地址')
        exit(0)
    ipv6 = config.get('ip', 'ipv6')
    if ipv6 == '':
        ipv6 = get_host_ipv6()
        print(ipv6)
        config.set('ip', 'ipv6', ipv6)
        config.write(open('config.ini', 'w'))


if __name__ == "__main__":
    read_config()
