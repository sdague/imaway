#!/usr/bin/python

import dbus
import dbus.glib
import gobject
import subprocess


def go_screensaver(active):
    if active:
        print "Screen saver turned on"
        subprocess.call("pactl set-sink-mute 1 1", shell=True)
        subprocess.call("xchat -e -c 'AWAY'", shell=True)
    else:
        subprocess.call("pactl set-sink-mute 1 0", shell=True)
        subprocess.call("xchat -e -c 'BACK'", shell=True)
        print "Screen saver deactivated"


def main(args):
    bus = dbus.SessionBus()

    # # figure out what the screensaver is up to right now
    # saver_proxy = bus.get_object('org.gnome.ScreenSaver',
    #                              '/org/gnome/ScreenSaver')
    # minder.screensaver_active_state_changed(saver_proxy.GetActive())

    # listen for changes in screensaver activity
    bus.add_signal_receiver(
        go_screensaver,
        'ActiveChanged',
        'org.gnome.ScreenSaver')

    mainLoop = gobject.MainLoop()
    mainLoop.run()


if __name__ == '__main__':
    import sys
    main(sys.argv[1:])
