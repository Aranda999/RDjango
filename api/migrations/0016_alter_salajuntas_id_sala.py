# Generated by Django 5.2 on 2025-04-23 19:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0015_salajuntastemporal'),
    ]

    operations = [
        migrations.AlterField(
            model_name='salajuntas',
            name='id_sala',
            field=models.AutoField(primary_key=True, serialize=False, verbose_name='ID de Sala'),
        ),
    ]
