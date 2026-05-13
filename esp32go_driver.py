# management of functions called from alpaca driver

import globals
from tkinter import messagebox 

#import config
from config import Config
import tcpsocket
from tcpsocket import TCPconnection
import datetime
import time
import math

class esp32go_driver:

    _TCP = None

    #--- is connected ?
    def connected(self):
        return globals.tcp_connected

    def connect(self, blind=True):
        globals.connect_picgotoLevel.set('')
        self.tcp_connect(blind=blind)
        print("picGotoLevel["+str(globals.picGotoLevel)+"]")
        match globals.picGotoLevel:
            case 2:
                globals.connect_picgotoLevel.set('PicGoto Mode (very limited)')
            case 1:
                globals.connect_picgotoLevel.set('FW outdated: Please update ESP32go')
        self.initDateTime()

    def disconnect(self):
        globals.connect_picgotoLevel.set('')
        return self.tcp_disconnect()
    
    def connect_disconnect(self, action:bool):
        if action and self.connected():
            return # already connected
        if not action and not self.connected():
            return # already disconnected
        if action:
            self.connect()
        else:
            self.disconnect()

    def tcp_connect(self, blind=True):
        if globals.connect_disconnect.get() == 'Disconnect' or globals.tcp_connected:
            globals.connect_disconnect.set('Connect')
            self.tcp_disconnect()
            return

        globals.tcp_please_disconnect=False

        try:
            self._TCP = tcpsocket.TCPconnection(Config.esp32go_ip_address,Config.esp32go_port)

            self.getBasicData()


        except Exception as e:
            print("Exception connecting to ESP32go")
            if hasattr(e, 'message'):
                print(e.message)
            else:
                print(e)

            if globals.connection_error == True:
                globals.connection_error = False
                if not blind:
                    messagebox.showerror("Error", "Connection failed")

    def tcp_disconnect(self):
        globals.tcp_please_disconnect=True #thread will exit ASAP


    #--- command queues

    def sendCommand(self,cmd:str):
        #print(cmd)
        if not globals.tcp_connected:
            return
        globals.blindCommandQueue.append(cmd)

    def flush(self):
        if not globals.tcp_connected:
            return
        self.sendCommand(cmd='FLUSH')  

    def generateId(self):
        import random
        import string
        length = 8
        random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=length))
        return random_string

    def sendCommandWaitReply(self,cmd:str,maxbytes=0,captureTimeout=False):
        import time
        response = ''
        timeout = 5 
        #print(cmd)
        if not globals.tcp_connected:
            return
        cmdId=self.generateId()
        if maxbytes > 0:
            globals.commandQueueBytes[cmdId]=maxbytes
        if captureTimeout:
            globals.commandCaptureTimeout[cmdId]=True

        globals.commandQueue[cmdId]=cmd
        #print('self.sendCommandWaitReply['+cmd+']')
        start = time.time()
        while time.time() < (start + timeout):
            if cmdId in globals.responseQueue:
                response=globals.responseQueue.pop(cmdId)
                #print('response in '+str(time.time()-start)+' seconds')
                #print(response)
                return response
        return response
    
    #--- command values
    def speed_cmd(self):
        speed=globals.speed_value.get()
        match speed:
            case '0': #guide
                return ":RG#"
            case '1': #slew
                return ":RS#"
            case '2': #find
                return ":RM#"
            case '3': #center
                return ":RC#" 
        # just in case        
        return ":RF#"

    #--- commands
    def setMoveSpeed(self,rate:int):
        print("setMoveSpeed["+str(rate)+"]")
        rate = abs(int(rate))
        if rate > 3:
            rate = 3
        globals.speed_value.set(rate)

    def speed_move(self, dir:str):
        speed=self.speed_cmd()
        match dir:
            case 'N':
                self.sendCommand(cmd=speed+":Mn#")
            case 'S':
                self.sendCommand(cmd=speed+":Ms#")
            case 'E':
                self.sendCommand(cmd=speed+":Me#")
            case 'W':
                self.sendCommand(cmd=speed+":Mw#")


    def move(self, dir:str):
        match dir:
            case 'N':
                self.sendCommand(cmd=":Mn#")
            case 'S':
                self.sendCommand(cmd=":Ms#")
            case 'E':
                self.sendCommand(cmd=":Me#")
            case 'W':
                self.sendCommand(cmd=":Mw#")

    def stop(self, dir:str=''):
        match dir:
            case 'N':
                self.sendCommand(cmd=":Qn#")
            case 'S':
                self.sendCommand(cmd=":Qs#")
            case 'E':
                self.sendCommand(cmd=":Qe#")
            case 'W':
                self.sendCommand(cmd=":Qw#")
            case _:
                self.sendCommand(cmd=":Q#")

    def goHome(self):
        self.sendCommand(cmd=":hP#")
    
    def resetHome(self):
        self.sendCommand(cmd=":pH#")

    def pulseguide(self,direction,interval):
        self.sendCommand(cmd=":Mg"+direction+str(interval)+"#")

    def setTrackingRate(self,rate:int): #rate is alpaca value
        if globals.picGotoLevel > 0: # not supported in older FW versions
            return
        
        match rate:
            case 0: # sideral
                self.sendCommand(cmd=":TQ#")
            case 1: # lunar
                self.sendCommand(cmd=":TL#")
            case 2: # solar
                self.sendCommand(cmd=":TS#")
            case 3: # king
                self.sendCommand(cmd=":TK#")
            case _:
                self.sendCommand(cmd=":TQ#")


    def getAlignmentMode(self):
        if globals.is_altAz.get()==1:
            return 0 #AltAz
        return 2 # germanPolar
    
    def getAltitude(self,raw=False):
        if raw:
            return globals.alt_position.get()
        # alpaca format (float)
        rawvalue=globals.alt_position.get()
        alt = self.signedDegToFloat(rawvalue)
        return alt

    def getAzimuth(self,raw=False):
        if raw:
            return globals.az_position.get()
        # alpaca format (float)
        rawvalue=globals.az_position.get()
        az = self.unsignedDegToFloat(rawvalue)
        return az
   
    def getZeroValue(self):
        return 0
    
    def getIsParked(self):
        if globals.is_parked.get() == '1':
            return True
        else:
            return False
    


    def getDeclination(self, raw=False):
        if raw:
            return globals.dec_position.get()
        # alpaca format (float)
        rawvalue=globals.dec_position.get()
        #print("DECpos["+rawvalue+"]")
        dec = self.signedDegToFloat(rawvalue)
        #print("DEC["+str(dec)+"]")
        return dec

    def getRightAscension(self, raw=False):
        if raw:
            return globals.ra_position.get()
        # alpaca format (float)
        rawvalue=globals.ra_position.get()
        #print("RApos["+rawvalue+"]")
        ra = self.hoursToFloat(rawvalue)
        #print("RA["+str(ra)+"]")
        return ra
    
    def getGuideRateDec(self):
        return float(globals.alt_guide_speed.get())
    
    def getGuideRateAr(self):
        return float(globals.az_guide_speed.get())
    
    def getPierSide(self):
        if globals.pierSideWest.get() == '1':
            return 1
        else:
            return 0
    
    def getSiderealTime(self, raw=False):
        #------------ falta update sidereal time
        if raw:
            return globals.sideraltime_value.get()
        # alpaca format (float)
        rawvalue=globals.sideraltime_value.get()
        sid = self.hoursToFloat(rawvalue,False)
        return sid
    
    def getLatitude(self):
        return float(globals.latitude.get())
    
    def getLongitude(self):
        return float(globals.longitude.get())
    
    def getUTCdate(self): #Alpaca style ()
        date=globals.date_value.get()
        #print(date)
        localtime=globals.localtime_value.get()
        #print(localtime)
        utcdiff=int(globals.utcdiff_value.get())
        dateobj = datetime.datetime.strptime(date+"T"+localtime,'%m/%d/%YT%H:%M:%S')
        dateUTC = dateobj + datetime.timedelta(hours=utcdiff)
        return dateUTC.strftime("%Y-%m-%dT%H:%M:%S.123456Z")
    
    def getTrackingRate(self):
        return int(globals.track_value.get())
    
    def getTargetDec(self):
        rawvalue = self.sendCommandWaitReply(":Gd#")
        return self.signedDegToFloat(rawvalue[:-1])

    def getTargetRa(self):
        rawvalue = self.sendCommandWaitReply(":Gr#")
        return self.signedDegToFloat(rawvalue[:-1])
    
    def isSlewing(self):
        if globals.is_slewing.get() == '1':
            return True
        else:
            return False
    
    def isTracking(self):
        if globals.is_tracking.get() == '1':
            return True
        else:
            return False
    
    # ---- SET / GOTO / SLEW

    def setUTCdate(self, utcdate):
        print("setUTCdate["+str(utcdate)+"]")
        utcdiff=int(globals.utcdiff_value.get())
        dateobj = datetime.datetime.strptime(utcdate[:19],'%Y-%m-%dT%H:%M:%S')
        #dateobj=dateobj.replace(tzinfo=datetime.timezone.utc)
        esptime = dateobj - datetime.timedelta(hours=utcdiff)
        globals.localtime_value.set(esptime.strftime("%H:%M:%S"))
        globals.date_value.set(esptime.strftime("%m/%d/%Y"))
        self.syncLocalDateTime()

    def setTargetDec(self, declination):
        print("setTargetDec["+str(declination)+"]")
        x = declination * 3600;
        c = '+'
        if x < 0:
            x = -x
            c = '-'
        gra = int(x / 3600)
        temp = (x % 3600)
        mins = int(temp / 60)
        sec = int(temp % 60)
        cmd = ':Sd'+c+str(gra).zfill(2)+'*'+str(mins).zfill(2)+':'+str(sec).zfill(2)+'#'
