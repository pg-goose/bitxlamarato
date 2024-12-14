from django.db import models

# Create your models here.
class Escola(models.Model):
    nom = models.CharField(max_length=100)
    regio = models.CharField(max_length=100)
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
        MAL_DE_COLL = "MAL_DE_COLL", _("Mal De_COLL")
        MOCS = "MOCS", _("MOCS")
        NAS_TAPAT = "NAS_TAPAT", _("NAS_TAPAT")
        ESTERNUT = "ESTERNUT", _("ESTERNUT")
        VOMITS = "VOMITS", _("VOMITS")
        TOS = "TOS", _("TOS")
        ALTRES = "ALTRES", _("ALTRES")
        
        
        
        
        
        
        
        
        


    data = models.DateField()
    curs = models.ForeignKey(Curs, on_delete=models.CASCADE)
    simptoma = 