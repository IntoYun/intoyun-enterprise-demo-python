#!/usr/bin/env python
# -*- coding: utf-8 -*-

__all__ = ['Kafka']

import json
import base64
import binascii
import struct
import hashlib
from Crypto import Random
from Crypto.Cipher import AES
from handlers.websocket import WebsocketHandler


WIFI_INFO_CODE = 11
GW_INFO_CODE   = 12
LORA_INFO_CODE = 13
TCP_INFO_CODE  = 14
WIFI_RX_CODE   = 21
GW_RX_CODE     = 22
LORA_RX_CODE   = 23
TCP_RX_CODE    = 24
HTTP_INFO_CODE = 30

BS = 16
pad = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS)
unpad = lambda s : s[0:-ord(s[-1])]

def b(n):
    return n*2

def parse_data(message, aes_key):
    print "==> receive crude message: ", message
    jsonData = json.loads(message)
    code     = jsonData['code']
    ts       = jsonData['ts']
    sign     = jsonData['sign']
    body     = jsonData['body']
    mic      = hashlib.md5(body).hexdigest()
    if mic == sign:
        base64_decoded_msg = base64.b64decode(body)
        iv = base64_decoded_msg[:AES.block_size]
        encoded_payload = base64_decoded_msg[16:]
        cipher = AES.new(aes_key, AES.MODE_CBC, iv)
        decoded_payload = unpad(cipher.decrypt(encoded_payload))
        if (code==WIFI_INFO_CODE)or(code==GW_INFO_CODE)or(code==LORA_INFO_CODE)or(code==TCP_INFO_CODE):
            info_msg = {}
            info_msg['code'] = code
            info_msg['ts'] = ts
            info_msg['sign'] = sign
            info_msg['body'] = parse_info_data(decoded_payload)

            print "==> receive info message"
            print "==> there are {} anonymouses".format(len(WebsocketHandler.anonymous))
            print "==> there are {} kinds of devices".format(len(WebsocketHandler.trusted))
            devId = info_msg['body']['devId']
            subs = WebsocketHandler.anonymous
            if len(subs)>0:
                for cli in subs:
                    cli.write_message(json.dumps(info_msg))

        elif (code==WIFI_RX_CODE)or(code==GW_RX_CODE)or(code==LORA_RX_CODE)or(code==TCP_RX_CODE):
            rx_msg = {}
            rx_msg['code'] = code
            rx_msg['ts'] = ts
            rx_msg['sign'] = sign
            rx_msg['body'] = parse_rx_data(decoded_payload)

            print "==> receive data message"
            print "==> there are {} anonymouses".format(len(WebsocketHandler.anonymous))
            print "==> there are {} kinds of devices".format(len(WebsocketHandler.trusted))
            devId = rx_msg['body']['devId']
            subs = WebsocketHandler.anonymous
            if len(subs)>0:
                for cli in subs:
                    cli.write_message(json.dumps(rx_msg))

        elif (code==HTTP_INFO_CODE):
            jsonData['body'] = json.loads(decoded_payload)
            print "==> receive http info message"
            print "==> there are {} anonymouses".format(len(WebsocketHandler.anonymous))
            print "==> there are {} kinds of devices".format(len(WebsocketHandler.trusted))
            subs = WebsocketHandler.anonymous
            if len(subs)>0:
                for cli in subs:
                    cli.write_message(json.dumps(jsonData))


def parse_info_data(payload):
    info_data = {}
    try:
        info = json.loads(payload)
        info_data['prdId'] = info['prdId']
        info_data['devId']  = info['devId']
        info_data['ipaddr'] = info['ipaddr']
        info_data['data']   = json.loads(base64.b64decode(info['data']))
        if info.get('gwId') != None:
            info_data['gwId'] = info['gwId']
        if info.get('rssi') != None:
            info_data['rssi'] = info['rssi']
    except Exception as e:
        print "Error: ", e
    return info_data

