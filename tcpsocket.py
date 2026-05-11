#
# tcpsocket.py - TCP process to ESP32go
#

import globals
#import os
import sys
import socket
import time
import threading
from threading import Thread                            

class TCPconnection(Thread):
    """TCP connection to ESP32go"""

    #clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #clientsocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    #clientsocket.settimeout(5)
    clientsocket = None

    def __init__(self, ADDR, PORT):
        Thread.__init__(self, name='TCPconnToESP32go')
        try:
            #self.clientsocket.connect(('192.168.1.21', 10001))
            #self.clientsocket.connect((ADDR, PORT))
            self.clientsocket = socket.create_connection((ADDR, PORT),5)
            #self.getBasicData()

        except TimeoutError:
            globals.connect_disconnect.set('Connect')
            globals.connect_status.set('Disconnected')
            print('TCPconnToESP32go: failure to connect to ESP32go')
            globals.connection_error = True
            self.clientsocket.close()
            self.clientsocket = 0
            raise
        globals.tcp_connected=True
        globals.connect_disconnect.set('Disconnect')
        globals.connected_status.set('Connected [TCP]')
        globals.connect_status.set('')
        self.daemon=True
        self.start()

    def thread_exit(self):
        globals.comLock=False
        globals.tcp_connected=False
        globals.connect_disconnect.set('Connect')
        globals.connect_status.set('Disconnected')
        globals.connected_status.set('')
        if self.clientsocket != None:
            self.clientsocket.shutdown(socket.SHUT_RDWR)
            self.clientsocket.close()
        self.clientsocket = None
        print('destroying class')
        sys.exit()
    
    def run(self):
        print("tcp thread RUN active")
        globals.blindCommandQueue = [] #empty queue just in case
        globals.commandQueue = {} #empty queue just in case
        globals.comLock=False

        #self.getStatus() # will schedule itself every time (globals.polling_seconds)
        #threading.Timer(globals.polling_seconds, self.getStatus).start()
        while True:
            if globals.tcp_please_disconnect:
                print("Thread exit requested")
                self.thread_exit()
                return
            try:
                self.processBlindCommands()
                self.processCommands()
                time.sleep(0.1) #needed!!!
            except:
                print("RunException: Closing thread")
                self.thread_exit()
                return


    def processCommands(self):
        if not globals.commandQueue: #empty?
            return
        if globals.comLock:
            return
        globals.comLock=True
        try:
            key=next(iter(globals.commandQueue))
            cmd = globals.commandQueue.pop(key)
            maxbytes = globals.commandQueueBytes.pop(key,0)
            #print('command['+cmd+']')
            if isinstance(cmd, (bytes, bytearray)):
                self.clientsocket.send(cmd)
            else:
                self.clientsocket.send(cmd.encode('utf-8'))
            time.sleep(0.1)
            response = ''
            if maxbytes > 0:
                bresponse=self.clientsocket.recv(maxbytes)
                # decoding fallback if needed
                try:
                    response=bresponse.decode('')
                except Exception as e:
                    response=bresponse.decode('cp1252')
                #print('maxbytes['+str(maxbytes)+']['+response+']')
            else:
                r = ''
                count = 0
                while r != '#' or count > 256:
                    br = self.clientsocket.recv(1)
                    #print(br)
                    try:
                        r=br.decode('')
                    except Exception as e:
                        r=br.decode('cp1252') #
                    response += r
                    count += 1
                #print('response['+response+']')
            globals.responseQueue[key]=response
            globals.comLock=False
        except TimeoutError:
            print("Timeout processing commandQueue["+cmd+"]: disconnecting socket")
            self.thread_exit()
            raise            
        except Exception as e:
            if hasattr(e, 'message'):
                print(e.message)
            else:
                print(e)
            self.thread_exit()
            raise


    def processBlindCommands(self):
        if not globals.blindCommandQueue: #empty?
            return
        if globals.comLock:
            return
        try:
            globals.comLock=True
            cmd=globals.blindCommandQueue.pop(0)
            if cmd == 'FLUSH': #special command, empty buffer
                self.clientsocket.send(b':Gc#')   
                time.sleep(0.1) 
                self.clientsocket.recv(1024)
                globals.comLock=False
                return

            if isinstance(cmd, (bytes, bytearray)):
                self.clientsocket.send(cmd)
            else:
                self.clientsocket.send(cmd.encode('utf-8'))
            time.sleep(0.1) 
            globals.comLock=False

        except TimeoutError:
            print("Timeout processing commandBlindQueue["+cmd+"]: disconnecting socket")
            self.thread_exit()
            raise            
        except Exception as e:
            if hasattr(e, 'message'):
                print(e.message)
            else:
                print(e)
            self.thread_exit()
            raise
