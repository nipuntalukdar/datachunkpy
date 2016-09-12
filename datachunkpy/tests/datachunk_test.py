#!/usr/bin/python

from __future__ import print_function
from struct import pack
import random
import unittest 

from datachunkpy.datachunk import DataChunk, MessageHandler

class MyMsgHandler(MessageHandler):
    def __init__(self):
        self.msg_processed = 0
        self.bytes_processed = 0

    def handle_msg(self, data):
        print('I am handling', data)
        self.msg_processed += 1
        self.bytes_processed += len(data)


class DatachunkTester(unittest.TestCase):
    def test_fun(self):
        mh = MyMsgHandler()
        d = DataChunk(mh)
        i = 0
        random.seed()
        mydata = b''
        total_bytes = 0
        while i < 10000:
            i += 1
            j = random.randint(1,50)
            mydata += pack('i', j)
            mydata += b'a' * j
            total_bytes += j
        d.process_chunk(mydata)
        self.assertEqual(total_bytes, mh.bytes_processed)
        self.assertEqual(i, mh.msg_processed)
    
    def test_fun_big(self):
        mh = MyMsgHandler()
        d = DataChunk(mh, False)
        i = 0
        random.seed()
        mydata = b''
        total_bytes = 0
        while i < 10000:
            i += 1
            j = random.randint(1,50)
            mydata += pack('>i', j)
            mydata += b'a' * j
            total_bytes += j
        d.process_chunk(mydata)
        self.assertEqual(total_bytes, mh.bytes_processed)
        self.assertEqual(i, mh.msg_processed)

if __name__ == '__main__':
    unittest.main()
