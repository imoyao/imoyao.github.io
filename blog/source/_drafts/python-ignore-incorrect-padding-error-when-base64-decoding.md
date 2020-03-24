---
title: python-ignore-incorrect-padding-error-when-base64-decoding
date: 2020-03-24 20:53:23
tags:
categories:
---

```python
import json
import base64


class Bytes2JsonEncoder(json.JSONEncoder):
    """
    解决：TypeError: Object of type bytes is not JSON serializable
    """

    def default(self, obj):
        if isinstance(obj, bytes):
            return str(obj, encoding='utf-8')
        return json.JSONEncoder.default(self, obj)


class B64Crypty:
    """
    密码混淆与反混淆
    """

    def __init__(self):
        pass

    @staticmethod
    def b64encode(plain_text):
        return base64.b64encode(plain_text.encode())

    @staticmethod
    def pw_decode(cipher_text):
        return base64.b64decode(cipher_text).decode()

    @staticmethod
    def b64decode_wrap(cipher_text):
        """
        # 解决问题：python-ignore-incorrect-padding-error-when-base64-decoding
        
        Wrapper for base64.b64decode
        - Expects Base64 encoded ASCII data as input argument cipher_text
        - Returns decoded data as bytes object
        - Expects cipher_text uses standard Base64 place-values:  A-Z; a-z; 0-9; +; /.
        - Robust to missing Base64 encoded characters
          - Will not return original data in this case
        - Not necessarily robust to corrupted characters in cipher_text
        - Throws MISSING_B64_NOT_ASCII exception if cipher_text contains non-ASCII
          characters; implemented via bytes.decode and/or str.encode
        """
        try:
            # Ensure argument is either bytes ASCII or str ASCII
            if isinstance(cipher_text, bytes):
                arg_string = cipher_text.decode('ASCII')
            elif isinstance(cipher_text, str):
                arg_string = cipher_text.encode().decode('ASCII')
            else:
                assert False
        except Exception:
            raise exceptions.MISSING_B64_NOT_ASCII(
                'Method missing_b64.b64decode Base64 encoded argument is neither ASCII bytes nor ASCII str')

        try:
            # Remove any = chars, and try padding with two =s
            # - This will work with (len(cipher_text') % 4) of 0, 2 or 3
            #  - cipher_text' is cipher_text with all non-Base64-standard-place-values removed
            decode_ret = base64.b64decode(arg_string.replace('=', '') + '==')

        except base64.binascii.Error as e:
            # If that failed, padd with A==
            # - This will work with (len(cipher_text') % 4) of 1
            decode_ret = base64.b64decode(arg_string.replace('=', '') + 'A==')

        except Exception:
            # Execution should never get here
            raise

        if isinstance(decode_ret, bytes):  # for py3
            return decode_ret.encode()
        else:
            return decode_ret
```
## 参考链接
[Python: Ignore 'Incorrect padding' error when base64 decoding - Stack Overflow](https://stackoverflow.com/questions/2941995/python-ignore-incorrect-padding-error-when-base64-decoding)