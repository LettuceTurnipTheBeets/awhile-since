from django.test import TestCase
import datetime
from django.utils import timezone
from .models import UserProfile, Task, History
from django.core.urlresolvers import reverse
# Create your tests here.

class ModelTests(TestCase):

    def test_importance_formatted(self):
        importance = 3
        importance_task = Task(importance=importance)

        self.assertEqual(importance_task.importance_formatted(), 'Moderate')


class CreateTaskViewTests(TestCase):

    def test_login(self):
        response = self.client.post('/login/', {'username': 'TestUser1', 'password': '1111'})
        self.assertEqual(response.status_code, 200)




