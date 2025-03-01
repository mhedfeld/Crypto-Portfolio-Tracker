# Generated by Django 4.2.14 on 2024-07-16 10:01

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('tracker', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='HistoricalPrice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.DecimalField(decimal_places=8, max_digits=20)),
                ('timestamp', models.DateTimeField(default=django.utils.timezone.now)),
                ('cryptocurrency', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tracker.cryptocurrency')),
            ],
            options={
                'indexes': [models.Index(fields=['cryptocurrency', 'timestamp'], name='tracker_his_cryptoc_5e3c3a_idx')],
            },
        ),
    ]
