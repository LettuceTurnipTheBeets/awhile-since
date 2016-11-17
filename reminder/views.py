from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.db.models import Q
from itertools import chain
from reminder.utilities import smartTRACK, validate
from .models import UserProfile, Task, History, Custom
from .forms import UserForm, PasswordForm
from django.template import RequestContext
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.views.decorators.cache import cache_control
from django.http import JsonResponse
import random
import datetime
from dateutil.relativedelta import relativedelta
import math
import pytz
from django.core.mail import send_mail
from django.conf import settings



# Home Page.  Display a brief message.  Should  be changed to an info page with sample task names/list
def home(request):
    print('\n***Home Requested***')
    template = Task.objects.all().order_by('?').filter(Q(user_id=1))[:9]

    return render(request, 'reminder/home.html', {'template': template})


# Acknowledge Initialization
def acknowledge_init(request):
    print('\n***Acknowledge_Init Requested***')
    response = {}
    task = request.user.task_set.get(pk=int(request.POST.get('id')))
    print('Task: {}'.format(task.name))

    response['last_year'] = task.last_date.year
    response['last_month'] = task.last_date.month
    response['last_day'] = task.last_date.day
    response['last_hour'] = task.last_date.hour
    response['last_minute'] = task.last_date.minute

    response['due_year'] = task.due_date.year
    response['due_month'] = task.due_date.month
    response['due_day'] = task.due_date.day
    response['due_hour'] = task.due_date.hour
    response['due_minute'] = task.due_date.minute

    response['name'] = task.name
    response['en_SmartTRACK'] = task.en_smartTRACK

    print('returning Json Response')
    return JsonResponse(response)


# Edit Task function.  Called when a table row is clicked.
def stat_init(request):
    print('\n***Stat_Init Requested***')
    response = {}
    task = request.user.task_set.get(pk=int(request.POST.get('id')))
    offset = int(int(request.POST.get('offset')) / 60)
    print('Task: {}'.format(task.name))

    # Populate the form's initial values with the correct task
    response['name'] = task.name
    response['en_SmartTRACK'] = task.en_smartTRACK
    response['choice'] = task.choice
    response['total'] = task.acknowledge_total
    response['track'] = task.choice_formatted()
    response['frequency'] = task.frequency_formatted()
    response['category'] = task.category
    response['importance'] = task.importance
    response['freq_int'] = task.frequency_int
    response['freq_choice'] = task.frequency_choice

    response['created_year'] = task.created_date.year
    response['created_month'] = task.created_date.month
    response['created_day'] = task.created_date.day
    response['created_hour'] = task.created_date.hour
    response['created_minute'] = task.created_date.minute

    response['last_year'] = task.last_date.year
    response['last_month'] = task.last_date.month
    response['last_day'] = task.last_date.day
    response['last_hour'] = task.last_date.hour
    response['last_minute'] = task.last_date.minute

    response['due_year'] = task.due_date.year
    response['due_month'] = task.due_date.month
    response['due_day'] = task.due_date.day
    response['due_hour'] = task.due_date.hour
    response['due_minute'] = task.due_date.minute

    due_date = task.due_date + datetime.timedelta(hours=0-offset)
    due_time = int(task.due_date.hour - offset)

    if due_time < 0:
        due_time += 24

    print('Due Date: {}'.format(due_date))
    print('Due Time: {}'.format(due_time))

    response['due_date'] = '{}/{}/{}'.format(due_date.month, due_date.day, due_date.year)
    response['due_time'] = due_time

    print('returning Json Response')
    return JsonResponse(response)


# Edit Task function.  Called when a table row is clicked.
def edit_task_init(request):
    print('\n***Edit_Task_Init Requested***')
    response = {}
    task = request.user.task_set.get(pk=int(request.POST.get('id')))
    print('Task: {}'.format(task.name))

    # Populate the form's initial values with the correct task
    response['name'] = task.name
    response['importance'] = task.importance
    response['en_SmartTRACK'] = task.en_smartTRACK
    response['choice'] = task.choice

    response['created_year'] = task.created_date.year
    response['created_month'] = task.created_date.month
    response['created_day'] = task.created_date.day
    response['created_hour'] = task.created_date.hour
    response['created_minute'] = task.created_date.minute

    if task.choice == 1:
        offset = int(int(request.POST.get('offset')) / 60)

        due_date = task.due_date + datetime.timedelta(hours=0-offset)
        due_time = int(task.due_date.hour - offset)

        if due_time < 0:
            due_time += 24

        print('Due Date: {}'.format(due_date))
        print('Due Time: {}'.format(due_time))

        response['due_date'] = '{}/{}/{}'.format(due_date.month, due_date.day, due_date.year)
        response['due_time'] = due_time
    elif task.choice == 2:
        response['frequency_int'] = task.frequency_int
        response['frequency_choice'] = task.frequency_choice

    response['category'] = task.category

    print('returning Json Response')
    return JsonResponse(response)


