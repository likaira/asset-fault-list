#Define model choices in this file
#Model - PVSystem; field - inverter
SMA = 'SM'
FRONIUS = 'FR'
SOLAREDGE = 'SO'
SUNGROW = 'SU'
OTHER = 'X'
NOT_APPLICABLE = 'NA'
INVERTER_MANUFACTURER_CHOICES = [
    (SMA, 'SMA'),
    (FRONIUS, 'Fronius'),
    (SOLAREDGE, 'SolarEdge'),
    (SUNGROW, 'Sungrow'),
    (OTHER, 'Other'),
    (NOT_APPLICABLE, 'Not Applicable'),
]

#Model - ErrorLog; field - fault_type
