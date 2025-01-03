import datetime

from django.contrib.auth.models import User
from django.db import models
from django.db.models import CharField, Q
from django.core.exceptions import ValidationError


class Visitatore(models.Model):
    """
    Visitatore:
    persona che effettua la registrazione al sito per effettuare la prenotazione
    """
    registrazione = models.DateTimeField("data registrazione")
    utente = models.OneToOneField(User, on_delete=models.CASCADE)

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
    utente = models.OneToOneField(User, on_delete=models.CASCADE)

    class Meta():
        verbose_name = "Host"
        verbose_name_plural = "Hosts"

    def __str__(self):
        return f"{self.utente.last_name} {self.utente.first_name}"


class Proprieta(models.Model):
    """
    Proprietà:
    l'albergo diffuso di proprietà di un host necessario per collezionare le camere da affittare
    """
    host = models.ForeignKey(Host, on_delete=models.CASCADE)
    descrizione = models.CharField(max_length=2000)
    principale = models.BooleanField(default=False, help_text="Indica se è l'AD principale")

    class Meta():
        verbose_name = "Proprietà"
        verbose_name_plural = "Proprietà"

    def __str__(self):
        return f"{self.descrizione[:20]}"
    
    def clean(self):
        if self.principale and Proprieta.objects.filter(principale=True).exclude(id=self.id).exists():
            raise ValidationError("Esiste già una proprietà principale.")

    def save(self, *args, **kwargs):
        self.clean()
        super(Proprieta, self).save(*args, **kwargs)
        

class Servizio(models.Model):
    """
    Servizio:
    definisce i servizi che possono essere forniti (differenti per ogni camera)
    """
    descrizione_servizio = models.CharField(max_length=30)

    def __str__(self):
        return f"{self.descrizione_servizio}"

    class Meta():
        verbose_name = "Servizio"
        verbose_name_plural = "Servizi"


class Camera(models.Model):
    """
    Camera:
    ogni camera fa parte di una proprietà
    """
    proprieta = models.ForeignKey(Proprieta, on_delete=models.CASCADE)
    nome = models.CharField(max_length=100, default="... inserire un nickname")
    descrizione = models.CharField(max_length=1000)
    numero_posti_letto = models.IntegerField(null=True, blank=True, default=2)

    class Meta():
        verbose_name = "Camera"
        verbose_name_plural = "Camere"

    def __str__(self):
        return f"{self.nome} di {self.proprieta}"

    @property
    def image(self):
        "ritorna l'elenco delle foto della camera"
        return Foto.objects.filter(camera=self.pk).first()

    @property
    def prezzo_bassa_stagione(self):
        "ritorna il prezzo minimo della stagione 'Bassa'"
        stagione_bassa = Stagione.objects.filter(stagione="Bassa").first()
        if stagione_bassa:
            prezzo_camera = PrezzoCamera.objects.filter(camera=self, stagione=stagione_bassa).order_by('prezzo').first()
            if prezzo_camera:
                return prezzo_camera.prezzo
            return stagione_bassa.prezzo_default
        return None