# Acknowledge function.  Called when 'Yes' is pressed on the acknowledge pop-up
def acknowledge(request):
    print('\n***Acknowledge Requested***')
    response = {}
    task = request.user.task_set.get(pk=int(request.POST.get('id')))
    print('Task: {}'.format(task.name))

    temp_time = timezone.now() + datetime.timedelta(seconds=1)
    formatted_time = timezone.now() - datetime.timedelta(seconds=timezone.now().second, microseconds=timezone.now().microsecond)
    freq_int = task.frequency_int
    freq_choice = task.frequency_choice
    choice = task.choice

    if request.POST.get('type') == 'button':
        due_list = request.user.task_set.exclude(id=task.id).filter(category=task.category).order_by('due_date')
        print('Tasks for category {}, ordered by due date: {}'.format(task.category, due_list))

        position_start = 0

        for temp_task in due_list:
            # print('Looping through Task: {}'.format(temp_task.name))
            # print('Is {}: {} < {}: {}'.format(task.name, task.due_date, temp_task.name, temp_task.due_date))
            if task.due_date < temp_task.due_date:
                print('{} comes before {}'.format(task.due_date, temp_task.due_date))
                break

            position_start += 1

    print('Type: {}'.format(request.POST.get('type')))

    if temp_time >= task.due_date:
        print('Acknowledged after it was due')
        if task.past_due:
            score = -5 - (task.importance * 5)
            request.user.userprofile.score += score
            request.user.userprofile.save()
            task.past_due = 0
            response['score'] = score
        else:
            response['score'] = 0

        if request.POST.get('type') == 'button':
            print('Type: button')
            task.past_due = 1
            task.last_date = formatted_time

            if choice == 0:
                if request.POST.get('omit') == 'true':
                    print('Old SmartTRACK omitted due date: {}'.format(task.due_date))
                else:
                    # create a new history point if not omitted
                    task.history_set.create(acknowledge_date=formatted_time)

                    smartTRACK(task, formatted_time)
                    task.en_smartTRACK = 2

                    print('New SmartTRACK due date: {}'.format(task.due_date))
            elif choice == 1:
                print('This uses a date')
                task.due_date = formatted_time + datetime.timedelta(seconds=task.time_delta)
                duration = int(task.time_delta / 3600)
                print('Duration: {}'.format(duration))
            elif choice == 2:
                print('This uses a frequency')
                if freq_choice == 1:
                    task.due_date = formatted_time + datetime.timedelta(hours=freq_int)
                elif freq_choice == 2:
                    task.due_date = formatted_time + datetime.timedelta(hours=freq_int * 24)
                elif freq_choice == 3:
                    task.due_date = formatted_time + datetime.timedelta(hours=freq_int * 24 * 7)
                elif freq_choice == 4:
                    task.due_date = formatted_time + relativedelta(months=freq_int)
                elif freq_choice == 5:
                    task.due_date = formatted_time + relativedelta(months=freq_int * 12)

            task.acknowledge_total += 1

    elif temp_time < task.due_date:
        print('Acknowledged before it was due')
        duration = 0

        if choice == 0:
            if request.POST.get('omit') == 'true':
                print('Old SmartTRACK omitted due date: {}'.format(task.due_date))
            else:
                # create a new history point if not omitted
                task.history_set.create(acknowledge_date=formatted_time)

                smartTRACK(task, formatted_time)
                task.en_smartTRACK = 2

                print('New SmartTRACK due date: {}'.format(task.due_date))
        elif choice == 1:
            print('This uses a date')
            task.due_date = formatted_time + datetime.timedelta(seconds=task.time_delta)
            duration = int(task.time_delta / 3600)
            print('Duration: {}'.format(duration))
        elif choice == 2:
            print('This uses a frequency')
            if freq_choice == 1:
                duration = freq_int
                task.due_date = formatted_time + datetime.timedelta(hours=duration)
            elif freq_choice == 2:
                duration = freq_int * 24
                task.due_date = formatted_time + datetime.timedelta(hours=duration)
            elif freq_choice == 3:
                duration = freq_int * 24 * 7
                task.due_date = formatted_time + datetime.timedelta(hours=duration)
            elif freq_choice == 4:
                duration = 24 * 30.4375
                task.due_date = formatted_time + relativedelta(months=freq_int)
            elif freq_choice == 5:
                duration = 24 * 365.25
                task.due_date = formatted_time + relativedelta(months=freq_int * 12)

        task.acknowledge_total += 1
        task.notified = False

        score = int(math.sqrt(duration) * (((task.importance * task.importance) / 50) + 1))

        if score > 100:
            score = 100

        print('Calculated Score: {}'.format(score))

        request.user.userprofile.score += score
        request.user.userprofile.save()

        print('New User Score: {}'.format(request.user.userprofile.score))

        response['score'] = score
        task.past_due = 1
        task.last_date = formatted_time

    task.save()
    print('Task saved')
    print('New Due Date: {}'.format(task.due_date))

    if request.POST.get('type') == 'button':
        category_list = request.user.task_set.filter(category=task.category)
        # print('Number of tasks with category {}: {}'.format(task.category, category_list.__len__()))

        response['changed'] = False

        if category_list.__len__() > 1:
            due_list = request.user.task_set.exclude(id=task.id).filter(category=task.category).order_by('due_date')
            print('Tasks for category {}, ordered by due date: {}'.format(task.category, due_list))

            position = 0

            for temp_task in due_list:
                print('Looping through Task: {}'.format(temp_task.name))
                if task.due_date < temp_task.due_date:
                    print('{} comes before {}'.format(task.due_date, temp_task.due_date))
                    break

                position += 1

            response['position_start'] = position_start
            print('Position Start: {}'.format(response['position_start']))
            response['position'] = position
            print('Position: {}'.format(response['position']))

            if position == position_start:
                response['changed'] = False
            else:
                response['changed'] = True

            response['id'] = task.id
            response['name'] = task.name

            total_categories_list = []
            sorted_categories = []
            sorted_numbers = []

            category_list = Custom.objects.filter(Q(user_id=1) | Q(user_id=request.user.id)).order_by('name')
            print('Category List: {}'.format(category_list))

            total_categories = request.user.task_set.order_by('category')

            for cat in total_categories:
                if cat.category not in total_categories_list:
                    total_categories_list.append(cat.category)

            print('Unique Category Numbers: {}'.format(total_categories_list))

            for num in total_categories_list:
                temp_name = str(Custom.objects.filter(Q(user_id=1) | Q(user_id=request.user.id)).filter(value=num)[0].name)
                sorted_categories.append([temp_name, num])

            sorted_categories = sorted(sorted_categories)

            for i in range(len(sorted_categories)):
                sorted_numbers.append(sorted_categories[i][1])

            print('Sorted Unique Category Numbers: {}'.format(sorted_numbers))

            for j in range(len(sorted_numbers)):
                if task.category == sorted_numbers[j]:
                    response['link_number'] = j
                    break

            print('Changed Positions?: {}'.format(response['changed']))

    response['due_year'] = task.due_date.year
    response['due_month'] = task.due_date.month
    response['due_day'] = task.due_date.day
    response['due_hour'] = task.due_date.hour
    response['due_minute'] = task.due_date.minute

    response['frequency'] = task.frequency_formatted()

    # check to see if the category header needs to change color
    category_list = request.user.task_set.filter(category=task.category)

    response['warning'] = True
    response['alarm'] = True

    for task in category_list:
        if (task.due_date < (temp_time - datetime.timedelta(seconds=60))) and task.en_smartTRACK != 1:
            response['alarm'] = False
            print('ALARM - {} is past due'.format(task.name))
        elif (task.due_date < (temp_time + datetime.timedelta(hours=24))) and task.en_smartTRACK != 1:
            response['warning'] = False
            print('WARNING - {} has one day remaining'.format(task.name))

    print('Remove Warning: {}'.format(response['warning']))
    print('Remove Alarm: {}'.format(response['alarm']))
    print('Returning Json Response')
    return JsonResponse(response)


