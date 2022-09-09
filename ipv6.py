# author : wangcwangc
# time : 2022/9/8 14:27
import netifaces


def get_host_ipv6():
    addresses = netifaces.ifaddresses('en0')
    ipv6_addr_list = addresses[netifaces.AF_INET6]
    ipv6_list = []
    for addr in ipv6_addr_list:
        ipv6 = addr['addr']
        if str(ipv6).startswith('fe'):
            continue
        return ipv6


if __name__ == '__main__':
    print(get_host_ipv6())
