#!/usr/bin/python

import ConfigParser
import datetime
import os
import subprocess
import time

import dateutil.parser

ROOT_DIR = os.environ["HOME"] + "/.imaway"
CONF = ROOT_DIR + "/imaway.conf"


def now_file():
    return "%s/%s/records.txt" % (ROOT_DIR, time.strftime("%Y-%U"))


def delta_hours(delta):
    return (delta.days * 24 + delta.seconds / (60 * 60))


def delta_mins(delta):
    return ((delta.seconds / 60) % 60)


def pretty_delta(delta):
    return "%d:%2.2d" % (delta_hours(delta), delta_mins(delta))


def calc_icon(week, day):
    """Calculate the icon for how the notification"""
    week_hours = delta_hours(week)
    day_hours = delta_hours(day)
    config = ConfigParser.ConfigParser()
    config.read(CONF)
    warnlimit = config.getint('limits', 'warn')
    infolimit = config.getint('limits', 'info')
    if (week_hours > (warnlimit * 5)) or (day_hours > warnlimit):
        return "dialog-warning"
    if (week_hours > (infolimit * 5)) or (day_hours > infolimit):
        return "dialog-information"
    return None


def notify():
    week, day = time_today()
    icon = calc_icon(week, day)
    pretty_time = ("Week: %s\nToday: %s" %
                   (pretty_delta(week), pretty_delta(day)))

    cmd = ['notify-send', 'Worked Time', pretty_time]
    if icon:
        cmd.extend(('-i', icon))
    print cmd
    subprocess.call(cmd)


def time_today():
    this_week = datetime.timedelta()
    today = datetime.timedelta()
    last_unlock = None
    now = dateutil.parser.parse(time.strftime("%Y-%m-%dT%H:%M:%S%z"))

    with open(now_file()) as f:
        for line in f:
            dt, event = line.split()
            dt = dateutil.parser.parse(dt)
            # print dt, event
            if event == "LOCKED" and last_unlock:
                this_week += (dt - last_unlock)

                if last_unlock.day == now.day:
                    # if we unlocked today, count it on today
                    today += (dt - last_unlock)

                last_unlock = None
            if event == "UNLOCKED":
                last_unlock = dt
    if last_unlock:
        this_week += (now - last_unlock)
        if last_unlock.day == now.day:
            today += (now - last_unlock)

    return this_week, today


def main():
    notify()

if __name__ == "__main__":
    main()
