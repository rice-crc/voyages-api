# Generated by Django 4.2.1 on 2023-07-17 18:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('document', '0006_zoterovoyageconnection'),
    ]

    operations = [
        migrations.AddField(
            model_name='zoterovoyageconnection',
            name='page_range',
            field=models.CharField(blank=True, max_length=25, null=True),
        ),
    ]
