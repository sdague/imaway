#!/usr/bin/python

import subprocess

import dbus
import dbus.glib
import gobject
import psutil


MUTE_CMD = "pactl set-sink-mute %s %s"


def is_xchat_running():
    return "xchat" in [psutil.Process(i).name for i in psutil.get_pid_list()]


def find_sinks():
    p = subprocess.Popen("pactl list | grep 'Sink #'",
                         stdout=subprocess.PIPE, shell=True)
    output = p.communicate()[0]
    lines = output.split('\n')
    return [int(x.split('Sink #')[1]) for x in lines if x]


def mute(mute=1):
    sinks = find_sinks()
    for sink in sinks:
        print "Sending %s" % (MUTE_CMD % (sink, mute))
        subprocess.call(MUTE_CMD % (sink, mute), shell=True)


def lock():
    print "Screen saver turned on"
    mute()
    if is_xchat_running():
        subprocess.call("xchat -e -c 'AWAY'", shell=True)


def unlock():
    mute(mute=0)
    if is_xchat_running():
        subprocess.call("xchat -e -c 'BACK'", shell=True)
    print "Screen saver deactivated"


def main(args):
    bus = dbus.SessionBus()

    # listen for changes in screensaver activity
    bus.add_signal_receiver(
        lock,
        'Locked',
        dbus_interface='com.canonical.Unity.Session')

    bus.add_signal_receiver(
        unlock,
        'Unlocked',
        dbus_interface='com.canonical.Unity.Session')

    mainLoop = gobject.MainLoop()
    mainLoop.run()


if __name__ == '__main__':
    import sys
    main(sys.argv[1:])
