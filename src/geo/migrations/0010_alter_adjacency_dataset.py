# Generated by Django 4.0.2 on 2022-06-10 21:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('geo', '0009_alter_adjacency_options_adjacency_dataset'),
    ]

    operations = [
        migrations.AlterField(
            model_name='adjacency',
            name='dataset',
            field=models.IntegerField(null=True, verbose_name='trans-atlantic (0), intra-american (1), intra-african (2)'),
        ),
    ]
