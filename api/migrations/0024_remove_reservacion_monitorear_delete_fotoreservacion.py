# Generated by Django 5.2 on 2025-06-12 00:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0023_remove_reservacion_detectar_personas_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='reservacion',
            name='monitorear',
        ),
        migrations.DeleteModel(
            name='FotoReservacion',
        ),
    ]
