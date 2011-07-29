#!/usr/bin/python2
import sys
import curses
import getopt
import time
import os
import wicd
from wicd import dbusmanager
from dbus import DBusException

# connection to DBUS interface
try:
    dbusmanager.connect_to_dbus()
except DBusException:
        print "Cannot connect to WICD daemon, please be sure daemon is started before using wtop. You can start daemon with /etc/init.d/wicd start, or /etc/rc.d/wicd start, or wicd from root account."
        sys.exit()

bus = dbusmanager.get_bus()
dbus_ifaces = dbusmanager.get_dbus_ifaces()
daemon = dbus_ifaces['daemon']
wireless = dbus_ifaces['wireless']
[state, info] = daemon.GetConnectionStatus()
myscreen = curses.initscr()
curses.noecho()
curses.cbreak()

myscreen.clear()
myscreen.border(0)
myscreen.addstr(1, 1, "Scanning...")
myscreen.refresh()
myscreen.timeout(5000)

def get_prop(net_id, prop):
        """ Get attribute of wireless network """
        return wireless.GetWirelessProperty(net_id, prop)

def fix_strength(val, default):
        """ Assigns given strength to a default value if needed. """
        return val and int(val) or default

# HISTORY
networks = {}

def main():
    global myscreen, networks
    myscreen.border(0)
    i=0

    [state, info] = daemon.GetConnectionStatus()
    wireless.Scan(True)

    num_networks = wireless.GetNumberOfNetworks()
    myscreen.clear()
    myscreen.border(0)

    if num_networks > 0:
        myscreen.addstr(1, 1, 'CURRENT SCAN RESULTS:')
        i=1
        for x in range(0, num_networks):
            i=i+1
            essid = str(get_prop(x, "essid"))
            strength = str(fix_strength(get_prop(x, "quality"), -1))
            encryption = str(get_prop(x, "encryption_method"))
            channel = get_prop(x, 'channel')
            mac = str(get_prop(x, "bssid"))

            myscreen.addstr(i, 1, strength+"% ("+encryption+") "+mac+" "+essid+" channel "+channel)

            try:
                networks[essid]
            except KeyError:
                networks[essid] = {}
                networks[essid]['signal'] = strength
                networks[essid]['encryption'] = encryption
                networks[essid]['channel'] = channel
                networks[essid]['mac'] = mac
                networks[essid]['name'] = essid
            else:
                if networks[essid]['signal'] < strength:
                    networks[essid]['signal'] = strength

        i=i+5
        myscreen.addstr(i, 1, 'HISTORY:')
        for x in networks:
            i=i+1
            myscreen.addstr(i, 1, networks[x]['signal']+"% ("+networks[x]['encryption']+") "+networks[x]['mac']+" "+networks[x]['name']+" channel "+networks[x]['channel'])

    myscreen.refresh()

main()
while True:
    ch = myscreen.getch()
    if ch == ord('q'):
        curses.endwin()
        exit()
    else:
        main()

# vim: set ts=4 sts=4 sw=4 expandtab :
