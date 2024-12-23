# Generated by Django 5.1.4 on 2024-12-14 17:59

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Escola',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(max_length=100)),
                ('regio', models.CharField(max_length=100)),
                ('municipi', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Curs',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(max_length=100)),
                ('numAlumnes', models.IntegerField()),
                ('edatMitja', models.IntegerField()),
                ('escola', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.escola')),
            ],
        ),
        migrations.CreateModel(
            name='Informe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data', models.DateField()),
                ('simptoma', models.CharField(choices=[('MAL_DE_PANXA', 'Mal De Panxa'), ('CALFREDS', 'Calfreds'), ('MAL_DE_CAP', 'Mal De Cap'), ('MAL_DE_COLL', 'Mal De Coll'), ('MOCS', 'Mocs'), ('NAS_TAPAT', 'Nas Tapat'), ('ESTERNUT', 'Esternut'), ('VOMITS', 'Vomits'), ('TOS', 'Tos'), ('ALTRES', 'Altres')], default='ALTRES', max_length=50)),
                ('curs', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.curs')),
            ],
        ),
    ]
