# Generated by Django 2.0.3 on 2018-03-24 17:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='FoodItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(max_length=300)),
                ('price', models.DecimalField(decimal_places=2, max_digits=5)),
                ('foodName', models.CharField(max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='Include',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('foodName', models.CharField(max_length=20)),
                ('restaurantName', models.CharField(max_length=30)),
                ('restaurantLocation', models.CharField(max_length=100)),
                ('time', models.DateTimeField()),
                ('orderLocation', models.CharField(max_length=100)),
                ('userID', models.CharField(max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('location', models.CharField(max_length=100)),
                ('time', models.DateTimeField()),
                ('userID', models.CharField(max_length=10)),
                ('sharedOrderID', models.CharField(max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='Restaurant',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
                ('type', models.CharField(max_length=30)),
                ('location', models.CharField(max_length=100)),
                ('priceRange', models.CharField(max_length=30)),
                ('hour', models.CharField(max_length=30)),
                ('image', models.CharField(max_length=1000, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='SharedOrder',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', models.DateTimeField()),
                ('orderLocation', models.CharField(max_length=100)),
                ('userID', models.CharField(max_length=10)),
                ('pickupPoint', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.CharField(max_length=10, primary_key=True, serialize=False)),
                ('email', models.CharField(max_length=20)),
                ('name', models.CharField(max_length=30)),
                ('preference', models.CharField(max_length=30)),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='sharedorder',
            unique_together={('time', 'orderLocation', 'userID')},
        ),
        migrations.AlterUniqueTogether(
            name='order',
            unique_together={('location', 'time', 'userID')},
        ),
        migrations.AlterUniqueTogether(
            name='include',
            unique_together={('foodName', 'restaurantName', 'restaurantLocation', 'time', 'orderLocation', 'userID')},
        ),
        migrations.AddField(
            model_name='fooditem',
            name='restaurant',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='polls.Restaurant'),
        ),
        migrations.AlterUniqueTogether(
            name='fooditem',
            unique_together={('foodName', 'restaurant')},
        ),
    ]
