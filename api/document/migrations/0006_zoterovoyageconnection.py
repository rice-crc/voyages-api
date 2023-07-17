# Generated by Django 4.2.1 on 2023-07-17 18:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('voyage', '0005_voyage_human_reviewed'),
        ('document', '0005_zoterosource_notes'),
    ]

    operations = [
        migrations.CreateModel(
            name='ZoteroVoyageConnection',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('voyage', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='voyage_zotero_connections', to='voyage.voyage')),
                ('zotero_source', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='zotero_voyage_connections', to='document.zoterosource')),
            ],
            options={
                'unique_together': {('zotero_source', 'voyage')},
            },
        ),
    ]