#sprintf(message, ":Sd%c%02d*%02d:%02d#", c, gra, min, sec);
        print(cmd)
        self.sendCommand(cmd)
            
    def setTargetRa(self, rightascension):
        print("setTargetRa["+str(rightascension)+"]")
        
        seconds = rightascension * 3600 * 15
        x = math.trunc(seconds)/ 15.0
        ##rest = ((seconds % 15) * 2) / 3
        ##rest %= 15
        ##rest = seconds % 15 
        rest = 0
        gra = int(x / 3600)
        temp = (x % 3600) 
        mins = int(temp / 60)
        sec = int(temp % 60)
        cmd = ':Sr'+str(gra).zfill(2)+':'+str(mins).zfill(2)+':'+str(sec).zfill(2)+'.'+str(rest)+'#'

        print(cmd)
        self.sendCommand(cmd)
            
    def slewToTarget(self):
        resp = self.sendCommandWaitReply(":MS#",2)
        #print("slew["+str(resp)+"]")
        return resp

    def syncToTarget(self):
        self.sendCommandWaitReply(":CM#")
    
    def setTracking(self, tracking:bool):
        if not tracking:
            self.sendCommand(":Mh#")
        else:
            self.sendCommand(":Qw#")
        
    def setLatitude(self, latitude):
        globals.latitude.set(latitude)
        lat = f"{latitude:05.2f}"
        if latitude > 0:
            lat = '+'+lat
        #print("setLatitude["+lat+"]")
        cmd=":St"+lat+"#"
        #print("cmd["+cmd+"]")
        self.sendCommand(cmd)

    def setLongitude(self, longitude):
        globals.longitude.set(longitude)
        lon = f"{longitude:06.2f}"
        if longitude > 0:
            lon = '+'+lon
        #print("setLongitude["+lon+"]")
        cmd=":Sg"+lon+"#"
        #print("cmd["+cmd+"]")
        self.sendCommand(cmd)

    def unpark(self):
        self.sendCommand(cmd=":Mw#:Qw#")
    
    def getSpeedRates(self):
        rates=[]
        rate={}
        rate['Minimum']=0
        rate['Maximum']=4
        rates.append(rate)

        return rates

    def signedDegToFloat(self, rawvalue): #-03º22129"
        s= 1
        if rawvalue[0]=='-':
            s=-1
        gra = int(rawvalue[1:3])
        mins = int(rawvalue[4:6])
        secs = int(rawvalue[7:9])
        value = s*(gra + mins/60 + secs/3600)
        return value

    def unsignedDegToFloat(self, rawvalue): #000º00'00"
        gra = int(rawvalue[0:3])
        mins = int(rawvalue[4:6])
        secs = int(rawvalue[7:9])
        value = gra + mins/60 + secs/3600
        return value
    
    def hoursToFloat(self, rawvalue, decs=True): #11h36m00.0s / 01:09:10
        gra = rawvalue[:2]
        mins = rawvalue[3:5]
        secs = rawvalue[6:8]
        if decs:
            secs = rawvalue[6:10]
        value = int(gra) + int(mins)/60 + float(secs)/3600
        return value
    
    def syncLocalDateTime(self):

        ltime = globals.localtime_value.get()
        ldate = globals.date_value.get()

        esptime = datetime.datetime.strptime(ldate+"T"+ltime,'%m/%d/%YT%H:%M:%S')

        cmd2 = ":SL"+esptime.strftime("%H:%M:%S")+"#" 
        self.sendCommand(cmd2)
        time.sleep(1)
        self.flush() # just in case              
        cmd1 = ":SC"+esptime.strftime("%m/%d/%y")+"#"
        self.sendCommand(cmd1)
        time.sleep(1)
        self.flush() # just in case

    
    def initDateTime(self):
        #print('initDateTime')
        if not globals.tcp_connected:
            return
        self.flush()
        #time.sleep(0.5)

        globals.localtime_diff_value.set(0)
        response = self.sendCommandWaitReply(':GG#') #UTC difference
        if response == None or response == '':
            globals.localtime_diff_value.set(0)
            return
        #print(response)
        globals.utcdiff_value.set(response[:-1])
        utcdiff = float(response[:-1])

        if globals.picGotoLevel == 2: # we MUST sync date/time
            self.flush() # just in case
            pctime = datetime.datetime.now(datetime.timezone.utc)
            esptime = pctime - datetime.timedelta(hours=utcdiff)
            globals.localtime_value.set(esptime.strftime("%H:%M:%S"))
            globals.date_value.set(esptime.strftime("%m/%d/%Y"))
            self.syncLocalDateTime()

        else:
            response = self.sendCommandWaitReply(':GC#') # Local date
            globals.date_value.set(response[:-1])
            date=response[:-1]
            response = self.sendCommandWaitReply(':GL#') # Local time
            globals.localtime_value.set(response[:-1])
            datetimeval = date + ' '+ response[:-1]
            #print(datetimeval)
            #----------------
            # store difference with computer time
            #----------------
            pctime = datetime.datetime.now(datetime.timezone.utc)
            esptime = datetime.datetime.strptime(datetimeval,'%m/%d/%y %H:%M:%S')
            esptime = esptime + datetime.timedelta(hours=utcdiff)
            esptime = esptime.replace(tzinfo=datetime.timezone.utc)
            timediff = pctime - esptime
            globals.localtime_diff_value.set(timediff.total_seconds())

    def getBasicData(self):
        #print('getBasicData')
        if not globals.tcp_connected:
            return
        self.flush()
        time.sleep(0.5)
        #ACK
        #print('ACK')
        response = self.sendCommandWaitReply(b'\x06',2)
        #print(response)
        if response[0]=='A':
            #print('AltAz')
            globals.is_altAz.set(1)
        else:
            globals.is_altAz.set(0)

        #check esp32go version level
        globals.picGotoLevel = 0 # assume ESP32go full support

        #print('config')
        #full config
        response = self.sendCommandWaitReply(':cA#',0,True)
        #print(response)
        if response == 'TIMEOUT' or response == '':
            print("Old PicGoto compatibility mode")
            globals.picGotoLevel = 2 # old picGoto board
            #print("picGotoLevel["+str(globals.picGotoLevel)+"]")
            # get longitude / latitude from lx200 commands (low res)
            #lat
            response = self.sendCommandWaitReply(":Gt#")
            globals.latitude.set(response[:-1])
            #long
            response = self.sendCommandWaitReply(":Gg#")
            globals.longitude.set(response[:-1])
            #print("after config picgoto")

        else:
            res = response.splitlines()
            #print(res)
            globals.longitude.set(res[11])
            globals.latitude.set(res[12])
            #print(globals.longitude.get())
            #print(globals.latitude.get())
            globals.az_count.set(res[0])
            globals.alt_count.set(res[1])

            globals.az_guide_speed.set(res[2])
            globals.az_center_speed.set(res[3])
            globals.az_find_speed.set(res[4])
            globals.az_slew_speed.set(res[5])

            globals.alt_guide_speed.set(res[6])
            globals.alt_center_speed.set(res[7])
            globals.alt_find_speed.set(res[8])
            globals.alt_slew_speed.set(res[9])

            globals.eqTrack.set(res[19])

        if globals.picGotoLevel < 2:
            # ESP32go full ?
            #print('GVN')
            response = self.sendCommandWaitReply(':GVN#',0,True)
            #print(response)
            res=response[:-1]
            #print(res)
            if response == 'TIMEOUT' or float(res) < 0:
                globals.picGotoLevel = 2 # just in case
            elif float(res) < 5:
                globals.picGotoLevel = 1 # ESP32go not updated
                print("ESP32go pre-V5 mode")

        #print("picGotoLevel["+str(globals.picGotoLevel)+"]")


    def updateStatus(self):
        if globals.comLock:
            return

        if self.connected() and not globals.commandQueue and not globals.blindCommandQueue: #preference is given to queued commands
            self.flush()

        if globals.picGotoLevel > 1: # old picGoto, no status commands available
            time.sleep(0.5)
            response = self.sendCommandWaitReply(":GR#")
            if response == None or response == '':
                return
            #print("RA["+response+"]")
            pos=response[:2]+'h'+response[3:5]+'m'+response[6:10]+'s'
            globals.ra_position.set(pos)      
            response = self.sendCommandWaitReply(":GD#")
            #print("DEC["+response+"]")
            pos=response[:3]+'º'+response[4:6]+'\''+response[7:9]+'"'
            globals.dec_position.set(pos)     
            globals.track_value.set(0)        
            return

        response = self.sendCommandWaitReply(":Gx#",50)
        if response == None or len(response) < 45:
            #print(response)
            #self.flush()
            return
        #print(response)
        pos=response[:2]+'h'+response[3:5]+'m'+response[6:10]+'s'
        globals.ra_position.set(pos)

        pos=response[11:14]+'º'+response[15:17]+'\''+response[18:20]+'"'
        globals.dec_position.set(pos)

        if globals.is_altAz.get()=='1':
            pos=response[21:24]+'º'+response[25:27]+'\''+response[28:30]+'"'
            globals.az_position.set(pos)
            pos=response[31:34]+'º'+response[35:37]+'\''+response[38:40]+'"'

            globals.alt_position.set(pos)
        #else:
        #    print("EQ only")

            #globals.az_position.set(response[21:29])
            #globals.alt_position.set(response[31:39])

        if globals.picGotoLevel != 0: # extended status not supported
            globals.track_value.set(0)
            return
        
        # extended status
        dresponse = self.sendCommandWaitReply(":GU#")
        if dresponse == None or len(dresponse) < 4:
            #print(dresponse)
            #self.flush()
            return
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
        #globals.track_value.set(dresponse[4]) 
        match dresponse[4]: # set to valid alpaca values
            case '1': # sideral
                globals.track_value.set(0)
            case '2': # solar
                globals.track_value.set(2)
            case '3': # lunar
                globals.track_value.set(1)
            case '4': # king
                globals.track_value.set(3)
            case _: 
                globals.track_value.set(0)