def delete_task(request):
    print('\n***Delete_Task Requested***')
    response = {}

    task_id = int(request.POST.get('id'))
    task = request.user.task_set.get(pk=task_id)
    task.history_set.all().delete()

    print("Deleting Task: {}".format(task.name))
    task.delete()
    response['id'] = task_id

    print('Returning Json Response')
    return JsonResponse(response)


# Create Task function.  Called when the ajax modal form is saved.
def create_task(request):
    print('\n***Create_Task Requested***')
    # elapsed = timezone.now()

    if request.method == 'POST':
        post = request.POST
        print("method == 'POST'\nPOST data: {}".format(post))

        # cache the POSTed variables
        name = str(post.get('name'))[0:50]
        print('Name: {}'.format(name))

        radio_choice = int(post.get('radio-choice'))

        if radio_choice < 0:
            radio_choice = 0
        elif radio_choice > 2:
            radio_choice = 2

        en_smartTRACK = 0
        en_date = False
        en_frequency = False

        if radio_choice == 0:
            en_smartTRACK = 1
        elif radio_choice == 1:
            en_date = True
        elif radio_choice == 2:
            en_frequency = True

        print('Radio-Choice: {}'.format(radio_choice))

        importance = int(post.get('importance'))

        if importance < 1:
            importance = 1
        elif importance > 5:
            importance = 5

        print('Importance: {}'.format(importance))

        date = 'default'
        time = 0
        freq_choice = 1
        freq_int = 1
        valid_datetime = True

        if en_date:
            print('Date was entered')

            date = str(post.get('due_date'))[0:10]
            print('Due Date: {}'.format(date))

            time = int(post.get('due_time'))

            if time < 0:
                time = 0
            elif time > 47:
                time = 1380
            else:
                time = (time * 60) + int(post.get('offset'))

            print('Due Time: {}'.format(time))

            valid_datetime = validate(date, time)
            print('Valid Datetime: {}'.format(valid_datetime))
        elif en_frequency:
            print('Frequency was entered')

            freq_int = int(post.get('frequency_int'))
            print('Frequency Int: {}'.format(freq_int))

            freq_choice = int(post.get('frequency_choice'))

            if freq_choice < 1:
                freq_choice = 1
            elif freq_choice > 5:
                freq_choice = 5

            print('Frequency Choice: {}'.format(freq_choice))

        response = {}
        response['new_category'] = False

        if (not en_date) or (date and valid_datetime):
            print('Form is valid')
            post = request.POST

            temp_time = timezone.now() - datetime.timedelta(seconds=timezone.now().second, microseconds=timezone.now().microsecond)
            print('Temp Time: {}'.format(temp_time))

            # if we want to create then create a new task.  If we want to edit then pull the correct task
            if post.get('type') == 'create':
                print('Type: Create')

                category = int(post.get('category'))

                if category < 7:
                    if category < 1:
                        category = 1
                else:
                    category_high = Custom.objects.filter(user_id=request.user.id).order_by('-value')

                    print('User custom category list: {}'.format(category_high))
                    print('Category highest value: {}'.format(category_high[0].value))

                    if category > category_high[0].value:
                        category = category_high[0].value

                print('Category: {}'.format(category))

                # test_task = request.user.task_set.create()
                task = request.user.task_set.create(en_smartTRACK=0, created_date=temp_time, last_date=temp_time, category=category)

                print('Task: {} (id: {}) created'.format(task.name, task.id))

                edit_due = False
                edit_frequency = False

                response['count'] = request.user.task_set.count() - 1
                response['type'] = 'create'
            else:
                print('Type: Edit')
                task = request.user.task_set.get(pk=int(post.get('id')))
                print('Task: {}'.format(task.name))
                response['count'] = post.get('num')
                response['type'] = 'edit'

                if not date == 'default':
                    edit_due = task.due_date == pytz.utc.localize(datetime.datetime.strptime(date, '%m/%d/%Y')) + datetime.timedelta(minutes=time)
                else:
                    edit_due = True

                edit_frequency = (task.frequency_int == freq_int) and (task.frequency_choice == freq_choice)

                due_list = request.user.task_set.exclude(id=task.id).filter(category=task.category).order_by('due_date')
                print('Tasks for category {}, ordered by due date: {}'.format(task.category, due_list))

                position_start = 0

                for temp_task in due_list:
                    # print('Looping through Task: {}'.format(temp_task.name))
                    # print('Is {}: {} < {}: {}'.format(task.name, task.due_date, temp_task.name, temp_task.due_date))
                    if task.due_date < temp_task.due_date:
                        print('{} comes before {}'.format(task.due_date, temp_task.due_date))
                        break

                    position_start += 1

            print('After Create/Edit')
            print('smartTRACK: {}'.format(en_smartTRACK))

            response['update'] = False

            task.name = name
            task.importance = importance
            task.choice = radio_choice
            print(task.name)
            task.save()

            if not task.en_smartTRACK and en_smartTRACK:
                print('smartTRACK enabled on create or changed from False to True on edit')
                task.en_smartTRACK = en_smartTRACK
                task.due_date = task.created_date
                task.time_delta = 0

                response['update'] = True
            elif en_date:
                print('Due Date/Time Enabled')

                if not edit_due:
                    print('Due Date is not the same')
                    task.due_date = pytz.utc.localize(datetime.datetime.strptime(date, '%m/%d/%Y')) + datetime.timedelta(minutes=time)
                    task.time_delta = (task.due_date - temp_time).total_seconds()
                    task.en_smartTRACK = 0
                    print(task.due_date)

                    response['update'] = True
            elif en_frequency:
                print('Frequency Enabled')

                if not edit_frequency:
                    print('Frequency is not the same')
                    task.frequency_int = freq_int
                    task.frequency_choice = freq_choice
                    task.en_smartTRACK = 0

                    # check if hours, days, weeks, months, or years were submitted
                    if freq_choice == 1:
                        task.time_delta = datetime.timedelta(hours=freq_int).total_seconds()
                    elif freq_choice == 2:
                        task.time_delta = datetime.timedelta(hours=freq_int * 24).total_seconds()
                    elif freq_choice == 3:
                        task.time_delta = datetime.timedelta(hours=freq_int * 24 * 7).total_seconds()
                    elif freq_choice == 4:
                        task.time_delta = ((temp_time + relativedelta(months=freq_int)) - temp_time).total_seconds()
                    elif freq_choice == 5:
                        task.time_delta = ((temp_time + relativedelta(months=freq_int * 12)) - temp_time).total_seconds()

                    task.due_date = temp_time + datetime.timedelta(seconds=task.time_delta)

                    response['update'] = True

            if not post.get('type') == 'create':
                category_list = request.user.task_set.filter(category=task.category)
                # print('Number of tasks with category {}: {}'.format(task.category, category_list.__len__()))

                response['changed'] = False

                if category_list.__len__() > 1:
                    due_list = request.user.task_set.exclude(id=task.id).filter(category=task.category).order_by('due_date')
                    print('Tasks for category {}, ordered by due date: {}'.format(task.category, due_list))

                    position = 0

                    for temp_task in due_list:
                        print('Looping through Task: {}'.format(temp_task.name))
                        if task.due_date < temp_task.due_date:
                            print('{} comes before {}'.format(task.due_date, temp_task.due_date))
                            break

                        position += 1

                    response['position_start'] = position_start
                    print('Position Start: {}'.format(response['position_start']))
                    response['position'] = position
                    print('Position: {}'.format(response['position']))

                    if position == position_start:
                        response['changed'] = False
                    else:
                        response['changed'] = True

                    response['id'] = task.id
                    response['name'] = task.name

                    total_categories_list = []
                    sorted_categories = []
                    sorted_numbers = []

                    category_list = Custom.objects.filter(Q(user_id=1) | Q(user_id=request.user.id)).order_by('name')
                    print('Category List: {}'.format(category_list))

                    total_categories = request.user.task_set.order_by('category')

                    for cat in total_categories:
                        if cat.category not in total_categories_list:
                            total_categories_list.append(cat.category)

                    print('Unique Category Numbers: {}'.format(total_categories_list))

                    for num in total_categories_list:
                        temp_name = str(Custom.objects.filter(Q(user_id=1) | Q(user_id=request.user.id)).filter(value=num)[0].name)
                        sorted_categories.append([temp_name, num])

                    sorted_categories = sorted(sorted_categories)

                    for i in range(len(sorted_categories)):
                        sorted_numbers.append(sorted_categories[i][1])

                    print('Sorted Unique Category Numbers: {}'.format(sorted_numbers))

                    for j in range(len(sorted_numbers)):
                        if task.category == sorted_numbers[j]:
                            response['link_number'] = j
                            break

                    print('Changed Positions?: {}'.format(response['changed']))
            elif post.get('type') == 'create':
                print('type == create')
                category_list = request.user.task_set.filter(category=task.category)
                print('Number of tasks with category {}: {}'.format(task.category, category_list.__len__()))

                if category_list.__len__() > 1:
                    due_list = request.user.task_set.exclude(id=task.id).filter(category=task.category).order_by('due_date')
                    print('Tasks for category {}, ordered by due date: {}'.format(task.category, due_list))

                    position = 0

                    for temp_task in due_list:
                        # print('Looping through Task: {}'.format(temp_task.name))
                        if task.due_date < temp_task.due_date:
                            print('{} comes before {}'.format(task.due_date, temp_task.due_date))
                            break

                        position += 1

                    response['position'] = position
                    print('Position: {}'.format(response['position']))

                    total_categories_list = []
                    sorted_categories = []
                    sorted_numbers = []

                    category_list = Custom.objects.filter(Q(user_id=1) | Q(user_id=request.user.id)).order_by('name')
                    print('Category List: {}'.format(category_list))

                    total_categories = request.user.task_set.order_by('category')

                    for cat in total_categories:
                        if cat.category not in total_categories_list:
                            total_categories_list.append(cat.category)

                    print('Unique Category Numbers: {}'.format(total_categories_list))

                    for num in total_categories_list:
                        temp_name = str(Custom.objects.filter(Q(user_id=1) | Q(user_id=request.user.id)).filter(value=num)[0].name)
                        sorted_categories.append([temp_name, num])

                    sorted_categories = sorted(sorted_categories)

                    for i in range(len(sorted_categories)):
                        sorted_numbers.append(sorted_categories[i][1])

                    print('Sorted Unique Category Numbers: {}'.format(sorted_numbers))

                    for j in range(len(sorted_numbers)):
                        if task.category == sorted_numbers[j]:
                            response['link_number'] = j
                            break

                    response['list_number'] = total_categories.__len__() - 1
                    print('Total Number of Tasks: {}'.format(response['list_number']))
                else:
                    print('Only 1 task in the category')

                    response['new_category'] = True

            print('Time Delta: {}'.format(task.time_delta))
            print('Due Date: {}'.format(task.due_date))

            task.save()
            print('Task {} (id: {}) Saved'.format(task.name, task.id))

            response['name'] = task.name
            print(response['name'])
            response['id'] = task.id
            response['category'] = task.category
            response['frequency'] = task.frequency_formatted()
            print('Frequency_Formatted: {}'.format(task.frequency_formatted()))
            response['importance'] = task.importance_formatted()

            response['due_year'] = task.due_date.year
            response['due_month'] = task.due_date.month
            response['due_day'] = task.due_date.day
            response['due_hour'] = task.due_date.hour
            response['due_minute'] = task.due_date.minute

            response['validation_error'] = False
            response['tracking'] = task.en_smartTRACK == 1

            # print("Elapsed time: {} ms".format(int((timezone.now() - elapsed).microseconds / 1000)))
            print('Returning Successful Json Response')
            return JsonResponse(response)
        else:
            response['validation_error'] = True
            response['date'] = not valid_datetime

            print('Form Validation Error: {}'.format(response['validation_error']))
            print('Date is not valid: {}'.format(response['date']))

            # print("Elapsed time: {} ms".format(int((timezone.now() - elapsed).microseconds / 1000)))
            print('Returning Error Json Response')
            return JsonResponse(response)


