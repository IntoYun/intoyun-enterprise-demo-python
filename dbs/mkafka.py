#!/usr/bin/env python
# -*- coding: utf-8 -*-

__all__ = ['Kafka']


CONN_NOTF_CODE = 10
WIFI_INFO_CODE = 11
GW_INFO_CODE   = 12
LORA_INFO_CODE = 13
TCP_INFO_CODE  = 14
WIFI_RX_CODE   = 21
GW_RX_CODE     = 22
LORA_RX_CODE   = 23
TCP_RX_CODE    = 24
HTTP_INFO_CODE = 30

TLV_BOOL  = 0 # 布尔型
TLV_NUM   = 1 # 数值型
TLV_ENUM  = 2 # 枚举型
TLV_STR   = 3 # 字符型
TLV_EXTRA = 4 # 扩展型


from utils.mcodec import Codec

def b(n):
    return n*2

def parse_rx_dps(data):
    realData = data[1:] # ignore the first byte which represent itself as tlv-format
    hexData = Codec.encHex(realData)
    try:
        return parse_dp({}, hexData)
    except Exception as e:
        print "==> parse_dp Error: ", e

def parse_dp(dps, hexData):
    if hexData != "":
        dpId,  rest = get_dpId(hexData)
        dpTyp, rest = get_dpType(rest)
        dpLen, rest = get_dpLen(rest)
        dpVal, rest = get_value(dpTyp, dpLen, rest)
        dps[dpId] = dpVal
        return parse_dp(dps, rest)
    else:
        return dps

def get_dpId(hexData):
    dpId = int(hexData[:b(1)], 16)
    if dpId > 127:
        dpId = int(hexData[:b(2)], 16) - 0x8000
        return (dpId, hexData[b(2):])
    else:
        return (dpId, hexData[b(1):])

def get_dpType(hexData):
    dpTyp = int(hexData[:b(1)], 16)
    return (dpTyp, hexData[b(1):])

def get_dpLen(hexData):
    length =  int(hexData[:b(1)], 16)
    if length > 127 :
        length = int(hexData[:b(2)], 16) - 0x8000
        return (length, hexData[b(2):])
    else:
        return (length, hexData[b(1):])

def get_value(dpTyp, dpLen, hexData):
    if dpTyp == TLV_BOOL:
          if int(hexData[:b(1)], 16) == 0:
              return (False, hexData[b(1):])
          elif int(hexData[:b(1)], 16) == 1:
              return (True, hexData[b(1):])
    elif dpTyp == TLV_NUM:
        return (int(hexData[:b(dpLen)], 16), hexData[b(dpLen):])
    elif dpTyp == TLV_ENUM:
        return (int(hexData[:b(1)], 16), hexData[b(1):])
    elif dpTyp == TLV_STR:
        return (Codec.decHex(hexData[:b(dpLen)]), hexData[b(dpLen):])
    elif dpTyp == TLV_EXTRA:
        return (Codec.decHex(hexData[:b(dpLen)]), hexData[b(dpLen):])
    else:
        print "==> Error: unsupported tlv-type."


from kafka import KafkaConsumer
from tornado.concurrent import run_on_executor
from tornado.ioloop import IOLoop
from concurrent.futures import ThreadPoolExecutor
from handlers.websocket import WebsocketHandler
from utils.client import Httpc
from utils.logger import log
from configs.kafka import config
from configs.intoyun import ityConf

class Kafka(object):
    executor = ThreadPoolExecutor(max_workers=2)
    IntoYunPrdDict = dict()
    prdFetched = False

    def __init__(self):
        if not Kafka.prdFetched:
            log.info("==> init Kafka...")
            code, body = Httpc.fetchSync("/v1/product", "GET")
            if code > 300:
                log.warning("==> Can't fetch product info. Exit!!!")
                IOLoop.current().stop()

            prdDict = dict()
            for prd in Codec.decJson(body):
                prdDict[prd['productId']] = prd['dataformat']

            Kafka.IntoYunPrdDict = prdDict
            Kafka.prdFetched = True

    @classmethod
    def parse_conn_data(cls, payload):
        try:
            conn = Codec.decJson(payload)
            conn['data'] = Codec.decJson(Codec.decBase64(conn['data']))
        except Exception as e:
            print "==> parse conn data Error: ", e
        return conn

    @classmethod
    def parse_info_data(cls, payload):
        try:
            info = Codec.decJson(payload)
            info['data'] = Codec.decJson(Codec.decBase64(info['data']))
        except Exception as e:
            print "==> parse info data Error: ", e
        return info

    @classmethod
    def parse_rx_data(cls, payload):
        try:
            rx = Codec.decJson(payload)
            if cls.IntoYunPrdDict[rx['prdId']] == "tlv":
                rx['data'] = parse_rx_dps(Codec.decBase64(rx['data']))
        except Exception as e:
            print "==> parse rx data Error: ", e
        return rx


    @classmethod
    def parse_data(cls, message, aes_key):
        print "==> receive crude message: ", message
        msgDict = Codec.decJson(message)
        code    = msgDict['code']
        ts      = msgDict['ts']
        body    = msgDict['body']

        if Codec.md5(body) == msgDict['sign']:
            data = Codec.decAesCBC(Codec.decBase64(body), aes_key)
            print "==> decode its 'body' field: ", data

            if (code==CONN_NOTF_CODE):
                msgConn = {'type':"conn", 'code': code, 'ts':ts, 'body':cls.parse_conn_data(data)}
                msgConn = Codec.encJson(msgConn)
                for cli in WebsocketHandler.anonymous:
                    cli.write_message(msgConn)
            elif (code==WIFI_INFO_CODE)or(code==GW_INFO_CODE)or(code==LORA_INFO_CODE)or(code==TCP_INFO_CODE):
                msgInfo = {'type':"info", 'code': code, 'ts':ts, 'body':cls.parse_info_data(data)}
                msgInfo = Codec.encJson(msgInfo)
                for cli in WebsocketHandler.anonymous:
                    cli.write_message(msgInfo)
            elif (code==WIFI_RX_CODE)or(code==GW_RX_CODE)or(code==LORA_RX_CODE)or(code==TCP_RX_CODE):
                msgRx = {'type':"rx", 'code': code, 'ts':ts, 'body':cls.parse_rx_data(data)}
                msgRx = Codec.encJson(msgRx)
                for cli in WebsocketHandler.anonymous:
                    cli.write_message(msgRx)
            elif (code==HTTP_INFO_CODE):
                info = Codec.decJson(data)
                if info['resource'] == 'product':
                    prdId = info['meta']['id']
                    if info['action'] == "DELETE":
                        del cls.IntoYunPrdDict[prdId]
                    else:
                        code, body = Httpc.fetchSync("/v1/product/"+prdId, "GET")
                        if code > 300:
                            print "==> Httpc Error: ", body
                        else:
                            cls.IntoYunPrdDict[prdId] = Codec.decJson(body)['dataformat']
        else:
            print "==> incorrect sign, drop this message!"


    @run_on_executor()
    def consume(self):
        broker = config["HOST"] + ":" + config["PORT"]
        appId = ityConf["APP_ID"]
        appSecret = ityConf["APP_SECRET"]
        password = Codec.md5(appId+Codec.md5(appSecret))

        topic = "device-data-" + appId
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
            self.parse_data(msg.value, aes_key)
