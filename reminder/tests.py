from django.test import TestCase
from django.http import HttpRequest
import datetime
from django.utils import timezone
from .models import UserProfile, Task, History, Custom
from django.core.urlresolvers import reverse, resolve


class ModelTests(TestCase):
    """Test the models with prepopulated data"""
    def test_importance_formatted(self):
        importance = 1
        importance_task = Task(importance=importance)
        self.assertEqual(importance_task.importance_formatted(), 'Trivial')

        importance = 2
        importance_task = Task(importance=importance)
        self.assertEqual(importance_task.importance_formatted(), 'Minor')

        importance = 3
        importance_task = Task(importance=importance)
        self.assertEqual(importance_task.importance_formatted(), 'Moderate')

        importance = 4
        importance_task = Task(importance=importance)
        self.assertEqual(importance_task.importance_formatted(), 'Significant')

        importance = 5
        importance_task = Task(importance=importance)
        self.assertEqual(importance_task.importance_formatted(), 'Critical')

    def test_frequency_formatted(self):
        choice = 2
        tracking = 0
        integer = 1
        time = 5000000
        frequency_task = Task(
            frequency_choice=choice,
            en_smartTRACK=tracking,
            frequency_int=integer,
            time_delta=time
        )
        self.assertEqual(
            frequency_task.frequency_formatted(),
            'Every 8 weeks, 1 day, 20 hours'
        )

        choice = 1
        tracking = 0
        integer = 1
        time = 500000
        frequency_task = Task(
            frequency_choice=choice,
            en_smartTRACK=tracking,
            frequency_int=integer,
            time_delta=time
        )
        self.assertEqual(
            frequency_task.frequency_formatted(),
            'Every 5 days, 18 hours'
        )

        choice = 0
        tracking = 0
        integer = 1
        time = 50000
        frequency_task = Task(
            frequency_choice=choice,
            en_smartTRACK=tracking,
            frequency_int=integer,
            time_delta=time
        )
        self.assertEqual(
            frequency_task.frequency_formatted(),
            'Every 13 hours'
        )

        choice = 2
        tracking = 0
        integer = 1
        time = 1000000
        frequency_task = Task(
            frequency_choice=choice,
            en_smartTRACK=tracking,
            frequency_int=integer,
            time_delta=time
        )
        self.assertEqual(
            frequency_task.frequency_formatted(),
            'Every 1 week, 4 days, 13 hours'
        )

        choice = 1
        tracking = 0
        integer = 1
        time = 100000
        frequency_task = Task(
            frequency_choice=choice,
            en_smartTRACK=tracking,
            frequency_int=integer,
            time_delta=time
        )
        self.assertEqual(
            frequency_task.frequency_formatted(),
            'Every 1 day, 3 hours'
        )

        choice = 0
        tracking = 0
        integer = 1
        time = 10000
        frequency_task = Task(
            frequency_choice=choice,
            en_smartTRACK=tracking,
            frequency_int=integer,
            time_delta=time
        )
        self.assertEqual(
            frequency_task.frequency_formatted(),
            'Every 2 hours'
        )

    def test_choice_formatted(self):
        choice = 0
        choice_task = Task(choice=choice)
        self.assertEqual(choice_task.choice_formatted(), 'SmartTRACK')

        choice = 1
        choice_task = Task(choice=choice)
        self.assertEqual(choice_task.choice_formatted(), 'Date')

        choice = 2
        choice_task = Task(choice=choice)
        self.assertEqual(choice_task.choice_formatted(), 'Frequency')

    def test_custom(self):
        name = 'test_name'
        name_custom = Custom(name=name)

        self.assertEqual(name_custom.__str__(), name)

    def test_history(self):
        date = datetime.datetime(2016, 9, 29, 2, 48, 57, 668169)
        history_date = History(acknowledge_date=date)
        self.assertEqual(history_date.__str__(), '20160929_0248')

        date = datetime.datetime(2015, 8, 28, 11, 38, 57, 668169)
        history_date = History(acknowledge_date=date)
        self.assertEqual(history_date.__str__(), '20150828_1138')

        date = datetime.datetime(2014, 7, 27, 10, 28, 57, 668169)
        history_date = History(acknowledge_date=date)
        self.assertEqual(history_date.__str__(), '20140727_1028')


class TaskViewTests(TestCase):
    """Test the tasks with prepulated data"""
    def test_login(self):
        response = self.client.post(
            '/login/',
            {'username': 'TestUser1', 'password': '1111'}
        )
        self.assertEqual(response.status_code, 200)
        response = self.client.post(
            '/login/',
            {'username': 'failLogin', 'password': 'null'}
        )
        self.assertEqual(response.status_code, 200)

    def test_call_view_denies_anonymous(self):
        response = self.client.get('/profile/', follow=True)
        self.assertRedirects(response, '/login/?next=/profile/')
        response = self.client.post('/profile/settings/', follow=True)
        self.assertRedirects(response, '/login/?next=/profile/settings/')

    def test_call_view_loads(self):
        self.client.login(username='user', password='test')
        response = self.client.get('/profile/')
        self.assertEqual(response.status_code, 302)
