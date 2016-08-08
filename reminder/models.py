from django.db import models
from django.forms import ModelForm
from django.utils import timezone
from django.contrib.auth.models import User
import datetime
from reminder.choices import IMPORTANCE_CHOICES, DATE_CHOICES





# Extends the User model and houses user information and settings
class UserProfile(models.Model):
    # One UserProfile per User, one User per UserProfile
    user = models.OneToOneField(User)

    # The additional attributes we wish to include.
    email_alerts = models.BooleanField(default=True)
    join_date = models.DateTimeField(default=timezone.now)
    score = models.score = models.IntegerField(default=0)

    # App exclusive settings go here
    en_notifications = models.BooleanField(default=True)

    def __unicode__(self):
        return self.user.username


# Individual task model.  Linked to a user.
class Task(models.Model):
    # One User per Task; any number of Tasks per User
    user = models.ForeignKey(User)

    # Default Settings
    name = models.CharField(max_length=50)
    created_date = models.DateTimeField(default=timezone.now)  # Not included in the profile, only in the settings
    due_date = models.DateTimeField(default=timezone.now)
    last_date = models.DateTimeField(default=timezone.now)
    frequency_int = models.IntegerField(default=1)
    frequency_choice = models.IntegerField(default=1)
    category = models.IntegerField(default=1)  # 1 = General, 2 = Hygiene/Fitness, 3 = Maintenance, 4 = School/Business, 5 = Social
    importance = models.IntegerField(default=3, choices=IMPORTANCE_CHOICES) # 1 = Trivial, 2 = Minor, 3 = Moderate, 4 = Significant, 5 = Critical
    past_due = models.BooleanField(default=True)
    time_delta = models.FloatField(default=0.0)
    choice = models.IntegerField(default=0)  # 0 = smartTRACK, 1 = date, 2 = frequency
    acknowledge_total = models.IntegerField(default=0)

    # smartTRACK Settings
    en_smartTRACK = models.IntegerField(default=0)  # 0 = disabled, 1 = enabled but tracking not ready, 2 = enabled and tracking ready
    omit_total = models.IntegerField(default=0)

    def importance_formatted(self):
        temp = self.importance

        if temp == 1:
            display = 'Trivial'
        elif temp == 2:
            display = 'Minor'
        elif temp == 3:
            display = 'Moderate'
        elif temp == 4:
            display = 'Significant'
        elif temp == 5:
            display = 'Critical'
        else:
            display = 'ERROR'

        return display

    def frequency_formatted(self):
        choice = self.frequency_choice
        integer = self.frequency_int
        tracking = self.en_smartTRACK

        if tracking == 1:
            return '-'
        else:
            if choice == 4:
                if integer == 1:
                    integer = ''
                    end = ''
                else:
                    integer = '{} '.format(integer)
                    end = 's'

                return 'Every {}month{}'.format(integer, end)
            else:
                val = int(self.time_delta)

                weeks = int(val / 604800)
                days = int((val - (weeks * 604800)) / 86400)
                hours = int((val - (weeks * 604800) - (days * 86400)) / 3600)
                weeks_comma = ', '
                days_comma = ', '

                if val == 0:
                    phrase = ''
                else:
                    if days == 0 and hours == 0:
                        weeks_comma = ''

                    if hours == 0:
                        days_comma = ''
                        hours = ''
                    elif hours == 1:
                        if days != 0 or weeks != 0:
                            hours = '{} hour'.format(hours)
                        else:
                            hours = 'hour'
                    else:
                        hours = '{} hours'.format(hours)

                    if days == 0:
                        days = ''
                    elif days == 1:
                        if weeks != 0:
                            days = '{} day{}'.format(days, days_comma)
                        else:
                            days = 'day{}'.format(days_comma)
                    else:
                        days = '{} days{}'.format(days, days_comma)

                    if weeks == 0:
                        weeks = ''
                    elif weeks == 1:
                        weeks = 'week{}'.format(weeks_comma)
                    else:
                        weeks = '{} weeks{}'.format(weeks, weeks_comma)

                    phrase = 'Every {}{}{}'.format(weeks, days, hours)

                return phrase

    def choice_formatted(self):
        choice = self.choice

        if choice == 0:
            return 'SmartTRACK'
        elif choice == 1:
            return 'Date'
        else:
            return 'Frequency'

    def __str__(self):
        return self.name


# Task Acknowledge History
class History(models.Model):
    task = models.ForeignKey(Task)
    acknowledge_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        month = self.acknowledge_date.month
        if month < 10:
            month = '0{}'.format(month)

        day = self.acknowledge_date.day
        if day < 10:
            day = '0{}'.format(day)

        hour = self.acknowledge_date.hour
        if hour < 10:
            hour = '0{}'.format(hour)

        minute = self.acknowledge_date.minute
        if minute < 10:
            minute = '0{}'.format(minute)

        return '{}{}{}_{}{}'.format(self.acknowledge_date.year, month, day, hour, minute)


# Custom Category
class Custom(models.Model):
    # One User per Custom Category; any number of Custom Categories per User
    user = models.ForeignKey(User)

    name = models.CharField(max_length=50)
    value = models.IntegerField(default=6)

    def __str__(self):
        return self.name
