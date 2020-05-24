---
title: Python3 报错"TypeError:a-bytes-like-object-is-required,not-'str'"解决办法
date: 2019-07-11 14:26:37
tags:
 - Python
 - Python3
---
今天在解析一个工具输出问题时遇到这两个编码错误，记录一下。
- TypeError: a bytes-like object is required, not 'str'
- UnicodeDecodeError: 'utf-8' codec can't decode byte 0xb3 in position 38: invalid start byte
<!--more-->

## 先上代码

```python
import subprocess

class ExecCommandError(Exception):
    pass


class ExecCommand:

    @staticmethod
    def cust_popen_list(cmdlist, close_fds=True):
        """
        subprocess.call只接受数组变量作为命令，并将数组的第一个元素作为命令，剩下的全部作为该命令的参数。
        :param cmdlist:
        :param close_fds:
        :return:
        """
        lastcmdlist = list()
        lastcmdlist.extend(cmdlist)
        try:
            proc = subprocess.Popen(lastcmdlist, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                    close_fds=close_fds)
            retcode = proc.wait()
            return retcode, proc
        except Exception as e:
            raise (ExecCommandError, e)
            
class HwMaker:
    def __init__(self):
        self.retcode = 1
        self.proc = None
        
    @staticmethod
    def exec_command(cmd_list=None):
        """
        调用执行命令的程序
        :param cmd_list: list,
        :return:
        """
        assert cmd_list
        cmd = ExecCommand()
        return cmd.cust_popen_list(cmd_list)
        
    @staticmethod
    def make_label(label):
        """
        如果以空格分割，则替换为 with_under_case,最后调用lower()返回lower_with_under_case
        :param label:
        :return:
        """
        split_label = label.split()
        label = '_'.join([span.lower() for span in split_label]) if len(split_label) > 1 else label.lower()
        return label
        
class SensorMaker(HwMaker):

    @staticmethod
    def secs2hours(secs):
        """
        秒转化为小时
        :param secs:
        :return:
        """
        mm, ss = divmod(secs, 60)
        hh, mm = divmod(mm, 60)
        return "%d:%02d:%02d" % (hh, mm, ss)

    def parse_vertical_line(self, parser_data):
        """
        以“|” 分割之后获取有用信息
        :param parser_data:
        :return:
        """
        _expect_info = dict()
        for line in parser_data:
            strip_line = line.strip().decode('utf-8', "ignore")
            if '|' in strip_line:
                item, value = [item.strip() for item in strip_line.split('|')]
                lower_label = self.make_label(item)
                _expect_info[lower_label] = value
        return _expect_info

    def ipmi_pminfo(self):
        """
         [SlaveAddress = B2h] [Module 2]
         Item                           |                Value
         ----                           |                -----
         Status                         |     [STATUS OK](00h)
         AC Input Voltage               |              237.0 V
         AC Input Current               |               0.36 A
         DC 12V Output Voltage          |              12.04 V
         DC 12V Output Current          |               5.07 A
         Temperature 1                  |              34C/94F
         Temperature 2                  |              37C/98F
         Fan 1                          |             5400 RPM
         Fan 2                          |              985 RPM
         DC 12V Output Power            |                 61 W
         AC Input Power                 |                 78 W
         PMBus Revision                 |               0xD222
         PWS Serial Number              |      ³³³³³³³U³³³³³³³
         PWS Module Number              |         ³³³³³³³³³³³³
         PWS Revision                   |               ³³³³³³

         out: {'status': '[STATUS OK](00h)',
             'ac_input_voltage': '237.0 V',
             'ac_input_current': '0.39 A',
             'dc_12v_output_voltage': '12.04 V',
             'dc_12v_output_current': '5.19 A',
             'temperature_1': '34C/94F',
             'temperature_2': '37C/98F',
             'fan_1': '5424 RPM',
             'fan_2': '985 RPM',
             'dc_12v_output_power': '63 W',
             'ac_input_power': '71 W',
             'pmbus_revision': '0xD222',
             'pws_serial_number': 'U',
             'pws_module_number': '',
             'pws_revision': ''}

        :return:
        """
        _pm_info = {}
        _cmd = ['ipmicfg', '-pminfo']
        self.retcode, self.proc = self.exec_command(_cmd)
        if self.retcode == 0:
            # 截取有用行（排除前三行）
            out_data = self.out_data()
            if out_data:
                _pm_info = self.parse_vertical_line(out_data[3:])
            else:
                pass
        else:
            pass
        return _pm_info
```
## 原因解释及解决方案

关于`TypeError: a bytes-like object is required, not 'str'`错误，我们可以这样复现一下：
```python
In [16]: a = b'123|456'

In [17]: a.split('|')                                                                                         
---------------------------------------------------------------------------
TypeError                                 Traceback (most recent call last)
<ipython-input-17-d4229c89bf5f> in <module>
----> 1 a.split('|')

TypeError: a bytes-like object is required, not 'str'
```
---
###  解决办法
```python
In [20]: a = b'123|456'                                                                                        
In [21]: a.decode('utf-8').split('|')                                                                         
Out[21]: ['123', '456']
```

关于问题`UnicodeDecodeError: 'utf-8' codec can't decode byte 0xb3 in position 38: invalid start byte`，主要是因为结果中有`³³³³³³³U³³³³³³³`,这个没有办法按照`utf-8`解码。
出现异常报错是由于设置了`decode()`方法的第二个参数`errors`为严格（`strict`）形式造成的，因为默认就是这个参数，将其更改为`ignore`即可。

## 参考链接
- [Python3 解决 UnicodeDecodeError: 'utf-8' codec can't decode byte..问题 终极解决方案](https://blog.csdn.net/wang7807564/article/details/78164855/)
- [TypeError: a bytes-like object is required, not 'str' when writing to a file in Python3](https://stackoverflow.com/questions/33054527/typeerror-a-bytes-like-object-is-required-not-str-when-writing-to-a-file-in)