# Profile Page.  Display tasks and allow for creation, acknowledgment, and editing of tasks.
@login_required
def profile(request):
    print('\n***Profile Requested***')
    sorted_categories = []
    total_categories_list = []
    sorted_numbers = []
    slice_list = []
    main_category = {}
    low = 0

    # Custom category population of the task form
    category_list = Custom.objects.filter(Q(user_id=1) | Q(user_id=request.user.id)).order_by('name')
    print('Category List: {}'.format(category_list))

    total_categories = request.user.task_set.order_by('category')

    for cat in total_categories:
        if cat.category not in total_categories_list:
            total_categories_list.append(cat.category)

    print('Unique Category Numbers: {}'.format(total_categories_list))

    for num in total_categories_list:
        name = str(Custom.objects.filter(Q(user_id=1) | Q(user_id=request.user.id)).filter(value=num)[0].name)
        sorted_categories.append([name, num])

    sorted_categories = sorted(sorted_categories)

    for i in range(len(sorted_categories)):
        sorted_numbers.append(sorted_categories[i][1])

    print('Sorted Unique Category Numbers: {}'.format(sorted_numbers))
    print('Sorted List of List: {}'.format(sorted_categories))

    # starting queryset with 0 values so I can append to it
    object_list = request.user.task_set.exclude(user_id=request.user.id)

    for num in sorted_numbers:
        object_list = list(chain(object_list, request.user.task_set.filter(category=num).order_by('due_date')))

    main_category_list = request.user.task_set.all()

    for task in main_category_list:
        key = str(Custom.objects.filter(Q(user_id=1) | Q(user_id=request.user.id)).filter(value=task.category)[0].name)

        if key in main_category:
            main_category[key] += 1
        else:
            main_category['{}'.format(key)] = 1

    main_category = sorted(main_category.items())

    print('Sorted Main Category: {}'.format(main_category))

    # list of objects - alphabetical for the native categories, then alphabetical for the custom categories
    print('Object List: {}'.format(object_list))

    for num in range(len(main_category)):
        high = int(main_category[num][1]) + low
        slice_list.append('{}:{}'.format(low, high))
        low = high

    print('Slice List: {}'.format(slice_list))

    # checking if the category just got its first task
    new_category = -1

    for time_task in main_category_list:
        if (timezone.now() - time_task.created_date).total_seconds() < 65:
            if request.user.task_set.filter(category=time_task.category).__len__() == 1:
                new_category = str(Custom.objects.filter(Q(user_id=1) | Q(user_id=request.user.id)).filter(value=time_task.category)[0].name)
                print('New Expanded Category: {}'.format(new_category))

    return render(request, 'reminder/profile.html', {'category_list': category_list, 'main_category': main_category,
                                                     'object_list': object_list, 'slice_list': slice_list, 'new_category': new_category})


