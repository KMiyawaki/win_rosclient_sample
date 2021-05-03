# -*- coding: utf_8 -*-
import json
import socket
import select
import time
from ros_utils import bson_serialize
from json.decoder import WHITESPACE


class RosBridgeTCP(object):
    def __init__(self, ip='127.0.0.1', port=9090, bufsize=4096, select_timeout=0.005, bson_only=False):
        self.serv_address = (ip, port)
        self.bufsize = bufsize
        self.select_timeout = select_timeout
        self.recv_data = []
        self._id_counter = 0
        self.sock = None
        # bson_only has SERIOUS RISK. It cannot send floating point numbers
        self.bson_only = bson_only
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect(self.serv_address)
            self.sock.setblocking(False)
        except Exception as e:
            print(str(e))
            self.sock = None

    def terminate(self):
        if self.sock is not None:
            self.sock.close()
            self.sock = None

    @property
    def is_connected(self):
        return self.sock is not None

    @property
    def id_counter(self):
        self._id_counter += 1
        return self._id_counter

    def send_message(self, message):
        try:
            if self.bson_only:
                return self.sock.send(bson_serialize(message))
            else:
                return self.sock.send(json.dumps(message).encode())
        except Exception as e:
            print(str(e))
            return 0

    def get_recv_data(self):
        return self.recv_data

    def flush(self, time=1):
        tm = time.time()
        while time.time() - tm < time:
            self.wait()
            time.sleep(0.2)

    def wait(self):
        self.recv_data = []
        try:
            readfds = set([self.sock])
            rready, _, _ = select.select(readfds, [], [], self.select_timeout)
            for sock in rready:
                if sock != self.sock:
                    print("Warning: UnKnow socket")
                else:
                    data, _ = self.sock.recvfrom(self.bufsize)
                    text = data.decode()
                    jsons = list(self.loads_iter(text))
                    for j in jsons:
                        self.recv_data.append(dict(j))
        except Exception as e:
            print(str(e))
            return 0
        return self.get_recv_data()

    def loads_iter(self, s):
        size = len(s)
        decoder = json.JSONDecoder()

        end = 0
        while True:
            idx = WHITESPACE.match(s[end:]).end()
            i = end + idx
            if i >= size:
                break
            ob, end = decoder.raw_decode(s, i)
            yield ob

    def check_messages(self, messages, target_words=None):
        for m in messages:
            msg_data = m['msg']['data']
            if target_words is None:
                return msg_data

            for target in target_words:
                if target in msg_data:
                    return msg_data
        return None

    def wait_response(self, publish_msg=None, target_words=None, timeout=None, publish_rate=1):
        sleep_time = 1 / publish_rate
        tm = time.time()
        message = None
        while message is None:
            if timeout is not None and time.time() - tm >= timeout:
                return None
            if publish_msg is not None:
                self.send_message(publish_msg)
                print("Sending ros message: " + str(publish_msg))
                time.sleep(sleep_time)
            message = self.check_messages(self.wait(), target_words)
        return message
