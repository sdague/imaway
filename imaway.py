#!/usr/bin/python

import os
import subprocess
import time

import dbus
import dbus.glib
import gobject
import psutil

import timetotals

ROOT_DIR = os.environ["HOME"] + "/.imaway"

MUTE_CMD = "pactl set-sink-mute %s %s"

# the last event we had
EVENT = None


def now_dir():
    return "%s/%s" % (ROOT_DIR, time.strftime("%Y-%U"))


def record_event(event):
    global EVENT
    EVENT = event
    if not os.path.isdir(now_dir()):
        os.makedirs(now_dir(), 0755)

    nowfile = "%s/records.txt" % now_dir()
    with open(nowfile, "a") as f:
        f.write("%s %s\n" % (time.strftime("%Y-%m-%dT%H:%M:%S%z"), event))


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
    record_event("LOCKED")
    mute()
    if is_xchat_running():
        subprocess.call("xchat -e -c 'AWAY'", shell=True)


def unlock():
    mute(mute=0)
    record_event("UNLOCKED")
    if is_xchat_running():
        subprocess.call("xchat -e -c 'BACK'", shell=True)
    timetotals.notify()
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

    def timer():
        timetotals.notify_timer(mod=60, res=60)
        return True

    gobject.timeout_add(10000, timer)
    mainLoop = gobject.MainLoop()
    mainLoop.run()


if __name__ == '__main__':
    import sys
    main(sys.argv[1:])
