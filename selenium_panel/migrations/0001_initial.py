# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Browser',
            fields=[
                ('service_url', models.CharField(max_length=100,
                                                 serialize=False,
                                                 primary_key=True)),
                ('session_id', models.CharField(max_length=100)),
                ('username', models.CharField(max_length=100, blank=True)),
                ('platform', models.CharField(max_length=50, blank=True)),
                ('driver', models.CharField(
                    max_length=20,
                    choices=[
                        (b'firefox', b'Firefox'),
                        (b'chrome', b'Chrome'),
                        (b'edge', b'Edge'),
                        (b'safari', b'Safari')
                    ])),
                ('running_task', models.CharField(max_length=50,
                                                  null=True,
                                                  blank=True)),
            ],
        ),
    ]
