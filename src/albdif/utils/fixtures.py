from datetime import date
from typing import Any

from django.conf import settings
from django.db.models import Model

import factory.fuzzy
from factory.django import DjangoModelFactory

from albdif.models import Visitatore, Host, Proprieta, Camera, Prenotazione, CalendarioPrenotazione, Foto


class UserFactory(DjangoModelFactory):
    username = factory.Sequence(lambda n: f"test-{n}")
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    email = factory.Sequence(lambda n: f"test-{n}@adpegasus.it")
    password = "password"  # noqa

    class Meta:
        model = settings.AUTH_USER_MODEL

    @classmethod
    def _create(cls, model_class: "Model", *args: Any, **kwargs: Any) -> "User":
        """Crea oggetto e lo salva sul db"""
        if cls._meta.django_get_or_create:
            return cls._get_or_create(model_class, *args, **kwargs)

        manager = cls._get_manager(model_class)
        return manager.create_user(*args, **kwargs)


class VisitatoreFactory(DjangoModelFactory):
    utente = factory.SubFactory(UserFactory)
    registrazione = factory.fuzzy.FuzzyDate(date(2024, 1, 1), date(2025, 12, 31))

    class Meta:
        model = Visitatore


class HostFactory(DjangoModelFactory):
    utente = factory.SubFactory(UserFactory)
    registrazione = factory.fuzzy.FuzzyDate(date(2024, 1, 1), date(2025, 12, 31))

    class Meta:
        model = Host


class ProprietaPrincFactory(DjangoModelFactory):
    host = factory.SubFactory(HostFactory)
    descrizione = factory.Faker('name')
    principale = True # solo uno a True, gli altri a False

    class Meta:
        model = Proprieta


class ProprietaFactory(DjangoModelFactory):
    host = factory.SubFactory(HostFactory)
    descrizione = factory.Faker('name')
    principale = False # solo uno a True, gli altri a False

    class Meta:
        model = Proprieta


class CameraFactory(DjangoModelFactory):
    proprieta = factory.SubFactory(ProprietaFactory)
    nome = factory.Faker('name')
    descrizione = factory.Faker('name')
    #services = dict

    class Meta:
        model = Camera


STATI = ["PR", "SC", "CA", "PG"]

class PrenotazioneFactory(DjangoModelFactory):
    visitatore = factory.SubFactory(VisitatoreFactory)
    camera = factory.SubFactory(CameraFactory)
    data_prenotazione = factory.fuzzy.FuzzyDate(date(2024, 1, 1), date(2024, 12, 31))
    stato_prenotazione = factory.Iterator(STATI)
    richiesta = factory.Faker('name')

    class Meta:
        model = Prenotazione


class CalendarioPrenotazioneFactory(DjangoModelFactory):
    prenotazione = factory.SubFactory(PrenotazioneFactory)
    data_inizio = factory.fuzzy.FuzzyDate(date(2025, 1, 1), date(2025, 12, 31))
    data_fine = factory.fuzzy.FuzzyDate(date(2025, 1, 1), date(2025, 12, 31))

    class Meta:
        model = CalendarioPrenotazione

class FotoFactory(DjangoModelFactory):

    descrizione = factory.Faker('name')
    camera = factory.SubFactory(CameraFactory)
    proprieta = factory.SubFactory(ProprietaFactory)
    file = factory.django.ImageField(color='blue')

    class Meta:
        model = Foto
