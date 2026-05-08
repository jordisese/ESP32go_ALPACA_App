
from tkinter import *
import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext
from tkinter import font
from tkinter import messagebox
from tkinter.ttk import *

import platform
if platform.system()=="Darwin": # MACOS
    from tkmacosx import Button
    from tkmacosx import Radiobutton
else:
    from tkinter import Button
    from tkinter import Radiobutton

import time

import tcpsocket

import alpaca
from alpaca import AlpacaServer

import discovery
from discovery import DiscoveryResponder

import globals

from config import Config
import config

#root = Tk()
root = globals.root
#----------------
#global variables
#----------------
#global az_position
#az_position=tk.StringVar() 
#global alt_position
#alt_position=tk.StringVar()
#global ra_position
#ra_position=tk.StringVar()
#global dec_position
#dec_position=tk.StringVar()
#global speed_value
#speed_value=tk.StringVar()
#global track_value
#track_value=tk.StringVar()
#global localtime_value
#localtime_value=tk.StringVar()
#global utctime_value
#utctime_value=tk.StringVar()
#global sideraltime_value
#sideraltime_value=tk.StringVar()
#----------------

# --------- COMMANDS
def sendCommand(cmd):
    #print(cmd)
    globals.blindCommandQueue.append(cmd)

# ---------- END COMMANDS


# --------- BUTTONS
def speed_cmd():
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

def on_press_N(context):
    sendCommand(speed_cmd()+":Mn#")
def on_press_S(context):
    sendCommand(speed_cmd()+":Ms#")
def on_press_E(context):
    sendCommand(speed_cmd()+":Me#")
def on_press_W(context):
    sendCommand(speed_cmd()+":Mw#")

def on_release_N(context):
    sendCommand(":Qn#")
def on_release_S(context):
    sendCommand(":Qs#")
def on_release_E(context):
    sendCommand(":Qe#")
def on_release_W(context):
    sendCommand(":Qw#")

def stopCommand():
    sendCommand(":Q#")

def goHomeCommand():
    sendCommand(":hP#")
def resetHomeCommand():
    sendCommand(":pH#")

def setSideralCommand():
    sendCommand(":TQ#")
def setSolarCommand():
    sendCommand(":TS#")
def setLunarCommand():
    sendCommand(":TL#")
def setKingCommand():
    sendCommand(":TK#")
# --------- END BUTTONS


def create_scope_frame(container):
    frame = tk.Frame(container)


    frame0 = tk.LabelFrame(frame,width=30,text="Telescope")

    chk0 = tk.Checkbutton(frame0, text='Parked', variable=globals.is_parked)
    chk0.grid(column=0, row=0)
    chk1 = tk.Checkbutton(frame0, text='Track', variable=globals.is_tracking)
    chk1.grid(column=1, row=0)
    chk2 = tk.Checkbutton(frame0, text='AltAz', variable=globals.is_altAz)
    chk2.grid(column=2, row=0)

    button1_font = font.Font(family='Helvetica', size=14, weight='bold')
    button2_font = font.Font(family='Helvetica', size=14, weight='normal')

    #but_NE = Button(frame0, text='NE', width=4, font=button1_font)
    #but_NE.grid(column=0, row=2)
    
    but_N = Button(frame0, text='N', font=button1_font)
    but_N.grid(column=1, row=2)

    #but_NW = Button(frame0, text='NW', width=4, font=button1_font)
    #but_NW.grid(column=2, row=2)


    #but_SE = Button(frame0, text='SE', width=4, font=button1_font)
    #but_SE.grid(column=0, row=4)
    
    but_S = Button(frame0, text='S', font=button1_font)
    but_S.grid(column=1, row=4)

    #but_SW = Button(frame0, text='SW', width=4, font=button1_font)
    #but_SW.grid(column=2, row=4)

    but_E = Button(frame0, text='E', font=button1_font)
    but_E.grid(column=0, row=3)

    but_ST = Button(frame0, text='Stop', command=stopCommand, font=button1_font)
    but_ST.grid(column=1, row=3)
    
    but_W = Button(frame0, text='W', font=button1_font)
    but_W.grid(column=2, row=3)

    but_N.bind("<ButtonPress>", on_press_N)
    but_S.bind("<ButtonPress>", on_press_S)
    but_E.bind("<ButtonPress>", on_press_E)
    but_W.bind("<ButtonPress>", on_press_W)
    but_N.bind("<ButtonRelease>", on_release_N)
    but_S.bind("<ButtonRelease>", on_release_S)
    but_E.bind("<ButtonRelease>", on_release_E)
    but_W.bind("<ButtonRelease>", on_release_W)



