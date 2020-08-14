---
title: 如何通过网卡名称获取其所对应的 IP 地址
date: 2020-08-11 11:32:23
tags:
- Python
- 网络
categories:
- 工作日常
---
## 代码
如果项目中有用到 netifaces 或者 psutil 库，可以直接使用下面的方法：

### 直接调用第三方库
- netifaces
```python
def via_netifaces():
    """
    调用第三方模块netifaces
    :return: 
    """
    ip_list = []
    for interface in netifaces.interfaces():
        if interface not in ['lo', 'sit0']:
            b = netifaces.ifaddresses(interface).get(netifaces.AF_INET)
            if b:
                for link in b:
                    ip_list.append(link['addr'])
    return ip_list
```
- psutil
```python
def get_net_ipaddr():
    ip_list = set()
    dic = psutil.net_if_addrs()
    for adapter in dic:
        snic_list = dic[adapter]
        mac = ''
        ipv4 = ''
        ipv6 = ''
        for snic in snic_list:
            if snic.family.name in {'AF_LINK', 'AF_PACKET'}:
                mac = snic.address
            elif snic.family.name == 'AF_INET':
                ipv4 = snic.address
            elif snic.family.name == 'AF_INET6':
                ipv6 = snic.address
            ip_list.add(ipv4)
        print('%s, %s, %s, %s' % (adapter, mac, ipv4, ipv6))
    return ip_list
```
如果觉得只是为了一个小功能引入第三方库有点大材小用，那么我们也可以自己造轮子。