def parse_rx_data(payload):
    rx_data = {}
    # print "payload: ", payload
    try:
        rx = json.loads(payload)
        rx_data['devId'] = rx['devId']
        rx_data['stoId'] = rx['stoId']
        rx_data['data']  = parse_rx_dps(base64.b64decode(rx['data']))
        if rx.get('prdId') != None: # gateway的rx消息没有productId
            rx_data['prdId'] = rx['prdId']
        if rx.get('gwId') != None:  # 非lora节点没有
            rx_data['gwId'] = rx['gwId']
        if rx.get('rssi') != None:  # 非lora节点没有
            rx_data['rssi'] = rx['rssi']
    except Exception as e:
        print "Error: ", e
    return rx_data

def parse_rx_dps(data):
    if data[:1] == '1':
        dps = {}
        dpsdata = data[1:]
        payloadBytes = binascii.hexlify(data)
        try:
            dps = parse_dp(dps, payloadBytes[b(1):])
        except Exception as e:
            print "Error: ", e
            dps = {0: data}
        return dps
    else:                       # dataformat=custom的数据可以使用数据点0表示，内容是所有数据
        return {0: data}

def parse_dp(dps, binStr):
    if binStr != "":
        dpId, rest0 = get_dpId(binStr)
        dpTyp, rest1 = get_dpType(rest0)
        dpLen, rest2 = get_dpLen(rest1)
        dpVal, rest3 = get_value(dpTyp, dpLen, rest2)
        dps[dpId] = dpVal
        return parse_dp(dps, rest3)
    else:
        return dps

def get_dpId(binStr):
    dpId0 =  int(binStr[:b(1)], 16)
    if dpId0 > 127 :
        dpId = int(binStr[:b(2)], 16) - 0x8000
        return (dpId, binStr[b(2):])
    else:
        return (dpId0,binStr[b(1):])

def get_dpType(binStr):
    dpTyp = int(binStr[:b(1)], 16)
    return (dpTyp, binStr[b(1):])

def get_dpLen(binStr):
    length0 =  int(binStr[:b(1)], 16)
    if length0 > 127 :
        length = int(binStr[:b(2)], 16) - 0x8000
        return (length, binStr[b(2):])
    else:
        return (length0, binStr[b(1):])

def get_value(dpTyp, dpLen, binStr):
    if dpTyp == 0:
          if int(binStr[:b(1)], 16) == 0:
              return (False, binStr[b(1):])
          elif int(binStr[:b(1)], 16) == 1:
              return (True, binStr[b(1):])
    elif dpTyp == 1:
        return (int(binStr[:b(dpLen)], 16), binStr[b(dpLen):])
    elif dpTyp == 2:
        return (int(binStr[:b(1)], 16), binStr[b(1):])
    elif dpTyp == 3:
        return (binascii.unhexlify(binStr[:b(dpLen)]), binStr[b(dpLen):])
    elif dpTyp == 4:
        return (binascii.unhexlify(binStr[:b(dpLen)]), binStr[b(dpLen):])
    else:
        print "unsupported type."


from kafka import KafkaConsumer
from tornado.concurrent import run_on_executor
from concurrent.futures import ThreadPoolExecutor
from configs.kafka import config
from configs.intoyun import ityConf

class Kafka(object):
    executor = ThreadPoolExecutor(max_workers=2)

    @run_on_executor()
    def consume(self):
        broker = config["HOST"] + ":" + config["PORT"]
        appId = ityConf["APP_ID"]
        appSecret = ityConf["APP_SECRET"]

        topic = "device-data-" + appId

        m0 = hashlib.md5()
        m0.update(appSecret)
        m1 = hashlib.md5()
        m1.update(appId+m0.hexdigest())
        password = m1.hexdigest()
        consumer = KafkaConsumer(topic,
                                bootstrap_servers=broker,
                                api_version = (0, 10),
                                security_protocol='SASL_PLAINTEXT',
                                auto_offset_reset='earliest',
                                group_id=appId,
                                sasl_mechanism='PLAIN',
                                sasl_plain_username=appId,
                                sasl_plain_password=password
        )
        aes_key = appSecret.decode("hex")
        for msg in consumer:
            parse_data(msg.value, aes_key)