# form_category function.  Called when the default category is changed
def form_category(request):
    print('\n***Form_Category Requested***')
    num = int(request.POST.get('category'))
    print('Category number: {}'.format(num))

    category_list = Task.objects.filter(user_id=1).filter(category=num).order_by('id')
    response = {}
    name_list = []
    count = 1

    for task in category_list:
        name_list.append(count)
        response[name_list[count - 1]] = task.name
        count += 1

    print('Json Response: {}'.format(response))
    print('Returning Json Response')
    return JsonResponse(response)

# form_name function.  Called when the default category is changed
def form_name(request):
    print('\n***Form_Name Requested***')
    num = int(request.POST.get('category'))
    position = int(request.POST.get('position'))
    offset = int(int(request.POST.get('offset')) / 60)
    print('Category: {}\nId: {}\nOffset: {}'.format(num, position, offset))
    response = {}

    category_list = Task.objects.filter(user_id=1).filter(category=num).order_by('id')
    count = 1

    for task in category_list:
        if position == count:
            break
        count += 1

    print('Requested Default Task: {}; id: {}'.format(task.name, task.id))

    response['id'] = task.id
    response['name'] = task.name
    response['category'] = task.category
    # response['en_smartTRACK'] = task.en_smartTRACK
    response['choice'] = task.choice
    response['frequency_int'] = task.frequency_int
    response['frequency_choice'] = task.frequency_choice

    due_date = task.due_date + datetime.timedelta(hours=0-offset)

    response['due_date'] = '{}/{}/{}'.format(due_date.month, due_date.day, due_date.year)
    print('Due Date MM/DD/YYYY: {}'.format(response['due_date']))
    response['due_time'] = int(task.due_date.hour - offset)
    print('Due Time: {}'.format(response['due_time']))
    response['importance'] = task.importance

    print('Returning Json Response')
    return JsonResponse(response)


