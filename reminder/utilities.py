from django.utils import timezone
from dateutil.relativedelta import relativedelta
import datetime
from datetime import date
import pytz

def smartTRACK(task, new_time):
    print('smartTRACK begin')
    if task.history_set.count() > 0:
        avg_frequency = (new_time - task.created_date) / task.history_set.count()
    else:
        avg_frequency = 0

    temp_due = new_time + avg_frequency
    print('New Time: {}'.format(new_time))
    print('Average Frequency: {}'.format(avg_frequency))
    task.time_delta = float(avg_frequency.total_seconds())
    temp_due = temp_due - datetime.timedelta(seconds=temp_due.second, microseconds=temp_due.microsecond)
    task.due_date = temp_due
    print('New Due Date: {}'.format(temp_due))
    task.save()

    return avg_frequency

def validate(date, time):
    # must be in MM/DD/YYYY format
    result = True

    if result != 'default':
        try:
            date = pytz.utc.localize(datetime.datetime.strptime(date, '%m/%d/%Y'))
            if (date + datetime.timedelta(minutes=time)) < timezone.now():
                result = False
        except ValueError:
            result = False

    print('Validate: {}'.format(result))
    return result

