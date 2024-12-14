from django.utils.translation import gettext_lazy as _
from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Regio(models.Model):
    nom = models.CharField(max_length=100)
    codi = models.IntegerField()

    def __str__(self):
        return self.nom

class Escola(models.Model):
    nom = models.CharField(max_length=100)
    regio = models.ForeignKey(Regio, on_delete=models.CASCADE)
    municipi = models.CharField(max_length=100)

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

class AtencioPrimaria(models.Model):
    data = models.DateField()
    setmana_epidemiologica = models.IntegerField()
    any = models.IntegerField()
    regio = models.ForeignKey(Regio, on_delete=models.CASCADE)
    codi_ambit = models.CharField(max_length=100)
    nom_ambit = models.CharField(max_length=100)
    codi_abs = models.CharField(max_length=100)
    nom_abs = models.CharField(max_length=100)
    diagnostic = models.CharField(max_length=100)
    sexe = models.CharField(max_length=100)
    grup_edat = models.CharField(max_length=100)
    index_socioeconomic = models.IntegerField()
    casos = models.IntegerField()
    poblacio = models.IntegerField()