### 标准库
```python
def std_get_ip_list():
    def get_ip_address_of_iface(ifname):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        ip_addr = ''
        try:
            ip_addr = socket.inet_ntoa(fcntl.ioctl(
                s.fileno(),
                0x8915,
                struct.pack('256s', bytes(ifname[:15], 'utf-8'))
            )[20:24])
        except OSError:
            pass
        return ip_addr

    all_eth = os.listdir('/sys/class/net/')
    ip_list = []
    for eth in all_eth:
        if eth not in ['lo', 'sit0']:
            ip = get_ip_address_of_iface(eth)
            ip_list.append(ip)
    return ip_list
```
这段代码的原始出处是[这里](https://stackoverflow.com/a/27423915)，我们主要尝试解释一下它的工作原理。

## 原理解释

### socket
Python 的 socket 模块提供了有关网络接口的底层控制方法。`socket.socket` 函数会创建一个新的 socket 对象。它的用法如下：

```plain
socket.socket(family=AF_INET, type=SOCK_STREAM, proto=0, fileno=None)
```

第一个参数 `family` 指定了网络地址的类型。最常用的值有两个：默认值 `AF_INET` 对应 IPv4，`AF_INET6` 是 IPv6。

第二个参数 `type` 代表了传输层协议的类型。默认值 `SOCK_STREAM` 是我们熟知的 TCP 协议，而 `SOCK_DGRAM` 则对应 UDP 协议。

因此，`s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)` 的含义是，创建一个使用 IPv4 网络和 UDP 协议的 socket 对象 `s`。

为了获取网卡的 IP 地址，创建 TCP socket 或是 UDP socket 是没有差别的。由于 `socket.AF_INET` 和 `socket.SOCK_STREAM` 都是 `socket.socket` 函数的默认参数，所以这一行实际上可以简写成`s = socket.socket()`。

socket 对象 `s` 创建后，可以通过 `s.fileno()` 获取这个 socket 的文件描述符（file descriptor）。

另外，代码中的 `socket.inet_ntoa` 函数把一个 4 字节 IP 地址（即 `struct in_addr`）转化成点分十进制的可读形式。（网络字节顺序的整型值 ->字符串形式的 IP 地址）

现在，我们可以推断出，从 `fcntl.ioctl` 到 `[20:24]` 这一大段内容，是用来获取网卡对应的 4 字节 IP 地址的。

### fcntl 与 ioctl

`fcntl` 与 `ioctl` 是 UNIX/Linux 系统中用于文件控制和 I/O 控制的两个系统调用。Python 在此基础上进行了封装。函数 `ioctl` 的用法如下，参考[此处](https://docs.python.org/zh-cn/3.7/library/fcntl.html#fcntl.fcntl)：

```python
fcntl.ioctl(fd, request, arg=0, mutate_flag=True)
```

参数 `fd` 是我们想控制的文件的文件描述符。在 UNIX/Linux 系统中，I/O 设备也用文件来表示，因此这里需要传入 socket 的文件操作符。

参数 `request` 是我们想要进行的操作。这个操作由一个预定义的 32 位整数表示。
    {% note info %}
    代码中使用的 `0x8915` 在 `/usr/include/linux/sockios.h` 文件中定义，它对应的符号是 `SIOCGIFADDR`，我们正是通过这一操作来取得 IPv4 地址。

    ```plainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplainplain
    [root@VM_0_16_centos ~]# cat /usr/include/linux/sockios.h |grep 

    0x8915#define SIOCGIFADDR	0x8915		/* get PA address	     */
    ```
    想要查询 `ioctl` 支持的所有操作，可以在命令行中输入 `man ioctl_list`。
    {% endnote %}

第三个参数 `arg` 是操作所需的参数，这通常是一个 32 位整数或一段二进制内容。
{% note info %}
根据[文档](https://man7.org/linux/man-pages/man7/netdevice.7.html)，使用 `SIOCGIFADDR` 时需要传入的参数是结构体 `struct ifreq`。`struct ifreq` 的定义位于 `/usr/include/net/if.h`

```plain
[root@VM_0_16_centos ~]# cat /usr/include/net/if.h | grep IFNAMSIZ

# define IFNAMSIZ	IF_NAMESIZE
	char ifrn_name[IFNAMSIZ];	/* Interface name, e.g. "en0".  */
	char ifru_slave[IFNAMSIZ];	/* Just fits the size */
	char ifru_newname[IFNAMSIZ];
# define _IOT_ifreq	_IOT(_IOTS(char),IFNAMSIZ,_IOTS(char),16,0,0)
# define _IOT_ifreq_short _IOT(_IOTS(char),IFNAMSIZ,_IOTS(short),1,0,0)
# define _IOT_ifreq_int	_IOT(_IOTS(char),IFNAMSIZ,_IOTS(int),1,0,0)
```

在我的计算机上，`IFNAMSIZ` 的值是 16，即网卡名称最长为 15 字节（第 16 个字节必须是 `\0` 用来表示字符串的结尾），而 `struct ifreq` 的大小是 40 字节。对于 `SIOCGIFADDR` 来说，只有前 16 个字节 `ifr_name` 是有意义的，后面的值都可以设定为 `0x00`。

操作 `SIOCGIFADDR` 返回的结果也是 `struct ifreq` 结构体。其中，网卡的 IPv4 地址信息包含在 `struct sockaddr ifr_addr` 结构体内。这个 4 字节的 IP 地址位于 `struct ifreq` 结构体 20-23 字节处。所以我们会看到，`fcntl.ioctl` 返回的结果后面有 `[20:24]`——只需要把这 4 个字节拿去转换就可以了。
{% endnote %}

到现在为止，只要我们可以正确生成 40 字节的 `struct ifreq` 结构体，就可以通过 `ioctl` 拿到 IPv4 的地址。生成结构体需要用到 Python 的 `struct` 模块。

### Python struct 与 unicode string

Python 的 `struct` 模块用于生成和解析二进制内容。`struct.pack` 的用法如下：

```python
struct.pack(fmt, v1, v2, ...)
```

这个函数比较像 `printf`，第一个参数用于设定格式，后续的参数用于填充内容。

`struct.pack('256s', ifname[:15])` 用 ifname 的前 15 个字节填充成了一个 256 字节的二进制空间，未指定内容的空间会用字节 `0x00` 填充。事实上，由于 `struct ifreq` 的大小只有 40 字节，将 `256s` 换成 `40s` 也能得到期望的 `struct ifreq` 结构体。

最后我们来讲一讲字符串的问题。Python 2 是不区分 `str` 和 `bytes` 的，所以 `ifname` 这个字符串可以直接拿来当一组字节用。代码中的 `ifname[:15]` 是一种防御性的措施，即只保留前 15 个字节。如果确信用户的输入合法，直接使用 `ifname` 也可以。但是在 Python 3 中，由于字符串不能隐式地当作一组字节用，所以需要额外的转换。具体来说就是把

```python2
struct.pack('256s', ifname[:15])
```
变成
```python3
struct.pack('256s', bytes(ifname[:15], 'utf-8'))
```
其中 utf-8 是字符串 ifname 的编码方法。
### 完整代码
```python
import fcntl
import socket
import struct

def get_ip_address_of_iface(ifname):
    s = socket.socket()
    ip_addr = ''
    try:
        # 拿到网卡名称(15来自Linux底层定义，与操作系统有关)并截取之后转化为utf-8的bytes字符串
        ifname_str2bytes = bytes(ifname[:15], 'utf-8')
        # 构造`struct ifreq` 结构体，对bytes进行填充至256位长度
        struct_ifreq = struct.pack('256s', ifname_str2bytes)
        # 发起操作请求，拿到返回，截取其中4位长度的IP地址作为有效值
        sockaddr_ifr_addr = fcntl.ioctl(s.fileno(),0x8915,struct_ifreq)[20:24]
        # 对4位的ip进行转换
        ip_addr = socket.inet_ntoa(sockaddr_ifr_addr)
    except OSError:
        pass
    return ip_addr
```

## 参考链接
[详解 Python 获取网卡 IP 地址 - bw_0927 - 博客园](https://www.cnblogs.com/my_life/articles/9187714.html)
[python - How to get the physical interface IP address from an interface - Stack Overflow](https://stackoverflow.com/questions/6243276/how-to-get-the-physical-interface-ip-address-from-an-interface)
