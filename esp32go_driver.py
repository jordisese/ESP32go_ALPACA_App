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
        self.tcp_connect(blind=blind)
        self.initDateTime()

    def disconnect(self):
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


        except:
            print("Exception connecting to ESP32go")
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

    def sendCommandWaitReply(self,cmd:str,maxbytes=0):
        import time
        response = ''
        timeout = 5 
        #print(cmd)
        if not globals.tcp_connected:
            return
        cmdId=self.generateId()
        if maxbytes > 0:
            globals.commandQueueBytes[cmdId]=maxbytes
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
        dateobj = datetime.datetime.strptime(date+" "+localtime,'%m/%d/%y %H:%M:%S')
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
    
    # ---- GOTO / SLEW

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
        #rest = ((seconds % 15) * 2) / 3
        #rest %= 15
        #rest = seconds % 15 
        rest = 0
        gra = int(x / 3600)
        temp = (x % 3600) 
        mins = int(temp / 60)
        sec = int(temp % 60)
        cmd = ':Sr'+str(gra).zfill(2)+':'+str(mins).zfill(2)+':'+str(sec).zfill(2)+'.'+str(rest)+'#'
        print(cmd)
#sprintf(message, ":Sr%02d:%02d:%02d.%d#", gra, min, sec, rest);
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
        

    def unpark(self):
        self.sendCommand(cmd=":Mw#:Qw#")
    
    def getSpeedRates(self):
        rates=[]
        #guide={}
        #find={}
        #center={}
        #slew={}
        #guide['Minimum']=float(globals.az_guide_speed.get())
        #guide['Maximum']=float(globals.az_guide_speed.get())
        #center['Minimum']=float(globals.az_center_speed.get())
        #center['Maximum']=float(globals.az_center_speed.get())
        #find['Minimum']=float(globals.az_find_speed.get())
        #find['Maximum']=float(globals.az_find_speed.get())
        #slew['Minimum']=float(globals.az_slew_speed.get())
        #slew['Maximum']=float(globals.az_slew_speed.get())

        #rates.append(guide)
        #rates.append(center)
        #rates.append(find)
        #rates.append(slew)

        rate={}
        rate['Minimum']=0
        rate['Maximum']=15
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
    
    def initDateTime(self):
        if not globals.tcp_connected:
            return
        self.flush()
        time.sleep(0.5)
        response = self.sendCommandWaitReply(':GG#') #UTC difference
        if response == None:
            return
        #print(response)
        globals.utcdiff_value.set(response[:-1])
        utcdiff = int(response[:-1])

        response = self.sendCommandWaitReply(':GC#') # Local date
        globals.date_value.set(response[:-1])
        datetimeval=response[:-1]
        response = self.sendCommandWaitReply(':GL#') # Local time
        globals.localtime_value.set(response[:-1])
        datetimeval +=' '+response[:8]
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
        #check esp32go version level - PENDING!!!



        #print('config')
        #full config
        response = self.sendCommandWaitReply(':cA#')
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
        globals.az_center_speed.set(res[3])
        globals.az_find_speed.set(res[4])
        globals.az_slew_speed.set(res[5])

        globals.alt_guide_speed.set(res[6])
        globals.alt_center_speed.set(res[7])
        globals.alt_find_speed.set(res[8])
        globals.alt_slew_speed.set(res[9])

        globals.eqTrack.set(res[19])

