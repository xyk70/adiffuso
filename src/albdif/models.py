from django.contrib.auth.models import User
from django.db import models
from django.db.models import CharField
from django.core.exceptions import ValidationError


class Visitatore(models.Model):
    """
    Visitatore:
    persona che effettua la registrazione al sito per effettuare la prenotazione
    """
    registrazione = models.DateTimeField("data registrazione")
    utente = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta():
        verbose_name = "Visitatore"
        verbose_name_plural = "Visitatori"

    def __str__(self):
        return f"{self.utente.last_name} {self.utente.first_name}"


class Host(models.Model):
    """
    Host:
    persona o azienda che effettua la registrazione per accedere ai servizi hosting dell'AD
    """
    registrazione = models.DateTimeField("data registrazione")
    utente = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta():
        verbose_name = "Host"
        verbose_name_plural = "Host"

    def __str__(self):
        return f"{self.utente.last_name} {self.utente.first_name}"


class Proprieta(models.Model):
    """
    Proprietà:
    l'albergo diffuso di proprietà di un host necessario per collezionare le camere da affittare
    """
    host = models.ForeignKey(Host, on_delete=models.CASCADE)
    descrizione = models.CharField(max_length=200)
    principale = models.BooleanField(default=False, help_text="Indica se è l'AD principale")

    class Meta():
        verbose_name = "Proprietà"
        verbose_name_plural = "Proprietà"

    def __str__(self):
        return f"{self.descrizione}"
    
    def clean(self):
        if self.principale and Proprieta.objects.filter(principale=True).exclude(id=self.id).exists():
            raise ValidationError("Esiste già una proprietà principale.")

    def save(self, *args, **kwargs):
        self.clean()
        super(Proprieta, self).save(*args, **kwargs)
        

class Camera(models.Model):
    """
    Camera:
    ogni camera fa parte di una proprietà
    """
    proprieta = models.ForeignKey(Proprieta, on_delete=models.CASCADE)
    nome = models.CharField(max_length=100, default="... inserire un nickname")
    descrizione = models.CharField(max_length=1000)
    services = models.JSONField(default={
            "toilette": True,
            "wifi": True,
            "tv": True,
            "aria condizionata": True,
            "minibar": False
        }, help_text="Servizi offerti nella camera, ad esempio: toilette, wifi, phon, etc.")

    class Meta():
        verbose_name = "Camera"
        verbose_name_plural = "Camere"

    def __str__(self):
        return f"{self.nome} di {self.proprieta}"

    @property
    def image(self):
        "ritorna l'elenco delle foto della camera"
        return Foto.objects.filter(camera=self.pk).first()

class Foto(models.Model):
    """
    Foto:
    ogni foto può essere riferita o ad una camera o alla proprietà
    """
    descrizione = CharField(max_length=100)
    camera = models.ForeignKey(Camera, on_delete=models.CASCADE, null=True, blank=True)
    proprieta = models.ForeignKey(Proprieta, on_delete=models.CASCADE, null=True, blank=True)
    file = models.FileField(blank=True, upload_to='foto_camera')

    class Meta():
        verbose_name = "Foto"
        verbose_name_plural = "Foto"

    def __str__(self):
        if self.camera:
            return f"{self.descrizione} di {self.camera} - camera: "
        else:
            return f"{self.descrizione} di {self.proprieta} - proprietà: "


class Prenotazione(models.Model):
    """
    Prenotazione:
    la prenotazione viene eseguita da un visitatore per una camera di una proprietà
    """

    PRENOTATA = "PR"
    CANCELLATA = "CA"
    PAGATA = "PG"

    STATO_PRENOTAZIONE = [
        (PRENOTATA, "Prenotata"),
        (CANCELLATA, "Cancellata"),
        (PAGATA, "Pagata"),
    ]

    visitatore = models.ForeignKey(Visitatore, on_delete=models.CASCADE)
    camera = models.ForeignKey(Camera, on_delete=models.CASCADE)
    data_prenotazione = models.DateTimeField()
    stato_prenotazione = models.CharField(max_length=2, choices=STATO_PRENOTAZIONE, default=PRENOTATA)
    richiesta = models.CharField(max_length=1000, null=True, blank=True, help_text="richiesta aggiuntiva del cliente")

    class Meta():
        verbose_name = "Prenotazione"
        verbose_name_plural = "Prenotazioni"

    def __str__(self):
        return f"{self.id} {self.visitatore} {self.camera} {self.stato_prenotazione}"


class CalendarioPrenotazione(models.Model):
    """
    CalendarioPrenotazione:
    registra i periodi relativi ad una prenotazione
    """
    prenotazione = models.ForeignKey(Prenotazione, on_delete=models.CASCADE)
    data_inizio = models.DateField()
    data_fine = models.DateField()

    class Meta():
        verbose_name = "Calendario della prenotazione"
        verbose_name_plural = "Calendario della prenotazione"

    def __str__(self):
        return f"{self.prenotazione} {self.data_inizio} {self.data_fine}"


class Stagione(models.Model):
    """
    Stagione:
    definisce le stagioni (periodi) che determinano poi i prezzi
    """
    stagione = models.CharField(max_length=50)
    data_inizio = models.DateField()
    data_fine = models.DateField()

    class Meta():
        verbose_name = "Stagione"
        verbose_name_plural = "Stagioni"

    def __str__(self):
        return f"{self.stagione} {self.data_inizio} {self.data_fine}"


class PrezzoCamera(models.Model):
    """
    PrezzoCamera:
    indica il prezzo della camera relativo ad ogni stagione
    """
    camera = models.ForeignKey(Camera, on_delete=models.CASCADE)
    stagione = models.ForeignKey(Stagione, on_delete=models.CASCADE)
    prezzo = models.DecimalField(max_digits=7, decimal_places=2)

    class Meta():
        verbose_name = "Prezzo della camera"
        verbose_name_plural = "Prezzo della camere"

    def __str__(self):
        return f"{self.camera} {self.stagione} {self.prezzo}"