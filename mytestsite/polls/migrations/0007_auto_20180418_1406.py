# Generated by Django 2.0.3 on 2018-04-18 19:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0006_auto_20180418_1405'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='userID',
            field=models.IntegerField(default=1),
        ),
    ]