# Profile Settings Page.  Display settings form and allow form saving.
@login_required
def profile_settings(request):
    print('\n***Settings Requested***')
    settings_list = []
    object_list = request.user.task_set.all().order_by('name')

    for obj in object_list:
        cat_name = Custom.objects.filter(Q(user_id=1) | Q(user_id=request.user.id)).filter(value=obj.category)[0].name
        print(cat_name)
        settings_list.append([obj.name, cat_name, obj.id])

    print('Settings List: {}'.format(settings_list))

    if request.method == 'POST':
        post = request.POST
        print("method == 'POST'\nPOST data: {}".format(post))

        data = request.user
        data.first_name = post.get('first_name')
        data.last_name = post.get('last_name')

        data.userprofile.en_notifications = post.get('push') == 'on'
        data.userprofile.save()
        data.save()

        count = request.user.task_set.count()

        for i in range(0, count):
            num = int(post.get('task_{}'.format(i)))

            if num > -1:
                task = request.user.task_set.get(pk=num)
                print('Deleting Task: {}'.format(task.name))
                task.delete()

        return HttpResponseRedirect('/profile/')

    return render(request, 'reminder/settings.html', {'settings_list': settings_list})


# Registration Page.  If the form is successfully completed, register the user and log them in.
# This cache control forces the browser to make a request to the server
@cache_control(no_cache=True, must_revalidate=True)
def register(request):
    print('\n***Register Requested***')
    # Set to False initially. Code changes value to True when registration succeeds.
    registered = False

    if request.method == 'POST':
        form = UserForm(data=request.POST)
        print("method == 'POST'\nPOST data: {}".format(form))

        if form.is_valid() and request.POST['password'] == request.POST['retype_password']:
            user = form.save()

            # Now we hash the password with the set_password method then we can update the user object.
            user.set_password(user.password)
            user.save()

            # make a new UserProfile tied to the user and save it
            pro = UserProfile(user=user)
            pro.save()

            # update the variable to tell the template registration was successful and log the user in
            registered = True

            # Send an email
            # send_mail(subject, message, from_email, to_list, fail_silently=True)
            subject = 'Thanks for registering with AwhileSince, {}'.format(user.username)
            message = 'To start enjoying all that AwhileSince has to offer simply login and get started.<nrhttp://www.AwhileSince.com/login'
            from_email = settings.EMAIL_HOST_USER
            to_list = [user.email, settings.EMAIL_HOST_USER]

            send_mail(subject, message, from_email, to_list, fail_silently=False)

            login(request, authenticate(username=request.POST['username'], password=request.POST['password']))
        else:
            print('Form Errors: {}'.format(form.errors))
    else:
        form = UserForm(initial={'username': '', 'first_name': '', 'last_name': '', 'email': '\n', 'password': ''})

    return render(request, 'reminder/register.html', {'form': form, 'registered': registered})


