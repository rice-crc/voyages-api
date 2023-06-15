# Generated by Django 4.2.1 on 2023-06-05 21:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('voyage', '0005_remove_voyagesourcesconnection_zotero_source'),
        ('document', '0003_alter_sourcepage_iiif_baseimage_url_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='zoterosource',
            name='legacy_source',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='source_zotero_refs', to='voyage.voyagesources'),
        ),
        migrations.AddField(
            model_name='zoterosource',
            name='source_cnx',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sourcecnx_zotero_refs', to='voyage.voyagesourcesconnection'),
        ),
    ]