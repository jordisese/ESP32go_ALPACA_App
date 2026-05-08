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
            self.getBasicData()

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
        self.getStatus() # will schedule itself every time (globals.polling_seconds)
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
            #time.sleep(0.2)

    def getBasicData(self):
        try:
            #ACK
            self.clientsocket.send(b'\x06')
            time.sleep(0.1)
            bresponse=self.clientsocket.recv(2)
            response=bresponse.decode()
            #print(response)
            if response[0]=='A':
                #print('AltAz')
                globals.is_altAz.set(1)
            else:
                globals.is_altAz.set(0)
            
            #Config
            self.clientsocket.send(b':cA#')
            time.sleep(0.1)
            bresponse=self.clientsocket.recv(512)
            response=bresponse.decode('cp1252')
            #print(response)
            res = response.splitlines()
            #print(res)
            globals.longitude.set(res[11])
            globals.latitude.set(res[12])
            #print(globals.longitude.get())
            #print(globals.latitude.get())
            globals.az_count.set(res[0])
            globals.alt_count.set(res[1])

            globals.az_guide_speed.set(res[2])
            globals.alt_guide_speed.set(res[3])
            globals.az_center_speed.set(res[4])
            globals.alt_center_speed.set(res[5])
            globals.az_find_speed.set(res[6])
            globals.alt_find_speed.set(res[7])
            globals.az_slew_speed.set(res[8])
            globals.alt_slew_speed.set(res[9])

            globals.eqTrack.set(res[19])


        except TimeoutError:
            print("Timeout reading status: disconnecting socket")
            self.thread_exit()
            raise            
        except Exception as e:
            if hasattr(e, 'message'):
                print(e.message)
            else:
                print(e)
            self.thread_exit()
            raise

    def getStatus(self):
        if globals.tcp_please_disconnect:
            return
        
        if not globals.commandQueue and not globals.blindCommandQueue: #preference is given to queued commands

            try:
                # RA/DEC
                #self.clientsocket.sendall(b":GR#")
                #time.sleep(0.1)
                #bresponse=self.clientsocket.recv(11)
                #response=bresponse.decode()
                ##print(response)
                #pos=response[:2]+'h'+response[3:5]+'m'+response[6:10]+'s'
                ##print(pos)
                #globals.ra_position.set(pos)

                #self.clientsocket.sendall(b":GD#")
                #time.sleep(0.1)
                #bresponse=self.clientsocket.recv(11)
                ##print(bresponse)
                #response=bresponse.decode('cp1252')
                #pos=response[:3]+'º'+response[4:6]+'\''+response[7:9]+'"'
                ##print(pos)
                #globals.dec_position.set(pos)

                self.clientsocket.sendall(b":Gx#")
                time.sleep(0.1)
                bresponse=self.clientsocket.recv(50)
                response=bresponse.decode('cp1252')
                #print(response)

                pos=response[:2]+'h'+response[3:5]+'m'+response[6:10]+'s'
                #print(pos)
                globals.ra_position.set(pos)

                pos=response[11:14]+'º'+response[15:17]+'\''+response[18:20]+'"'
                #print(pos)
                globals.dec_position.set(pos)

                if globals.is_altAz.get()=='1':
                #if True:
                    pos=response[21:24]+'º'+response[25:27]+'\''+response[28:30]+'"'
                    #print(pos)
                    globals.az_position.set(pos)
                    pos=response[31:34]+'º'+response[35:37]+'\''+response[38:40]+'"'
                    #print(pos)
                    globals.alt_position.set(pos)
                #else:
                #    print("EQ only")

                #globals.az_position.set(response[21:29])
                #globals.alt_position.set(response[31:39])


                # extended status
                self.clientsocket.sendall(b":GU#")
                time.sleep(0.1)
                response=self.clientsocket.recv(6)
                dresponse=response.decode()
                #print(dresponse)
                if dresponse[0]=='T':
                   globals.is_tracking.set(1)
                   #print('tracking')
                else:
                    globals.is_tracking.set(0)
                    #print('not tracking')
                if dresponse[1]=='P':
                    globals.is_parked.set(1)
                else:
                    globals.is_parked.set(0)
                if dresponse[2]=='S':
                    globals.is_slewing.set(1)
                else:
                    globals.is_slewing.set(0)
                if dresponse[3]=='W':
                    globals.pierSideWest.set(1)
                else:
                    globals.pierSideWest.set(0)
                globals.track_value.set(dresponse[4])
                #print('track value:')
                #print(dresponse[4])

            except TimeoutError:
                print("Timeout reading status: disconnecting socket")
                self.thread_exit()
                raise            
            except Exception as e:
                if hasattr(e, 'message'):
                    print(e.message)
                else:
                    print(e)
                self.thread_exit()
                raise
        
        # schedule next execution
        threading.Timer(globals.polling_seconds, self.getStatus).start()


    def processCommands(self):
        if not globals.commandQueue: #empty?
            return
        try:
            cmdObj=globals.commandQueue.pop(0)
            cmd = ""
            self.clientsocket.send(cmd.encode('utf-8'))


        except TimeoutError:
            print("Timeout reading status: disconnecting socket")
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
        try:
            cmd=globals.blindCommandQueue.pop(0)
            self.clientsocket.send(cmd.encode('utf-8'))

        except TimeoutError:
            print("Timeout reading status: disconnecting socket")
            self.thread_exit()
            raise            
        except Exception as e:
            if hasattr(e, 'message'):
                print(e.message)
            else:
                print(e)
            self.thread_exit()
            raise