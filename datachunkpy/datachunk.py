#!/usr/bin/env python

from io import BytesIO
from struct import pack, unpack

class MessageHandler(object):
    '''
    Base class for message handler. handle_msg is called by DataChunk whenever
    a complete message is read
    '''

    def handle_msg(self, msg):
        '''
        handles the msg passed
        :param msg: a complete msg
        :type msg:  str
        '''
        print('Handled msg {}'.format(msg))



class DataChunk(object):
    '''
    DataChunk class is useful for proessing messages in a stream where messages are sent in
    a stream as shown below:
    <msg-size><msg-bytes><msg-size><msg-bytes><msg-size>....
    msg-size is a 4 byte integer (little-endian)
    whenever a complete message is read, DataChunk calls the handle_msg method of the handler
    '''

    def __init__(self, handler):
        '''
        Creates a DataChunk object
        :param handler: handler for a message obtained
        :type handler: MessageHandler
        '''
        self.__times = 0
        self.__expect_new = True
        self.__current_msg_len = 0
        self.__current_buffer = BytesIO()
        if handler is None:
            raise Exception('handler must not be None')
        self.__handler = handler

    def __handle_msg(self, data):
       self.__handler.handle_msg(data) 
        
    def process_chunk(self, data):
        datalen = len(data)
        if self.__expect_new:
            if datalen >= 4:
                self.__current_msg_len = unpack('i', data[0:4])[0]
                if (self.__current_msg_len + 4) == datalen:
                    # We got the entire packet 
                    self.__handle_msg(data[4:])
                    return
                elif (self.__current_msg_len + 4) > datalen:
                    # We need some more bytes
                    self.__current_buffer.write(data[4:])
                    self.__expect_new = False
                else:
                    # We may have got more than one message
                    start = 4
                    while True:
                        self.__handle_msg(data[start : start + self.__current_msg_len])
                        start = start + self.__current_msg_len
                        if start == datalen:
                            # We finished all the bytes and there is no incomplete messages
                            # in the bytes
                            self.__expect_new = True
                            self.__current_msg_len = -1
                            self.__current_buffer = BytesIO()
                            break
                        if 4 <= (datalen - start):
                            self.__current_msg_len = unpack('i', data[start : start + 4])[0]
                            start += 4
                            if (datalen - start) >= self.__current_msg_len:
                                # we have this message also in this buffer
                                continue
                            else:
                                # This message is incomplete, wait for the next chunk
                                self.__expect_new = False
                                self.__current_buffer = BytesIO()
                                self.__current_buffer.write(data[start:])
                                break
                        else:
                            # we don't even know the size of the current buffer
                            self.__current_msg_len = -1
                            self.__current_buffer = BytesIO()
                            self.__current_buffer.write(data[start:])
                            self.__expect_new = False
                            break
            else:
                # We haven't even received 4 bytes of data for this brand new 
                # packet
                self.__expect_new = False
                self.__current_buffer = BytesIO()
                self.__current_buffer.write(data)
                self.__current_msg_len = -1
        else:
            # Not a new message
            start = 0
            if self.__current_msg_len == -1:
                # try to get the message len
                if datalen >= (4 - self.__current_buffer.tell()):
                    #get the length of the data
                    start = 4 - self.__current_buffer.tell()
                    self.__current_buffer.write(data[0: start])
                    self.__current_buffer.seek(0)
                    self.__current_msg_len = unpack('i', self.__current_buffer.read())[0]
                    self.__current_buffer = BytesIO()
                else:
                    # Till now even the size of the data is not known
                    self.__current_buffer.write(data)
                    return
            while start < datalen:
                if self.__current_buffer is None:
                    self.__current_buffer = BytesIO()
                if self.__current_msg_len == -1:
                    if (datalen - start) < 4:
                        self.__current_buffer.write(data[start:])
                        break
                    elif (datalen - start) == 4:
                        self.__current_msg_len = unpack('i', data[start:])[0]
                        break
                    else:
                        self.__current_msg_len = unpack('i', data[start: start + 4])[0]
                        start += 4
                if (datalen - start) >= (self.__current_msg_len - self.__current_buffer.tell()):
                    consume = self.__current_msg_len -  self.__current_buffer.tell()
                    self.__current_buffer.write(data[start: start + consume])
                    start += consume
                    self.__current_msg_len = - 1
                    self.__current_buffer.seek(0)
                    self.__handle_msg(self.__current_buffer.read())
                    self.__current_buffer = BytesIO()
                    if start == datalen:
                        self.__expect_new = True
                else:
                    self.__current_buffer.write(data[start:])
                    break

