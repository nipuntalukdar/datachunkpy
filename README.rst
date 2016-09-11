Datachunkpy
============
DataChunk is an useful library for proessing messages in a stream where messages are sent in
a stream as shown below:
<msg-size><msg-bytes><msg-size><msg-bytes><msg-size>....
msg-size is a 4 byte integer (little-endian)
whenever a complete message is read, DataChunk calls the handle_msg method of the handler.

A message may come in fragments. Sometimes many messages may come in a single data packet. 
All we need to do is to call process_chunk method of DataChunk and DataChunk object will take care 
of re-assembling the messages as and when needed.


Basic example
-------------


    .. code:: python

        from __future__ import print_function
        from struct import pack
        import random
        from datachunkpy.datachunk import DataChunk, MessageHandler

        # A message handler class 
        class MyMsgHandler(MessageHandler):
            def __init__(self):
                self.msg_processed = 0
                self.bytes_processed = 0

            def handle_msg(self, data):
                print('I am handling', data)
                self.msg_processed += 1
                self.bytes_processed += len(data)

        
        datach = DataChunk(MyMsgHandler())

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
        datach.process_chunk(mydata)