#       self.button.bind("<ButtonPress>", self.on_press)
#       self.button.bind("<ButtonRelease>", self.on_release)
#   def on_press(self, event):
#       self.log("button was pressed")
#    def on_release(self, event):
#        self.log("button was released")



    frame1 = tk.LabelFrame(frame,width=30, text="Speed")

    rad1 = Radiobutton(frame1,text='Slew', variable=globals.speed_value, value=1)
    rad2 = Radiobutton(frame1,text='Find', variable=globals.speed_value, value=2)
    rad3 = Radiobutton(frame1,text='Center', variable=globals.speed_value, value=3)
    rad0 = Radiobutton(frame1,text='Guide', variable=globals.speed_value, value=0)

    rad1.grid(column=0, row=7)
    rad2.grid(column=1, row=7)
    rad3.grid(column=2, row=7)
    rad0.grid(column=3, row=7)

    frame2 = tk.LabelFrame(frame,width=30, text="Tracking mode")

    tk_rad1 = Radiobutton(frame2,text='Sideral', command=setSideralCommand, variable=globals.track_value, value=1)
    tk_rad3 = Radiobutton(frame2,text='Solar', command=setSolarCommand, variable=globals.track_value, value=2)
    tk_rad2 = Radiobutton(frame2,text='Lunar', command=setLunarCommand, variable=globals.track_value, value=3)
    tk_rad4 = Radiobutton(frame2,text='King', command=setKingCommand, variable=globals.track_value, value=4)

    tk_rad1.grid(column=0, row=9)
    tk_rad2.grid(column=1, row=9)
    tk_rad3.grid(column=2, row=9)
    tk_rad4.grid(column=3, row=9)

    frame3 = tk.LabelFrame(frame,width=30, text="Status")

    txt = scrolledtext.ScrolledText(frame3,width=30,height=5)
    txt.grid(column=0, row=1)

    frame4 = Frame(frame)
    globals.connect_disconnect.set('Connect')
    globals.connect_status.set('Disconnected')
    globals.connected_status.set('')


    lbl_disconnected = tk.Label(frame4, textvariable=globals.connect_status, font=globals.connect_status_font, fg='red')
    lbl_disconnected.grid(column=0, row=0)
    lbl_connected = tk.Label(frame4, textvariable=globals.connected_status, font=globals.connect_status_font, fg='green')
    lbl_connected.grid(column=1, row=0)
    but_connect = Button(frame4, textvariable=globals.connect_disconnect, command=tcp_connect, font=globals.connect_disconnect_font)
    but_connect.grid(column=2, row=0)    

    frame5 = tk.LabelFrame(frame,width=30, text="Homing")

    but_gH = Button(frame5, text='Go&Park Home', command=goHomeCommand, font=button2_font)
    but_gH.grid(column=0, row=0)
    but_rH = Button(frame5, text='Reset Home', command=resetHomeCommand, font=button2_font)
    but_rH.grid(column=1, row=0)
 #   but_pk = Button(frame0, text='Park', command=parkCommand, font=button2_font)
 #   but_pk.grid(column=2, row=0)



    frame0.grid(column=0, row=0, sticky="nsew")
    frame5.grid(column=0, row=2, sticky="nsew")
    frame1.grid(column=0, row=1, sticky="nsew")
    frame2.grid(column=0, row=3, sticky="nsew")
    frame3.grid(column=0, row=4, sticky="nsew")
    frame4.grid(column=0, row=5, sticky="nsew")

    globals.is_altAz.set(0)
    globals.is_tracking.set(0)
    globals.is_parked.set(0)

    return frame


def saveConnInfo():
    Config.save_esp32go_info()
    messagebox.showinfo("Info", "Settings saved")