# About Us Page.  Display the page.
def about(request):
    print('\n***About_Us Requested***')
    return render(request, 'reminder/about.html')


# Login Page.  If account is enabled and activated, log the user in.
def user_login(request):
    print('\n***User_Login Requested***')
    if request.method == 'POST':
        form = PasswordForm(data=request.POST)

        if form.is_valid():
            user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])

            # if matching credentials were found
            if user:
                if user.is_active:
                    # If the account is valid and active, log the user in
                    login(request, user)
                    return HttpResponseRedirect('/profile/')
                else:
                    # returns HttpResponse("Your Awhile Since account is disabled.")
                    return render(request, 'reminder/login.html', {'feedback': 'Your Awhile Since account is disabled', 'form': form})
            else:
                # print invalid username and password to the terminal and tell the user
                print("Invalid login details: {}, {}".format(form.cleaned_data['username'], form.cleaned_data['password']))
                return render(request, 'reminder/login.html', {'feedback': 'Invalid login details supplied', 'form': form})
    else:
        form = PasswordForm(initial={'username': '', 'password': ''})

    return render(request, 'reminder/login.html', {'form': form})


# Logout Page.  Log the user out.
@login_required
def user_logout(request):
    print('\n***User_Logout Requested***')

    logout(request)

    return HttpResponseRedirect('/')

