# Generated by Django 4.0.2 on 2022-06-10 21:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('geo', '0010_alter_adjacency_dataset'),
    ]

    operations = [
        migrations.AddField(
            model_name='location',
            name='dataset',
            field=models.IntegerField(null=True, verbose_name='trans-atlantic (0), intra-american (1), intra-african (2)'),
        ),
    ]
