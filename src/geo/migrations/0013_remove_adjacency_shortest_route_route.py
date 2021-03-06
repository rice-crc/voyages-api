# Generated by Django 4.0.2 on 2022-06-14 21:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('geo', '0012_adjacency_shortest_route_alter_adjacency_dataset'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='adjacency',
            name='shortest_route',
        ),
        migrations.CreateModel(
            name='Route',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dataset', models.IntegerField(null=True, verbose_name='Dataset')),
                ('shortest_route', models.JSONField(null=True, verbose_name='Endpoint to endpoint route')),
                ('source', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sourceofroute', to='geo.location', verbose_name='Alice')),
                ('target', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='targetofroute', to='geo.location', verbose_name='Bob')),
            ],
            options={
                'verbose_name': 'Route',
                'verbose_name_plural': 'Routes',
            },
        ),
    ]
