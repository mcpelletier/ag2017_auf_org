# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inscription', '0016_auto_20161020_1245'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='inscription',
            name='paiement',
        ),
    ]
