#!/usr/bin/python

import ConfigParser
import datetime
import os
import subprocess
import time

import dateutil.parser

import conf

ROOT_DIR = os.environ["HOME"] + "/.imaway"
CONF = ROOT_DIR + "/imaway.conf"
LAST_SENT = {'last': ''}


class TimeTracker(object):
    _thisweek = datetime.timedelta()
    _today = datetime.timedelta()
    _synctime = datetime.datetime.utcnow()

    def __init__(self):
        super(TimeTracker, self).__init__()

    def _current_db(self):
        nowdir = "%s/%s" % (ROOT_DIR, time.strftime("%Y-%U"))
        if not os.path.exists(nowdir):
            os.makedirs(nowdir)
        return nowdir + "/records.txt"

    def _sync(self):
        """sync the time tracker from the event log

        The TimeTracker event log is a series of lines in the format:

        2015-02-27T05:42:31-0500 UNLOCKED
        2015-02-27T09:13:26-0500 LOCKED
        2015-02-27T09:30:29-0500 UNLOCKED
        2015-02-27T10:14:15-0500 LOCKED
        2015-02-27T10:28:44-0500 UNLOCKED

        The math we are doing is start with the first UNLOCKED event
        and add up all the the timedeltas of UNLOCKED => LOCKED.

        If we cross a week boundary, we don't care. It means it won't
        really be accounted anywhere. That means don't work across
        that boundary.

        If we cross a day boundary, it probably won't be accounted
        correctly on the day, but it will for the week.

        """
        nowfile = self._current_db()

        newsynctime = datetime.datetime.utcnow().replace()
        if self._synctime < (newsynctime - datetime.timedelta(seconds=1)):
            # early bail so that we can
            return
        else:
            self._synctime == newsynctime

        if not os.path.exists(nowfile):
            return

        # the last time we've unlocked
        last_unlock = None

        self.thisweek = datetime.timedelta()
        self.today = datetime.timedelta()

        now = dateutil.parser.parse(time.strftime("%Y-%m-%dT%H:%M:%S%z"))
        with open(nowfile) as f:
            for line in f:
                dt, event = line.split()
                timestamp = dateutil.parser.parse(dt)

                # if we found a LOCKED event, and we've seen an UNLOCK
                # previously, we have an interval that should be accounted
                if event == "LOCKED" and last_unlock:
                    interval = (timestamp - last_unlock)
                    self.this_week += interval
                    if last_unlock.day == now.day:
                        # The interval started today, so we can
                        # account it for today
                        self.today += interval
                    # the last event was a LOCK event, so clear it
                    last_unlock = None

                # if the event is an unlocked, we toggle state again
                elif event == "UNLOCKED":
                    last_unlock = timestamp

        if last_unlock:
            self.this_week += (now - last_unlock)
            if last_unlock.day == now.day:
                self.today += (now - last_unlock)

    @property
    def thisweek(self):
        self._sync()
        return self._thisweek

    @property
    def today(self):
        self._sync()
        return self._today

    @property
    def hours_thisweek(self):
        self._sync()
        return (self._thisweek.days * 24 + self._thisweek.seconds / (60 * 60))

    @property
    def hours_today(self):
        self._sync()
        return (self._today.days * 24 + self._today.seconds / (60 * 60))


def now_file():
    nowdir = "%s/%s" % (ROOT_DIR, time.strftime("%Y-%U"))
    if not os.path.exists(nowdir):
        os.makedirs(nowdir)
    return nowdir + "/records.txt"


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
    config = conf.Config()

    if ((week_hours >= (config.warnlimit * 5)) or
        (day_hours >= config.warnlimit)):
        return "dialog-warning"
    if ((week_hours >= (config.infolimit * 5)) or
        (day_hours >= config.infolimit)):
        return "dialog-information"
    return None


def _send_notify(week, day):
    icon = calc_icon(week, day)
    pretty_time = ("Week: %s\nToday: %s" %
                   (pretty_delta(week), pretty_delta(day)))

    cmd = ['notify-send', 'Worked Time', pretty_time]
    if icon:
        cmd.extend(('-i', icon))
    print cmd
    subprocess.call(cmd)


def notify():
    week, day = time_today()
    _send_notify(week, day)


def notify_timer(mod=60, res=1):
    week, day = time_today()
    wmod = (week.seconds / res) % mod
    dmod = (day.seconds / res) % mod
    msg = "week %d, day %d" % (wmod, dmod)
    print msg
    if (wmod == 0 or dmod == 0) and LAST_SENT['last'] != msg:
        _send_notify(week, day)
        LAST_SENT['last'] = msg
    return True


def time_today():
    this_week = datetime.timedelta()
    today = datetime.timedelta()
    last_unlock = None
    now = dateutil.parser.parse(time.strftime("%Y-%m-%dT%H:%M:%S%z"))

    if os.path.exists(now_file()):
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
