# Generated by Django 3.2.5 on 2021-07-28 02:26

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='PVSystem',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(help_text='Enter the PV System name as it appears on the monitoring portal', max_length=128, unique=True)),
                ('inverter', models.CharField(choices=[('SM', 'SMA'), ('FR', 'Fronius'), ('SO', 'SolarEdge'), ('SU', 'Sungrow'), ('X', 'Other'), ('NA', 'Not Applicable')], default='X', max_length=2, verbose_name='Inverter Manufacturer')),
                ('link_to_portal', models.URLField(blank=True, null=True, verbose_name='Link to Inverter Portal')),
                ('link_to_salesforce', models.URLField(blank=True, null=True, verbose_name='Link to Salesforce Project Opportunity')),
                ('dc_size', models.DecimalField(blank=True, decimal_places=3, max_digits=8, null=True)),
                ('ac_size', models.DecimalField(blank=True, decimal_places=3, max_digits=8, null=True)),
                ('vendor', models.CharField(blank=True, help_text='Enter the vendor name (recommend to enter the name as it appears on Salesforce)', max_length=128, null=True)),
            ],
            options={
                'verbose_name': 'PV System',
                'verbose_name_plural': 'PV Systems',
                'ordering': ['inverter', 'name'],
            },
        ),
    ]