def create_config_frame(container):
    frame = Frame(container)

    tab_control = ttk.Notebook(frame)
    
    tab1 = Frame(tab_control)
    tab2 = Frame(tab_control)
    tab3 = Frame(tab_control)
    tab4 = Frame(tab_control)
    tab5 = Frame(tab_control)
    tab6 = Frame(tab_control)
    
    tab_control.add(tab1, text='Control')
    tab_control.add(tab2, text='Settings')
    tab_control.add(tab3, text='Connection')
    tab_control.add(tab4, text='Config')
    tab_control.add(tab5, text='TMC/Aux')
    tab_control.add(tab6, text='Focus/Wheel')

    #lbl1 = Label(tab1, text= 'Telescope', font=("Arial", 14))
    #lbl1.grid(column=0, row=0)


    radec_font = font.Font(family='Helvetica', size=30, weight='bold')
    altaz_font = font.Font(family='Helvetica', size=30, weight='bold')

    position = tk.LabelFrame(tab1, text="Position")
    pos_ra = tk.Label(position, textvariable=globals.ra_position, font=radec_font, fg='red')
    pos_ra.grid(column=0, row=0)
    pos_dec = tk.Label(position, textvariable=globals.dec_position, font=radec_font, fg='red')
    pos_dec.grid(column=0, row=1)
    altaz = tk.LabelFrame(tab1, text="AltAz")
    pos_az = tk.Label(altaz, textvariable=globals.az_position, font=altaz_font, fg='green')
    pos_az.grid(column=0, row=0)
    pos_alt = tk.Label(altaz, textvariable=globals.alt_position, font=altaz_font, fg='green')
    pos_alt.grid(column=0, row=1)
    time = tk.LabelFrame(tab1, text="Time")
    time_local = tk.Label(time, textvariable=globals.localtime_value)
    time_local.grid(column=0, row=0)
    time_utc = tk.Label(time, textvariable=globals.utctime_value)
    time_utc.grid(column=0, row=1)
    time_sideral = tk.Label(time, textvariable=globals.sideraltime_value)
    time_sideral.grid(column=0, row=2)

    position.grid(column=0, row=0)
    altaz.grid(column=1, row=0)
    time.grid(column=0, row=1)




    lbl2 = Label(tab2, text= 'label2')
    lbl2.grid(column=0, row=0)
    
    #lbl3 = Label(tab3, text= 'label3')
    #lbl3.grid(column=0, row=0)

    connection = tk.LabelFrame(tab3, text="Connection")
    tk_rad1 = Radiobutton(connection, text='TCP/IP', variable=globals.connType_value, value=1)
    tk_Address = tk.Entry(connection, textvariable=globals.connAddress_value)
    tk_Port = tk.Entry(connection, textvariable=globals.connPort_value)
    tk_rad2 = Radiobutton(connection,text='Serial', variable=globals.connType_value, value=2)
    tk_CommPort = tk.Entry(connection, textvariable=globals.serialPort_value)
    tk_CommSpeed = tk.Entry(connection, textvariable=globals.serialSpeed_value)
    tk_check0 = tk.Checkbutton(connection, text='Connect at startup', variable=globals.autoConnect)    
    tk_rad1.grid(column=0, row=0, sticky=tk.NW)
    tk_Address.grid(column=1, row=0, sticky=tk.NW)
    tk_Port.grid(column=2, row=0, sticky=tk.NW)
    tk_rad2.grid(column=0, row=1, sticky=tk.NW)
    tk_CommPort.grid(column=1, row=1, sticky=tk.NW)
    tk_CommSpeed.grid(column=2, row=1, sticky=tk.NW)
    tk_check0.grid(column=0, row=2, columnspan=3, sticky=tk.NW)

    connection.grid(column=0, row=0, sticky=tk.NW)
    
    alpacaOpts = tk.LabelFrame(tab3, text="Alpaca")
    tk_check1 = tk.Checkbutton(alpacaOpts, text='Discovery service', variable=globals.alpacaDiscovery)
    tk_check2 = tk.Checkbutton(alpacaOpts, text='Alpaca server', variable=globals.alpacaServer)    
    tk_check1.grid(column=0, row=1, sticky=tk.NW)
    tk_check2.grid(column=0, row=2, sticky=tk.NW)
    
    alpacaOpts.grid(column=0, row=1, sticky=tk.NW)

    button2_font = font.Font(family='Helvetica', size=14, weight='normal')

    but_saveConn = Button(tab3, text='Save',  command=saveConnInfo, font=button2_font)
    but_saveConn.grid(column=0, row=3, sticky=tk.NW)


    lbl4 = Label(tab4, text= 'label4')
    lbl4.grid(column=0, row=0)
    
    
    
    tab_control.pack(expand=1, fill='both')

    #globals.connType_value.set(1)
    #globals.alpacaDiscovery.set(1)
    #globals.alpacaServer.set(1)

    globals.connAddress_value.set(Config.esp32go_ip_address)
    globals.connPort_value.set(Config.esp32go_port)
    globals.serialPort_value.set(Config.esp32go_serialPort)
    globals.serialSpeed_value.set(Config.esp32go_serialSpeed)
    globals.connType_value.set(Config.esp32go_connectionType)
    globals.autoConnect.set(Config.esp32go_autoconnect)
    globals.alpacaDiscovery.set(Config.alpaca_discovery)
    globals.alpacaServer.set(Config.alpaca_server)

    return frame