class ServizioCamera(models.Model):
    """
    ServizioCamera
    elenca tutti i servizi di una camera specificando se sono inclusi nel prezzo (incluso=True)
    o opzionali (incluso=False), in questo caso sarà visibile il prezzo
    """
    camera = models.ForeignKey(Camera, on_delete=models.CASCADE)
    servizio = models.ForeignKey(Servizio, on_delete=models.CASCADE)
    incluso = models.BooleanField(default=False)
    costo = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)

    class Meta():
        verbose_name = "Servizio camera"
        verbose_name_plural = "Servizi camera"

    def __str__(self):
        return f"{self.servizio}"

    def clean(self):
        if not self.incluso and (not self.costo or self.costo == 0):
            raise ValidationError("Se il servizio è opzionale va indicato il costo")

    def save(self, *args, **kwargs):
        self.clean()
        super(ServizioCamera, self).save(*args, **kwargs)


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
    PAGATA = "PG"
    CANCELLATA = "CA"

    STATO_PRENOTAZIONE = [
        (PRENOTATA, "Prenotata"),
        (PAGATA, "Pagata"),
        (CANCELLATA, "Cancellata"),
    ]

    PASSAGGI_STATO = [
        (PRENOTATA, PRENOTATA),
        (PRENOTATA, PAGATA),
        (PRENOTATA, CANCELLATA),
    ]

    visitatore = models.ForeignKey(Visitatore, on_delete=models.CASCADE)
    camera = models.ForeignKey(Camera, on_delete=models.CASCADE)
    data_prenotazione = models.DateTimeField()
    stato_prenotazione = models.CharField(max_length=2, choices=STATO_PRENOTAZIONE, default=PRENOTATA)
    richiesta = models.CharField(max_length=1000, null=True, blank=True, help_text="richiesta aggiuntiva del cliente")
    costo_soggiorno = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
    data_pagamento = models.DateTimeField(null=True, blank=True)
    numero_persone = models.IntegerField(null=True, blank=True, default=1)
    version = models.DateTimeField(default=datetime.datetime.now())

    class Meta():
        verbose_name = "Prenotazione"
        verbose_name_plural = "Prenotazioni"

    def __str__(self):
        return f"{self.id} {self.visitatore} {self.camera} {self.stato_prenotazione}"

    def is_valid_state_transition(self, old_state, new_state):
        return (old_state, new_state) in self.PASSAGGI_STATO

    def clean(self):
        if self.pk:
            old_state = Prenotazione.objects.get(pk=self.pk).stato_prenotazione
            if not self.is_valid_state_transition(old_state, self.stato_prenotazione):
                raise ValidationError(f"Passaggio di stato non consentito da {old_state} a {self.stato_prenotazione}")

    def save(self, *args, **kwargs):
        self.clean()
        super(Prenotazione, self).save(*args, **kwargs)


class CalendarioPrenotazione(models.Model):
    """
    CalendarioPrenotazione:
    registra i periodi relativi ad una prenotazione
    """
    prenotazione = models.ForeignKey(Prenotazione, on_delete=models.CASCADE)
    data_inizio = models.DateField(help_text="Data inizio soggiorno")
    data_fine = models.DateField(help_text="Data fine soggiorno")

    class Meta():
        verbose_name = "Calendario della prenotazione"
        verbose_name_plural = "Calendario della prenotazione"

    def __str__(self):
        return f"{self.prenotazione} {self.data_inizio} {self.data_fine}"

    def altra_prenotazione_presente(self, data_inizio, data_fine, prenotazione):
        cp = CalendarioPrenotazione.objects.filter(
            Q(data_inizio__lte=data_fine),
            Q(data_fine__gt=data_inizio),
            Q(prenotazione__camera__pk=prenotazione.camera.pk),
            ~Q(prenotazione__id=prenotazione.id)
        )
        return cp.exists()

    def clean(self):
        if self.pk:
            prenotazione = Prenotazione.objects.get(pk=self.prenotazione.pk)
            if self.altra_prenotazione_presente(self.data_inizio, self.data_fine, prenotazione):
                raise ValidationError(f"Trovata altra prenotazione nello stesso periodo")

    def save(self, *args, **kwargs):
        self.clean()
        super(CalendarioPrenotazione, self).save(*args, **kwargs)


class Stagione(models.Model):
    """
    Stagione:
    definisce le stagioni (periodi) che determinano poi i prezzi
    """
    stagione = models.CharField(max_length=50)
    data_inizio = models.DateField()
    data_fine = models.DateField()
    prezzo_default = models.DecimalField(max_digits=7, decimal_places=2, default=50)

    class Meta():
        verbose_name = "Stagione"
        verbose_name_plural = "Stagioni"

    def __str__(self):
        return f"{self.stagione} {self.data_inizio} {self.data_fine}"

    def clean(self):
        if self.data_fine < self.data_inizio:
            raise ValidationError("La data fine deve essere maggiore della data inizio")

        s = 0 if not self.id else self.id
        if Stagione.objects.filter(Q(data_inizio__lte=self.data_fine),
                                   Q(data_fine__gte=self.data_inizio),
                                   ~Q(id__exact=s)).exists():
            raise ValidationError("Le date si sovrappongono ad un'altra stagione")

    def save(self, *args, **kwargs):
        self.clean()
        super(Stagione, self).save(*args, **kwargs)


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