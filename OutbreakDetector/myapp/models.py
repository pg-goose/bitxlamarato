from django.utils.translation import gettext_lazy as _
from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Escola(models.Model):
    nom = models.CharField(max_length=100)
    regio = models.CharField(max_length=100)
    municipi = models.CharField(max_length=100)
    lat = models.FloatField(default=41.41810362181554)
    lon = models.FloatField(default=2.151507746987765)

    def __str__(self):
        return self.nom

class Curs(models.Model):
    nom = models.CharField(max_length=100)
    numAlumnes = models.IntegerField()
    edatMitja = models.IntegerField()
    escola = models.ForeignKey(Escola, on_delete=models.CASCADE)

    def __str__(self):
        return self.nom

class Informe(models.Model):
    class Simptoma(models.TextChoices):
        MAL_DE_PANXA = "MAL_DE_PANXA", _("Mal De Panxa")
        CALFREDS = "CALFREDS", _("Calfreds")
        MAL_DE_CAP = "MAL_DE_CAP", _("Mal De Cap")
        MAL_DE_COLL = "MAL_DE_COLL", _("Mal De Coll")
        MOCS = "MOCS", _("Mocs")
        NAS_TAPAT = "NAS_TAPAT", _("Nas Tapat")
        ESTERNUT = "ESTERNUT", _("Esternut")
        VOMITS = "VOMITS", _("Vomits")
        TOS = "TOS", _("Tos")
        ALTRES = "ALTRES", _("Altres")

    data = models.DateField()
    curs = models.ForeignKey(Curs, on_delete=models.CASCADE)
    simptoma = models.CharField(
        max_length=50,
        choices=Simptoma.choices,
        default=Simptoma.ALTRES,
    )
