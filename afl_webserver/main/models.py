#Python Libraries Imports
import uuid

#Django Libraries Imports
from django.db import models
from django.urls import reverse

#Local libraries
from . import choices

#PV System
class PVSystem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(
        max_length=128, 
        null=False,
        blank=False,
        unique=True,
        help_text='Enter the PV System name as it appears on the monitoring portal',
    )
    inverter = models.CharField(
        max_length=2,
        choices=choices.INVERTER_MANUFACTURER_CHOICES,
        default=choices.OTHER,
        verbose_name='Inverter Manufacturer',
    )
    link_to_portal = models.URLField(null=True, blank=True, verbose_name='Link to Inverter Portal')
    link_to_salesforce = models.URLField(null=True, blank=True, verbose_name='Link to Salesforce Project Opportunity')
    dc_size = models.DecimalField(max_digits=8, decimal_places=3, null=True, blank=True)
    ac_size = models.DecimalField(max_digits=8, decimal_places=3, null=True, blank=True)
    vendor = models.CharField(
        max_length=128,
        null=True,
        blank=True,
        help_text='Enter the vendor name (recommend to enter the name as it appears on Salesforce)',
    )

    class Meta:
        verbose_name = "PV System"
        verbose_name_plural = "PV Systems"
        ordering = ['inverter','name']

    def __str__(self):
        return f'{self.name}'
    
    def get_absolute_url(self):
        return reverse('pvsystem_detail', kwargs={'pk': self.pk})

