# Generated by Django 4.0.2 on 2022-07-27 16:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('docs', '0004_doc_citation'),
    ]

    operations = [
        migrations.AlterField(
            model_name='doc',
            name='citation',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
    ]