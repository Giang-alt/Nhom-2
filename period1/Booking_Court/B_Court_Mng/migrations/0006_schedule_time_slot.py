# Generated by Django 5.1.5 on 2025-01-27 07:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('B_Court_Mng', '0005_schedule_created_at_schedule_expired_at_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='schedule',
            name='time_slot',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
    ]
