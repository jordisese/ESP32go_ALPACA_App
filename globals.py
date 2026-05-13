from tkinter import *
import tkinter as tk
from tkinter import font

root = Tk()

#----------------
#global variables
#----------------
global comLock
comLock = False

global picGotoLevel # 0 = ESP32go full, 1 = ESP32go part, 2 = PicGoto 4b
picGotoLevel = 0
global connect_picgotoLevel
connect_picgotoLevel = tk.StringVar() 

global polling_seconds
polling_seconds = 1

global blindCommandQueue
blindCommandQueue=[]

global commandQueue
commandQueue={}
global commandQueueBytes
commandQueueBytes={}
global commandCaptureTimeout
commandCaptureTimeout={}
global responseQueue
responseQueue={}

global tcp_connected
tcp_connected = False
global tcp_please_disconnect
tcp_please_disconnect = False
global tcp_please_update_dateTime
tcp_please_update_dateTime = False

global connect_disconnect
connect_disconnect=tk.StringVar() 
global connect_disconnect_font
connect_disconnect_font=font.Font(family='Helvetica', size=14, weight='bold')
global connect_status
connect_status=tk.StringVar() 
global connected_status
connected_status = tk.StringVar()
global connect_status_font
connect_status_font=font.Font(family='Helvetica', size=14, weight='normal')
global connect_note_font
connect_note_font=font.Font(family='Helvetica', size=12, weight='bold')
global connection_error
connection_error = False

global connType_value
connType_value = tk.StringVar()
global connAddress_value
connAddress_value = tk.StringVar()
global connPort_value
connPort_value = tk.StringVar()
global serialPort_value
serialPort_value = tk.StringVar()
global serialSpeed_value
serialSpeed_value = tk.StringVar()
global alpacaDiscovery
alpacaDiscovery = tk.StringVar()
global alpacaServer
alpacaServer = tk.StringVar()
global autoConnect
autoConnect = tk.StringVar()

global is_tracking
is_tracking=tk.StringVar()
global is_parked
is_parked=tk.StringVar()
global is_altAz
is_altAz=tk.StringVar()
global is_slewing
is_slewing=tk.StringVar()
global pierSideWest
pierSideWest=tk.StringVar()
global longitude
longitude=tk.StringVar()
global latitude
latitude=tk.StringVar()
global az_count
az_count=tk.StringVar()
global az_guide_speed
az_guide_speed=tk.StringVar()
global az_center_speed
az_center_speed=tk.StringVar()
global az_find_speed
az_find_speed=tk.StringVar()
global az_slew_speed
az_slew_speed=tk.StringVar()
global az_ramp
az_ramp=tk.StringVar()
global az_backlash
az_backlash=tk.StringVar()

global alt_count
alt_count=tk.StringVar()
global alt_guide_speed
alt_guide_speed=tk.StringVar()
global alt_center_speed
alt_center_speed=tk.StringVar()
global alt_find_speed
alt_find_speed=tk.StringVar()
global alt_slew_speed
alt_slew_speed=tk.StringVar()
global alt_ramp
alt_ramp=tk.StringVar()
global alt_backlash
alt_backlash=tk.StringVar()

global eqTrack
eqTrack=tk.StringVar()

global az_position
az_position=tk.StringVar() 
global alt_position
alt_position=tk.StringVar()
global ra_position
ra_position=tk.StringVar()
global dec_position
dec_position=tk.StringVar()
global ra_target
ra_target=tk.StringVar()
global dec_target
dec_target=tk.StringVar()
global speed_value
speed_value=tk.StringVar()
global track_value
track_value=tk.StringVar()

global date_value
date_value=tk.StringVar()
global localtime_value
localtime_value=tk.StringVar()
global utctime_value
utctime_value=tk.StringVar()
global utcdiff_value
utcdiff_value=tk.StringVar()
global sideraltime_value
sideraltime_value=tk.StringVar()
global localtime_diff_value
localtime_diff_value=tk.StringVar()

#----------------