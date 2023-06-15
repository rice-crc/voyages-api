# Generated by Django 4.2.1 on 2023-06-14 21:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('voyage', '0007_rename_label_nationality_name_and_more'),
        ('past', '0006_alter_enslaverinrelation_enslaver_alias_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='enslaved',
            name='voyage',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='voyage_enslaved_people', to='voyage.voyage'),
        ),
    ]
