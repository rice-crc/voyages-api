# Generated by Django 4.0 on 2022-03-16 18:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('voyage', '0001_initial'),
        ('past', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='enslaved',
            name='sources',
            field=models.ManyToManyField(related_name='+', through='past.EnslavedSourceConnection', to='voyage.VoyageSources'),
        ),
    ]
