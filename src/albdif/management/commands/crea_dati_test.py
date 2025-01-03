from datetime import date, timedelta

from django.core.management.base import BaseCommand
from albdif.models import Proprieta, Camera, Prenotazione, Servizio, Visitatore, User

from albdif.utils.fixtures import ProprietaFactory, CameraFactory, PrenotazioneFactory, \
    CalendarioPrenotazioneFactory, StagioneFactory, FotoFactory, ProprietaPrincFactory, UserFactory, VisitatoreFactory, \
    ServizioFactory, ServizioCameraFactory


class Command(BaseCommand):
    help = 'Crea dati di test'

    def handle(self, *args, **kwargs):

        # Servizi
        #servs = ServizioFactory.build_batch(5)
        #for s in servs:
        #    s.save()
        servs = ['toilette', 'wifi', 'phon', 'minibar', 'aria condizionata']
        for s in servs:
            ServizioFactory.create(descrizione_servizio=s)

        # Creazione visitatori
        utenti = UserFactory.build_batch(3)
        for u in utenti:
            u.save()
        for t in User.objects.all():
            VisitatoreFactory.create(utente=t)

        # Proprietà principale
        ProprietaPrincFactory.create()

        # Creazione altre proprieta
        for _ in range(3):
            p = ProprietaFactory.create()
            FotoFactory.create(proprieta=p)

        # Creazione camere
        for proprieta in Proprieta.objects.all():
            for _ in range(4):
                c = CameraFactory.create(proprieta=proprieta)
                for s in Servizio.objects.all():
                    ServizioCameraFactory.create(camera=c, servizio=s)
                FotoFactory.create(camera=c)
                FotoFactory.create(camera=c)

        # Creazione stagioni
        stagioni = [
            ('Bassa', date(2025, 1, 1), date(2025, 2, 28), 50.00),
            ('Media', date(2025, 3, 1), date(2025, 5, 31), 75.00),
            ('Bassa', date(2025, 6, 1), date(2025, 9, 30), 100.00),
            ('Media', date(2025, 10, 1), date(2025, 12, 31), 75.00),
            ('Bassa', date(2026, 1, 1), date(9999, 12, 31), 85.00)
        ]
        
        for stagione, data_inizio, data_fine, prezzo_default in stagioni:
            StagioneFactory.create(
                stagione=stagione,
                data_inizio=data_inizio,
                data_fine=data_fine,
                prezzo_default=prezzo_default
            )

        for v in Visitatore.objects.all():
            # Creazione prenotazioni
            for c in Camera.objects.all():
                PrenotazioneFactory.create(camera=c, visitatore=v)

        # Creazione calendario prenotazioni
        for p in Prenotazione.objects.all():
            CalendarioPrenotazioneFactory.create(prenotazione=p)

        # Creazione dell'utente guest
        g = UserFactory.create(username="guest")
        v = VisitatoreFactory.create(utente=g)

        c1 = Camera.objects.get(id=1)
        c2 = Camera.objects.get(id=2)
        c3 = Camera.objects.get(id=3)
        # pagata passata
        p1 = PrenotazioneFactory.create(camera=c1, visitatore=v,
                                        stato_prenotazione='PG',
                                        data_prenotazione=date(2024, 1, 1))
        CalendarioPrenotazioneFactory.create(prenotazione=p1,
                                             data_inizio=date(2024, 2, 1),
                                             data_fine=date(2024, 2, 5))

        # pagata futura
        p2 = PrenotazioneFactory.create(camera=c2, visitatore=v,
                                        stato_prenotazione='PG',
                                        data_prenotazione=date(2024, 1, 1))
        CalendarioPrenotazioneFactory.create(prenotazione=p2,
                                             data_inizio=date(2024, 1, 1),
                                             data_fine=date(2024, 1, 5))

        # prenotata futura
        p3 = PrenotazioneFactory.create(camera=c3, visitatore=v,
                                        stato_prenotazione='PR',
                                        data_prenotazione=date.today() - timedelta(days=10))
        CalendarioPrenotazioneFactory.create(prenotazione=p3,
                                             data_inizio=date.today() + timedelta(days=30),
                                             data_fine=date.today() + timedelta(days=35))

        self.stdout.write(self.style.SUCCESS('Dati di test creati con successo'))