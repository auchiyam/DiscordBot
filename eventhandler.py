from sched import scheduler
from datetime import datetime, timedelta
import time
from reminder import Reminder
import discord
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.base import ConflictingIdError
import random
import threading
from database import Database

class EventHandler:

    def __init__(self, client, prefix):
        self.client = client
        self.loop = asyncio.get_event_loop()
        self.alarm = AsyncIOScheduler()
        self.alarm.start()
        self.prefix = prefix

    def create_new_alarm(self, reminder):
        try:
            t = datetime.now()
            if reminder.time - t < timedelta(days=1):
                self.alarm.add_job(self.print_reminder, trigger='date', args=[reminder],
                id="%s%s%s" % (self.datetime_to_time(reminder.time),
                reminder.channel, reminder.note),
                next_run_time=reminder.time)
            else:
                self.alarm.add_job(self.postpone, trigger='date', args=[reminder],
                id="%s%s%s" % (self.datetime_to_time(t + timedelta(days=1)), \
                               reminder.channel, reminder.note),
                next_run_time=t + timedelta(days=1))
            return ""
        except ConflictingIdError:
            with Database() as d:
                tmp = reminder.note.split("'")
                v = ""
                for a in tmp:
                    v += a + "\\'"
                v = v[0:-2]
                oid = reminder.get_id()
                return "A reminder with same note and time exists!\nPlease edit the existing reminder using the id [__%s__].\nFor more information on editing a reminder, type `%shelp remind` or `%sremind edit.`"\
                        % (oid, self.prefix, self.prefix)

    def postpone(self, reminder):
        self.create_new_alarm(reminder)

    def print_reminder(self, reminder):
        m = "Hello, "
        for u in reminder.users:
            m += "%s, " % (u.mention)
        m = m[0:-2] + "!\nIt is %s and this is a reminder for:" % (reminder.time)
        m += '```%s```' % reminder.note + "\n"
        if reminder.repeat != 5:
            r = self.translate_repeat(reminder)
            t = self.get_time(reminder.time, reminder.repeat)
            m += "This reminder is set to repeat %s, so the next reminder is on %s." % (r, t)
            rmd = Reminder(reminder.channel, reminder.server, note=reminder.note, time=t, repeat=reminder.repeat, users=reminder.users)
            with Database() as d:
                nt = d.escape_characters(reminder.note, "'")
                reminder.update_reminder(rmd)
            self.create_new_alarm(rmd)
        else:
            with Database() as d:
                id = d.select("reminder", ["id"], "channel='%s' AND note='%s' AND time='%s'" % (reminder.channel.id, d.escape_characters(reminder.note, "'"), reminder.time))[0]['id']
                reminder.delete_reminder()
        
        asyncio.set_event_loop(self.loop)
        asyncio.ensure_future(self.client.send_message(reminder.channel, m))
        
        
    def delay(self, sec):
        t0 = time.time()
        while time.time() < t0 + sec:
            time.sleep(1)
    
    def translate_repeat(self, reminder):
        if reminder.repeat == 1:
            return "daily"
        if reminder.repeat == 2:
            return "weekly"
        if reminder.repeat == 3:
            return "monthly"
        if reminder.repeat == 4:
            return "yearly"

    def get_time(self, time, repeat):
        if repeat == 1:
            return time + timedelta(days=1)
        if repeat == 2:
            return time + timedelta(days=7)
        if repeat == 3:
            return time + timedelta(days=self.get_dates(time))
        if repeat == 4:
            next_year = time + timedelta(days=365)
            if self.is_leap_year(next_year) and next_year >= datetime(year=next_year.year, month=2, day=29):
                return next_year + timedelta(days=1)
            return next_year

    def is_leap_year(self, t):
        year = t.year
        return year % 4 == 0 and year % 100 != 0 or year % 400 == 0

    def get_dates(self, t):
        month = t.month
        if (month % 2 == 1 and month < 8) or (month % 2 == 0 and month >= 8):
            return 31
        elif month != 2:
            return 30
        else:
            if self.is_leap_year(t):
                return 29
            return 28

    def get_id(self, operator):
        return sele

    def datetime_to_time(self, t):
        return time.mktime(t.timetuple()) + t.microsecond / 1E6

