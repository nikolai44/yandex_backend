# Generated by Django 3.0 on 2019-12-08 14:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('promotion', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='citizen',
            name='gender',
            field=models.IntegerField(blank=True, choices=[('Male', 'Male'), ('Female', 'Female')]),
        ),
    ]