# Custom Category Page.  Display the form on the page with initial values.
@login_required
def custom_category(request):
    print('\n***Custom_Category Requested***')

    category_list = Custom.objects.filter(Q(user_id=1) | Q(user_id=request.user.id)).order_by('name')

    if request.method == 'POST':
        post = request.POST
        print("method == 'POST'\nPOST data: {}".format(post))

        count = Custom.objects.filter(user_id=request.user.id)

        for category in count:
            num = int(post.get('custom' + str(category.id)))

            if num > -1:
                print('Delete Custom Category: {}'.format(category.name))

                changed = request.user.task_set.filter(category=category.value)

                for task in changed:
                    task.category = 1
                    task.save()

                    print('Task {} category changed from {} to 1'.format(task.name, num))

                category.delete()

        custom = str(post.get('category_custom'))

        if custom:
            print('Custom Category Name: {}'.format(custom))
            check = True
            high = 6

            for category in category_list:
                if high < category.value:
                    high = category.value

                if custom.lower() == category.name.lower():
                    check = False
                    break

            if check:
                high += 1
                request.user.custom_set.create(name=custom, value=high)

                print('Create a new category with: {}, {}'.format(custom, high))

        return HttpResponseRedirect('/profile/')

    return render(request, 'reminder/custom_category.html', {'category_list': category_list})


# Pre-Made Actions Page.  Display the form on the page with initial values.
@login_required
def premade_action(request):
    print('\n***Premade_Action Requested***')
    category_list = Custom.objects.filter(Q(user_id=1) | Q(user_id=request.user.id)).order_by('name')

    category_general = Task.objects.filter(user_id=1).filter(category=1).order_by('id')

    if request.method == 'POST':
        post = request.POST
        print("method == 'POST'\nPOST data: {}".format(post))

        default = Task.objects.get(pk=int(request.POST.get('task_id')))

        temp_time = timezone.now() - datetime.timedelta(seconds=timezone.now().second, microseconds=timezone.now().microsecond)
        choice = default.choice

        due_date = temp_time

        if choice == 1:
            due_date = default.due_date
        elif choice == 2:
            due_date += datetime.timedelta(seconds=default.time_delta)

        task = request.user.task_set.create(name=default.name, en_smartTRACK=default.en_smartTRACK, created_date=temp_time,
                                                last_date=temp_time, due_date=due_date, choice=choice, frequency_int=default.frequency_int,
                                                frequency_choice=default.frequency_choice, category=default.category, importance=default.importance,
                                                time_delta=default.time_delta)

        task.save()

        print('Added {} (id: {}) to the profile'.format(task.name, task.id))

        return HttpResponseRedirect('/profile/')

    return render(request, 'reminder/premade_action.html', {'category_list': category_list, 'category_general': category_general})