def tcp_connect():
    if globals.connect_disconnect.get() == 'Disconnect' or globals.tcp_connected:
        globals.connect_disconnect.set('Connect')
        tcp_disconnect()
        return

    globals.tcp_please_disconnect=False

    # secondary threads
    print('Starting thread')
    #_TCP = tcpsocket.TCPconnection('192.168.1.21',10001)
    #_TCP = tcpsocket.TCPconnection(Config.esp32go_ip_address,Config.esp32go_port)
    try:
        _TCP = tcpsocket.TCPconnection(Config.esp32go_ip_address,Config.esp32go_port)
    except:
        print("Exception connecting to ESP32go")
    if globals.connection_error == True:
        globals.connection_error = False
        messagebox.showerror("Error", "Connection failed")

def tcp_disconnect():
    globals.tcp_please_disconnect=True #thread will exit ASAP


def fire_alpaca_discovery():
    # ---------
    # DISCOVERY
    # ---------
    if globals.alpacaDiscovery.get() == 0:
        return
    _DSC = DiscoveryResponder(Config.ip_address, Config.port)

def fire_alpaca_server():
    # -------------
    # ALPACA SERVER
    # -------------
    if globals.alpacaServer.get() == 0:
        return
    _ALPACA = AlpacaServer(Config.ip_address, Config.port)


def create_main_window():

    root.title("ESp32go")
    if platform.system()=="Darwin": # MACOS
        root.geometry('850x400')
    else:
        root.geometry('850x500')

#    try:
#        # windows only (remove the minimize/maximize button)
#        root.attributes('-toolwindow', True)
#    except TclError:
#        print('Not supported on your platform')

    # layout on the root window
    root.columnconfigure(0, weight=4)
    root.columnconfigure(1, weight=1)

    scope_frame = create_scope_frame(root)
    scope_frame.grid(column=0, row=0, sticky=tk.NW)

    config_frame = create_config_frame(root)
    config_frame.grid(column=1, row=0, sticky=tk.NW)

    # default values
    #global speed_value
    #global track_value
    #global ra_position
    #global dec_position
    #global az_position
    #global alt_position
    #global localtime_value
    #global utctime_value
    #global sideraltime_value

    globals.speed_value.set(2)
    globals.track_value.set(1)
    globals.ra_position.set('00h00m00.0s')
    globals.dec_position.set('+00º00\'00"')
    globals.az_position.set('+000º00\'00"')
    globals.alt_position.set('+00º00\'00"')
    globals.localtime_value.set('Local: 00:00:00')
    globals.utctime_value.set('UTC: 00:00:00')
    globals.sideraltime_value.set('Sid: 00:00:00')

    root.after(1, lambda: root.focus_force())

    # secondary threads
    #try:
    #    _TCP = tcpsocket.TCPconnection('192.168.1.21',10001)
    #except:
    #    print("Exception connecting to ESP32go")

    if globals.autoConnect.get()=='1':
        tcp_connect()

    fire_alpaca_discovery()
    fire_alpaca_server()

    # main loop
    root.mainloop()




if __name__ == "__main__":
    create_main_window()