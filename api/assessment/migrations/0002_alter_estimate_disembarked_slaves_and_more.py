# Generated by Django 4.2.1 on 2024-01-18 21:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assessment', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='estimate',
            name='disembarked_slaves',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='estimate',
            name='embarked_slaves',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
