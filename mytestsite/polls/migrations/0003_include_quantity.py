# Generated by Django 2.0.3 on 2018-03-24 23:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0002_auto_20180324_1605'),
    ]

    operations = [
        migrations.AddField(
            model_name='include',
            name='quantity',
            field=models.IntegerField(default=1),
        ),
    ]