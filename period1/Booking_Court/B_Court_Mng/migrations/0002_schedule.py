# Generated by Django 5.1.5 on 2025-01-19 17:16

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('B_Court_Mng', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Schedule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_time', models.DateTimeField()),
                ('end_time', models.DateTimeField()),
                ('schedule_type', models.CharField(choices=[('Fixed', 'Lịch cố định'), ('Daily', 'Đặt lịch ngày'), ('Flexible', 'Lịch linh hoạt')], max_length=20)),
                ('court', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='B_Court_Mng.court')),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
