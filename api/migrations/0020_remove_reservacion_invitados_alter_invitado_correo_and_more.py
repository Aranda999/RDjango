# Generated by Django 5.2 on 2025-05-21 00:32

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0019_reservacion_enviar_correo'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='reservacion',
            name='invitados',
        ),
        migrations.AlterField(
            model_name='invitado',
            name='correo',
            field=models.EmailField(max_length=254, unique=True),
        ),
        migrations.AlterField(
            model_name='invitado',
            name='id_area',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='invitados', to='api.area'),
        ),
        migrations.AlterField(
            model_name='salajuntas',
            name='id_sala',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
        migrations.CreateModel(
            name='ReservacionInvitado',
            fields=[
                ('id_reservacion_invitado', models.AutoField(primary_key=True, serialize=False)),
                ('invitado', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.invitado')),
                ('reservacion', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.reservacion')),
            ],
            options={
                'db_table': 'reservacion_invitados',
                'unique_together': {('reservacion', 'invitado')},
            },
        ),
    ]
