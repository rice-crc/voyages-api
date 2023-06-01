# Generated by Django 4.2.1 on 2023-06-01 15:24

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='SavedQuery',
            fields=[
                ('id', models.CharField(max_length=8, primary_key=True, serialize=False)),
                ('hash', models.CharField(db_index=True, default='', max_length=255)),
                ('query', models.TextField()),
                ('is_legacy', models.BooleanField(default=True)),
            ],
        ),
    ]
