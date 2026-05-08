# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# conf.py - Device configuration file and shared logger construction
# Part of the AlpycaDevice Alpaca skeleton/template device driver
#
# Author:   Robert B. Denny <rdenny@dc3.com> (rbd)
#
# Python Compatibility: Requires Python 3.7 or later
# GitHub: https://github.com/ASCOMInitiative/AlpycaDevice
#
# -----------------------------------------------------------------------------
# MIT License
#
# Copyright (c) 2022-2024 Bob Denny
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# -----------------------------------------------------------------------------
# Edit History:
# 24-Dec-2022   rbd 0.1 Logging
# 25-Dec-2022   rbd 0.1 More config items, separate logging section
# 27-Dec-2022   rbd 0.1 Move shared logger construction and global
#               var here. MIT license and module header. No mcast.
# 17-Feb-2024   ltf 0.6 GitHub PR #11 "docker friendly configuration"
#               https://github.com/ASCOMInitiative/AlpycaDevice/pull/11
#               (manually merged). Remove comment about "slimy hack".
# 20-Ferb-2024  rbd 0.7 Add sync_write_connected to control sync/async
#               write-Connected behavior.
#
import sys
import toml
import logging
import globals

_dict = {}
_dict = toml.load(f'{sys.path[0]}/config.toml')    # Errors here are fatal.

def get_toml(sect: str, item: str):
    setting = ''
    s = None
    try:
        setting = _dict[sect][item]
    except:
        setting = ''
    return setting

def set_toml(sect: str, item: str, setting):
    _dict[sect][item] = setting

def toml_update():
    with open(f'{sys.path[0]}/config.toml', "w") as f:
        f.write(toml.dumps(_dict))


class Config:
    """Device configuration. For docker based installation specific
        configuration, will first look for ``/alpyca/config.toml``
        and if exists, any setting there will override those in
        ``./config.toml`` (the default settings file).
    """
    # ESP32GO section
    esp32go_ip_address: str = get_toml('esp32go', 'ip_address')
    esp32go_port: int = get_toml('esp32go', 'port')
    esp32go_serialPort: str = get_toml('esp32go', 'serial_port')
    esp32go_serialSpeed: int = get_toml('esp32go', 'serial_speed')
    esp32go_connectionType: int = get_toml('esp32go', 'connection_type')
    esp32go_autoconnect: int = get_toml('esp32go', 'auto_connect')
    # ALPACA section
    alpaca_discovery:  int = get_toml('alpaca', 'discovery')
    alpaca_server: int = get_toml('alpaca', 'server')
    # ---------------
    # Network Section
    # ---------------
    ip_address: str = get_toml('network', 'ip_address')
    port: int = get_toml('network', 'port')
    # --------------
    # Server Section
    # --------------
    location: str = get_toml('server', 'location')
    verbose_driver_exceptions: bool = get_toml('server', 'verbose_driver_exceptions')
    # --------------
    # Device Section
    # --------------
    can_reverse: bool = get_toml('device', 'can_reverse')
    step_size: float = get_toml('device', 'step_size')
    steps_per_sec: int = get_toml('device', 'steps_per_sec')
    sync_write_connected: bool = get_toml('device', 'sync_write_connected')
    # ---------------
    # Logging Section
    # ---------------
    log_level: int = logging.getLevelName(get_toml('logging', 'log_level'))  # Not documented but works (!!!!)
    log_to_stdout: str = get_toml('logging', 'log_to_stdout')
    max_size_mb: int = get_toml('logging', 'max_size_mb')
    num_keep_logs: int = get_toml('logging', 'num_keep_logs')

    def save_esp32go_info():
        set_toml('esp32go','ip_address',globals.connAddress_value.get())
        set_toml('esp32go','port',int(globals.connPort_value.get()))
        set_toml('esp32go','serial_port',globals.serialPort_value.get())
        set_toml('esp32go','serial_speed',int(globals.serialSpeed_value.get()))
        set_toml('esp32go','connection_type',int(globals.connType_value.get()))
        set_toml('esp32go','auto_connect',int(globals.autoConnect.get()))

        set_toml('alpaca','discovery',int(globals.alpacaDiscovery.get()))
        set_toml('alpaca','server',int(globals.alpacaServer.get()))

        toml_update()

