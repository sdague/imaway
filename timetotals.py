#!/usr/bin/python

import datetime
import os
import time

import dateutil.parser

ROOT_DIR = os.environ["HOME"] + "/.imaway"


def now_file():
    return "%s/%s/records.txt" % (ROOT_DIR, time.strftime("%Y-%U"))


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

    return "Week so far: %s, today %s" % (this_week, today)


def main():
    print time_today()

if __name__ == "__main__":
    main()
