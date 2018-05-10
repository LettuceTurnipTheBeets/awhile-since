# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Custom',
            fields=[
                ('id', models.AutoField(primary_key=True,
                                        serialize=False,
                                        auto_created=True,
                                        verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('value', models.IntegerField(default=6)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='History',
            fields=[
                ('id', models.AutoField(primary_key=True,
                                        serialize=False,
                                        auto_created=True,
                                        verbose_name='ID')),
                ('acknowledge_date', models.DateTimeField(
                    default=django.utils.timezone.now)),
            ],
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.AutoField(primary_key=True,
                                        serialize=False,
                                        auto_created=True,
                                        verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('created_date', models.DateTimeField(
                    default=django.utils.timezone.now)),
                ('due_date', models.DateTimeField(
                    default=django.utils.timezone.now)),
                ('last_date', models.DateTimeField(
                    default=django.utils.timezone.now)),
                ('frequency_int', models.IntegerField(default=1)),
                ('frequency_choice', models.IntegerField(default=1)),
                ('category', models.IntegerField(default=1)),
                ('importance', models.IntegerField(default=3, choices=[
                 (1, 'Trivial'), (2, 'Minor'), (3, 'Moderate'), (4, 'Significant'), (5, 'Critical')])),
                ('past_due', models.BooleanField(default=True)),
                ('time_delta', models.FloatField(default=0.0)),
                ('choice', models.IntegerField(default=0)),
                ('acknowledge_total', models.IntegerField(default=0)),
                ('en_smartTRACK', models.IntegerField(default=0)),
                ('omit_total', models.IntegerField(default=0)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(primary_key=True,
                                        serialize=False, auto_created=True, verbose_name='ID')),
                ('email_alerts', models.BooleanField(default=True)),
                ('join_date', models.DateTimeField(
                    default=django.utils.timezone.now)),
                ('score', models.IntegerField(default=0)),
                ('en_notifications', models.BooleanField(default=True)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='history',
            name='task',
            field=models.ForeignKey(to='reminder.Task'),
        ),
    ]
