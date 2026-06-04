"""
火山引擎 RTC AccessToken
"""
import base64
import hmac
import random
import struct
import time
from collections import OrderedDict
from hashlib import sha256

VERSION = '001'
VERSION_LENGTH = 3
APP_ID_LENGTH = 24

PrivPublishStream = 0
privPublishAudioStream = 1
privPublishVideoStream = 2
privPublishDataStream = 3
PrivSubscribeStream = 4


class AccessToken:
    def __init__(self, app_id, app_key, room_id, user_id):
        random.seed(time.time())
        self.app_id = app_id
        self.app_key = app_key
        self.room_id = room_id
        self.user_id = user_id
        self.issued_at = int(time.time())
        self.nonce = random.randint(1, 99999999)
        self.expire_at = 0
        self.privileges = {}
        self.signature = b''

    def add_privilege(self, privilege, expire_ts):
        if self.privileges is None:
            self.privileges = {}
        self.privileges[privilege] = expire_ts
        if privilege == PrivPublishStream:
            self.privileges[privPublishVideoStream] = expire_ts
            self.privileges[privPublishAudioStream] = expire_ts
            self.privileges[privPublishDataStream] = expire_ts

    def expire_time(self, expire_ts):
        self.expire_at = expire_ts

    def pack_msg(self):
        m = pack_uint32(self.nonce)
        m += pack_uint32(self.issued_at)
        m += pack_uint32(self.expire_at)
        m += pack_string(self.room_id)
        m += pack_string(self.user_id)
        m += pack_map_uint32(self.privileges)
        return m

    def serialize(self):
        m = self.pack_msg()
        signature = hmac.new(self.app_key.encode('utf-8'), m, sha256).digest()
        content = pack_bytes(m) + pack_bytes(signature)
        return VERSION + self.app_id + base64.b64encode(content).decode('utf-8')

    def verify(self):
        if 0 < self.expire_at < int(time.time()):
            return False
        return (
            hmac.new(self.app_key.encode('utf-8'), self.pack_msg(), sha256).digest()
            == self.signature
        )


def parse(raw, app_key=None):
    try:
        if len(raw) <= VERSION_LENGTH or raw[:VERSION_LENGTH] != VERSION:
            return None
        token = AccessToken('', app_key or '', '', '')
        token.app_id = raw[VERSION_LENGTH:VERSION_LENGTH + APP_ID_LENGTH]
        content_buf = base64.b64decode(raw[VERSION_LENGTH + APP_ID_LENGTH:])
        readbuf = ReadByteBuffer(content_buf)
        msg = readbuf.unpack_bytes()
        token.signature = readbuf.unpack_bytes()
        msgbuf = ReadByteBuffer(msg)
        token.nonce = msgbuf.unpack_uint32()
        token.issued_at = msgbuf.unpack_uint32()
        token.expire_at = msgbuf.unpack_uint32()
        token.room_id = msgbuf.unpack_string()
        token.user_id = msgbuf.unpack_string()
        token.privileges = msgbuf.unpack_map_uint32()
        if app_key:
            token.app_key = app_key
        return token
    except Exception:
        return None


def create_rtc_token(app_id, app_key, room_id, user_id, expire_hours):
    token = AccessToken(app_id, app_key, room_id, user_id)
    expire = int(time.time()) + 3600 * int(expire_hours)
    token.add_privilege(PrivSubscribeStream, 0)
    token.add_privilege(PrivPublishStream, expire)
    token.expire_time(expire)
    return token.serialize()


def pack_uint16(x):
    return struct.pack('<H', int(x))


def pack_uint32(x):
    return struct.pack('<I', int(x))


def pack_string(string):
    return pack_bytes(string.encode('utf-8'))


def pack_bytes(b):
    return pack_uint16(len(b)) + b


def pack_map_uint32(m):
    m = OrderedDict(sorted(m.items(), key=lambda x: int(x[0])))
    ret = pack_uint16(len(m.items()))
    for k, v in m.items():
        ret += pack_uint16(k) + pack_uint32(v)
    return ret


class ReadByteBuffer:
    def __init__(self, data):
        self.buffer = data
        self.position = 0

    def unpack_uint16(self):
        length = struct.calcsize('H')
        buff = self.buffer[self.position:self.position + length]
        ret = struct.unpack('<H', buff)[0]
        self.position += length
        return ret

    def unpack_uint32(self):
        length = struct.calcsize('I')
        buff = self.buffer[self.position:self.position + length]
        ret = struct.unpack('<I', buff)[0]
        self.position += length
        return ret

    def unpack_string(self):
        return self.unpack_bytes().decode('utf-8')

    def unpack_bytes(self):
        strlen = self.unpack_uint16()
        buff = self.buffer[self.position:self.position + strlen]
        ret = struct.unpack('<' + str(strlen) + 's', buff)[0]
        self.position += strlen
        return ret

    def unpack_map_uint32(self):
        messages = {}
        maplen = self.unpack_uint16()
        for _ in range(maplen):
            key = self.unpack_uint16()
            value = self.unpack_uint32()
            messages[key] = value
        return messages
