# Generated by Django 5.2 on 2025-04-23 18:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0013_area_salajuntas_empleado_invitado_reservacion'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='reservacion',
            name='area',
        ),
    ]
