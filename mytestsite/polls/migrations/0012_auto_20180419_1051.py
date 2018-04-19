# Generated by Django 2.0.3 on 2018-04-19 15:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0011_auto_20180418_2321'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='totalCost',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=5),
        ),
        migrations.AddField(
            model_name='restaurant',
            name='minOrderFee',
            field=models.DecimalField(decimal_places=2, default=20.0, max_digits=5),
        ),
    ]
