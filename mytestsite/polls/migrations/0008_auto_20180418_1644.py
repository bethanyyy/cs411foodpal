# Generated by Django 2.0.3 on 2018-04-18 21:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0007_auto_20180418_1406'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sharedorder',
            name='status',
            field=models.CharField(default='unfulfilled', max_length=20),
        ),
    ]
