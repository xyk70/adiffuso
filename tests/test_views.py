from datetime import date
from typing import TYPE_CHECKING

from django.urls import reverse

import pytest
from django_webtest import DjangoTestApp

from albdif.utils.fixtures import UserFactory, VisitatoreFactory, HostFactory, CalendarioPrenotazioneFactory, \
    PrenotazioneFactory, CameraFactory, ProprietaFactory

if TYPE_CHECKING:
    from albdif.models import Prenotazione, CalendarioPrenotazione

from albdif.models import Prenotazione, CalendarioPrenotazione

@pytest.fixture
def user(db):
    return UserFactory()

@pytest.fixture
def visitatore(db):
    return VisitatoreFactory()

@pytest.fixture
def host(db):
    return HostFactory()

def test_home(app: "DjangoTestApp"):
    url = reverse("albdif:home")
    response = app.get(url, user="")
    assert response.status_code == 200

    response = app.get(url)
    assert response.status_code == 200
    assert 'albdif/home.html' in [t.name for t in response.templates]
    assert 'Homepage AD Pegasus' in response.content.decode()


def test_login_ko(app: "DjangoTestApp"):
    url = reverse("albdif:login")
    app.set_user(None)
    response = app.get(url)
    response.form["username"] = "pippo"
    response.form["password"] = "pluto"
    response = response.form.submit()
    assert response.status_code == 200
    assert "Username o password errate!" in response.content.decode()


def test_login_ok(app: "DjangoTestApp", user):
    url = reverse("albdif:login")
    app.set_user(None)
    response = app.get(url)
    #u = User.objects.all().first()
    response.form["username"] = user.username
    response.form["password"] = "password"
    response = response.form.submit()
    assert response.status_code == 302
    assert response.url == reverse('albdif:home')
    assert "Username o password errate!" not in response.content.decode()


def test_profilo_ok(app: "DjangoTestApp", user):
    url = reverse("albdif:profilo", kwargs={'pk': user.pk})
    response = app.get(url)
    assert response.status_code == 200
    assert 'Le tue prenotazioni' in response.content.decode()


def test_logout(app: "DjangoTestApp"):
    url = reverse("albdif:logout")
    response = app.post(url)
    assert response.status_code == 302
    assert response.url == reverse('albdif:home')


def test_profilo_denied(app: "DjangoTestApp", user):
    s = UserFactory()
    url = reverse("albdif:profilo", kwargs={'pk': s.pk})
    response = app.get(url)
    assert response.status_code == 302
    assert 'Le tue prenotazioni' not in response.content.decode()


def test_proprieta_partner_view(app: "DjangoTestApp"):
    url = reverse('albdif:proprieta_partner')
    response = app.get(url)
    assert response.status_code == 200
    assert 'albdif/proprieta_list.html' in [t.name for t in response.templates]
    assert 'Lista dei Partner' in response.content.decode()


def test_calendario_passato(app: "DjangoTestApp", user):
    pr1 = ProprietaFactory()
    v1 = VisitatoreFactory(utente=user)
    c1 = CameraFactory(proprieta=pr1)
    p1 = PrenotazioneFactory(
        visitatore=v1,
        camera=c1,
        data_prenotazione=date(2023, 12, 1),
        stato_prenotazione="PG"
    )
    CalendarioPrenotazioneFactory(
        prenotazione=p1,
        data_inizio=date(2024, 1, 1),
        data_fine=date(2024, 1, 2))

    url = reverse("albdif:profilo", kwargs={'pk': user.pk})
    response = app.get(url)
    assert response.status_code == 200
    assert 'Storico' in response.content.decode()


def test_prenotazione_passata(app: "DjangoTestApp", user):
    pr1 = ProprietaFactory()
    v1 = VisitatoreFactory(utente=user)
    c1 = CameraFactory(proprieta=pr1)

    url = reverse("albdif:prenota_camera", kwargs={'id1': v1.pk, 'id2': c1.pk})
    response = app.get(url)
    assert response.status_code == 200
    assert 'Stai prenotando la camera' in response.content.decode()

    response.form["richiesta"] = "bla bla"
    response.form["data_inizio"] = date(2024,1,1)
    response.form["data_fine"] = date(2026,1,2)
    response = response.form.submit()
    assert 'La data inizio deve essere futura' in response.content.decode()

    response.form["richiesta"] = "bla bla"
    response.form["data_inizio"] = date(2026,1,1)
    response.form["data_fine"] = date(2024,1,2)
    response = response.form.submit()
    assert 'La data fine non può essere antecedente alla data inizio' in response.content.decode()

def test_prenotazione_negata(app: "DjangoTestApp", user):
    u1 = UserFactory()
    pr1 = ProprietaFactory()
    v1 = VisitatoreFactory(utente=u1)
    c1 = CameraFactory(proprieta=pr1)
    p1 = PrenotazioneFactory(
        visitatore=v1,
        camera=c1,
        data_prenotazione=date(2024, 12, 25),
        stato_prenotazione="PR"
    )
    CalendarioPrenotazioneFactory(
        prenotazione=p1,
        data_inizio=date(2025, 2, 1),
        data_fine=date(2025, 2, 2))

    v = VisitatoreFactory(utente=user)
    url = reverse("albdif:prenota_camera", kwargs={'id1': v.pk, 'id2': c1.pk})
    response = app.get(url)
    assert response.status_code == 200
    assert 'Stai prenotando la camera' in response.content.decode()

    response.form["richiesta"] = "bla bla"
    response.form["data_inizio"] = date(2025,2,1)
    response.form["data_fine"] = date(2025,2,1)
    response = response.form.submit()
    assert "Spiacenti: la camera è stata già prenotata" in response.content.decode()

def test_prenotazione_sovrapposta(app: "DjangoTestApp", user):
    pr1 = ProprietaFactory()
    v1 = VisitatoreFactory(utente=user)
    c1 = CameraFactory(proprieta=pr1)
    p1 = PrenotazioneFactory(
        visitatore=v1,
        camera=c1,
        data_prenotazione=date(2024, 12, 25),
        stato_prenotazione="PR"
    )
    CalendarioPrenotazioneFactory(
        prenotazione=p1,
        data_inizio=date(2025, 2, 1),
        data_fine=date(2025, 2, 2))

    url = reverse("albdif:prenota_camera", kwargs={'id1': v1.pk, 'id2': c1.pk})
    response = app.get(url)
    assert response.status_code == 200
    assert 'Stai prenotando la camera' in response.content.decode()

    response.form["richiesta"] = "bla bla"
    response.form["data_inizio"] = date(2025,2,1)
    response.form["data_fine"] = date(2025,2,1)
    response = response.form.submit()
    assert "Spiacenti: le date si sovrappongono ad un" in response.content.decode()


def test_prenotazione_avvenuta(app: "DjangoTestApp", user):
    pr1 = ProprietaFactory()
    v1 = VisitatoreFactory(utente=user)
    c1 = CameraFactory(proprieta=pr1)

    url = reverse("albdif:prenota_camera", kwargs={'id1': v1.pk, 'id2': c1.pk})
    response = app.get(url)
    assert response.status_code == 200
    assert 'Stai prenotando la camera' in response.content.decode()

    response.form["richiesta"] = "bla bla"
    response.form["numero_persone"] = 3
    response.form["data_inizio"] = date(2025,2,1)
    response.form["data_fine"] = date(2025,2,1)
    response.form["costo_soggiorno"] = 100
    response = response.form.submit()
    assert response.status_code == 302
    p = Prenotazione.objects.get(visitatore__utente=user)
    assert "bla bla" == p.richiesta
    assert CalendarioPrenotazione.objects.filter(prenotazione=p).exists()
    #assert "Profilo dell'utente" in response.content.decode()


def test_prenotazione_modifica(app: "DjangoTestApp", user):
    pr1 = ProprietaFactory()
    v1 = VisitatoreFactory(utente=user)
    c1 = CameraFactory(proprieta=pr1)
    p1 = PrenotazioneFactory(
        visitatore=v1,
        camera=c1,
        data_prenotazione=date(2024, 12, 25),
        stato_prenotazione="PR",
        costo_soggiorno=100,
    )
    CalendarioPrenotazioneFactory(
        prenotazione=p1,
        data_inizio=date(2025, 2, 1),
        data_fine=date(2025, 2, 2))

    url = reverse("albdif:prenota_modifica", kwargs={'id1': p1.pk})
    response = app.get(url)
    assert response.status_code == 200
    assert 'Stai modificando la prenotazione della camera' in response.content.decode()

    response.form["richiesta"] = "avevo dimenticato di chiedere ..."
    response.form["data_inizio"] = date(2025,2,1)
    response.form["data_fine"] = date(2025,2,1)
    response = response.form.submit()
    assert response.status_code == 302
    p = Prenotazione.objects.get(visitatore__utente=user)
    assert "avevo dimenticato di chiedere ..." == p.richiesta


def test_prenotazione_modifica_denied(app: "DjangoTestApp", user):
    s = UserFactory()
    pr1 = ProprietaFactory()
    v1 = VisitatoreFactory(utente=s)
    c1 = CameraFactory(proprieta=pr1)
    p1 = PrenotazioneFactory(
        visitatore=v1,
        camera=c1,
        data_prenotazione=date(2024, 12, 25),
        stato_prenotazione="PR"
    )
    CalendarioPrenotazioneFactory(
        prenotazione=p1,
        data_inizio=date(2025, 2, 1),
        data_fine=date(2025, 2, 2))

    url = reverse("albdif:prenota_modifica", kwargs={'id1': p1.pk})
    response = app.get(url)
    assert response.status_code == 302
    assert 'Stai modificando la prenotazione della camera' not in response.content.decode()
    #TODO aggiungere test sul messaggio


def test_prenotazione_modifica_denied_2(app: "DjangoTestApp", user):
    s = UserFactory()
    pr1 = ProprietaFactory()
    v1 = VisitatoreFactory(utente=s)
    c1 = CameraFactory(proprieta=pr1)
    p1 = PrenotazioneFactory(
        visitatore=v1,
        camera=c1,
        data_prenotazione=date(2023, 1, 1),
        stato_prenotazione="PR"
    )
    cp = CalendarioPrenotazioneFactory(
        prenotazione=p1,
        data_inizio=date(2023, 2, 1),
        data_fine=date(2023, 2, 2))

    url = reverse("albdif:prenota_modifica", kwargs={'id1': p1.pk})
    response = app.get(url)
    assert response.status_code == 302
    #assert 'Non è possibile modificare una prenotazione passata!' in response.content.decode()

    p1.stato_prenotazione = "PG"
    cp.data_inizio = date(2025, 2, 2)
    cp.data_inizio = date(2025, 2, 3)
    url = reverse("albdif:prenota_modifica", kwargs={'id1': p1.pk})
    response = app.get(url)
    assert response.status_code == 302
    #assert 'Non è possibile modificare una prenotazione già pagata!' in response.content.decode()
    #TODO aggiungere test sul messaggio


def test_prenotazione_cancellata(app: "DjangoTestApp", user):
    s = UserFactory()
    pr1 = ProprietaFactory()
    v1 = VisitatoreFactory(utente=s)
    c1 = CameraFactory(proprieta=pr1)
    p1 = PrenotazioneFactory(
        visitatore=v1,
        camera=c1,
        data_prenotazione=date(2023, 1, 1),
        stato_prenotazione="PG"
    )
    cp = CalendarioPrenotazioneFactory(
        prenotazione=p1,
        data_inizio=date(2025, 2, 1),
        data_fine=date(2025, 2, 2))

    url = reverse("albdif:prenota_cancella", kwargs={'id1': p1.pk})
    response = app.get(url)
    assert response.status_code == 302
    #TODO gli assert che seguono lo status code 302 non funzionano: approfondire
    #assert 'Non è possibile cancellare una prenotazione già pagata' in response.content.decode()

    p1.stato_prenotazione = "PR"
    cp.data_inizio = date(2023, 2, 2)
    cp.data_inizio = date(2023, 2, 3)
    url = reverse("albdif:prenota_cancella", kwargs={'id1': p1.pk})
    response = app.get(url)
    assert response.status_code == 302
    #assert 'Non è possibile cancellare una prenotazione passata' in response.content.decode()

    p1.stato_prenotazione = "PR"
    cp.data_inizio = date(2025, 2, 2)
    cp.data_inizio = date(2025, 2, 3)
    url = reverse("albdif:prenota_cancella", kwargs={'id1': p1.pk})
    response = app.get(url)
    assert response.status_code == 302
    #assert 'Prenotazione cancellata con successo' in response.content.decode()


def test_proprieta(app: "DjangoTestApp"):
    url = reverse("albdif:proprieta_partner")
    response = app.get(url)
    assert response.status_code == 200
    assert 'I nostri partner' in response.content.decode()
    assert 'Nessuna proprietà disponibile' in response.content.decode()

    p1 = ProprietaFactory()
    CameraFactory(proprieta=p1)
    CameraFactory(proprieta=p1)
    p2 = ProprietaFactory()
    CameraFactory(proprieta=p2)
    response = app.get(url)
    assert response.status_code == 200
    assert 'I nostri partner' in response.content.decode()
    assert 'Nessuna proprieta disponibile' not in response.content.decode()

    url = reverse("albdif:proprieta_detail", kwargs={'pk': p1.pk})
    response = app.get(url)
    assert response.status_code == 200
    assert 'Le camere del nostro partner' in response.content.decode()


def test_camera(app: "DjangoTestApp", user):
    pr1 = ProprietaFactory()
    v1 = VisitatoreFactory(utente=user)
    c1 = CameraFactory(proprieta=pr1)
    c2 = CameraFactory(proprieta=pr1)
    p1 = PrenotazioneFactory(
        visitatore=v1,
        camera=c1,
        numero_persone=2,
        data_prenotazione=date(2023, 12, 25),
        stato_prenotazione="PG"
    )
    CalendarioPrenotazioneFactory(
        prenotazione=p1,
        data_inizio=date(2024, 2, 1),
        data_fine=date(2024, 2, 2))

    p2 = PrenotazioneFactory(
        visitatore=v1,
        camera=c1,
        numero_persone=3,
        data_prenotazione=date(2024, 11, 25),
        stato_prenotazione="PR"
    )
    CalendarioPrenotazioneFactory(
        prenotazione=p2,
        data_inizio=date(2025, 1, 6),
        data_fine=date(2025, 1, 10))

    url = reverse("albdif:camera_detail", kwargs={'pk': c1.pk})
    response = app.get(url)
    assert response.status_code == 200
    assert 'Le tue prenotazioni' in response.content.decode()
    assert 'Modifica' in response.content.decode()
    assert 'Nessuna prenotazione trovata' not in response.content.decode()

    url = reverse("albdif:camera_detail", kwargs={'pk': c2.pk})
    response = app.get(url)
    assert response.status_code == 200
    assert 'Le tue prenotazioni' in response.content.decode()
    assert 'Nessuna prenotazione trovata' in response.content.decode()


#TODO test da rivedere: non funziona il logout e non riesco a testare in modalità anonima
def test_camera_anonymous(app: "DjangoTestApp"):
    pr1 = ProprietaFactory()
    c2 = CameraFactory(proprieta=pr1)

    url = reverse("albdif:logout")
    response = app.post(url)
    assert response.status_code == 302
    assert response.url == reverse('albdif:home')
    url = reverse("albdif:camera_detail", kwargs={'pk': c2.pk})
    response = app.get(url)
    assert response.status_code == 200
    #assert not 'Le tue prenotazioni' in response.content.decode()
    #assert not 'Nessuna prenotazione trovata' in response.content.decode()


def test_cancellazione_prenotazione(app: "DjangoTestApp", user):
    pr1 = ProprietaFactory()
    v1 = VisitatoreFactory(utente=user)
    c1 = CameraFactory(proprieta=pr1)
    p1 = PrenotazioneFactory(
        visitatore=v1,
        camera=c1,
        numero_persone=2,
        data_prenotazione=date(2023, 12, 25),
        stato_prenotazione="PG"
    )
    CalendarioPrenotazioneFactory(
        prenotazione=p1,
        data_inizio=date(2025, 2, 1),
        data_fine=date(2025, 2, 2))

    p2 = PrenotazioneFactory(
        visitatore=v1,
        camera=c1,
        numero_persone=3,
        data_prenotazione=date(2024, 11, 25),
        stato_prenotazione="PR"
    )
    CalendarioPrenotazioneFactory(
        prenotazione=p2,
        data_inizio=date(2025, 1, 6),
        data_fine=date(2025, 1, 10))

    url = reverse("albdif:prenota_cancella", kwargs={'id1': p2.pk})
    response = app.get(url)
    assert response.status_code == 302
    assert Prenotazione.objects.get(pk=p2.pk).stato_prenotazione == 'CA'


def test_pagamento_prenotazione(app: "DjangoTestApp", user):
    pr1 = ProprietaFactory()
    v1 = VisitatoreFactory(utente=user)
    c1 = CameraFactory(proprieta=pr1)
    p1 = PrenotazioneFactory(
        visitatore=v1,
        camera=c1,
        numero_persone=2,
        costo_soggiorno=40,
        data_prenotazione=date(2023, 12, 25),
        stato_prenotazione="PR"
    )
    CalendarioPrenotazioneFactory(
        prenotazione=p1,
        data_inizio=date(2025, 2, 1),
        data_fine=date(2025, 2, 2))

    url = reverse("albdif:prenota_paga", kwargs={'id1': p1.pk})
    response = app.get(url)
    assert response.status_code == 200
    response = response.form.submit()
    assert response.status_code == 302
    assert Prenotazione.objects.get(pk=p1.pk).stato_prenotazione == 'PG'

    url = reverse("albdif:prenota_cancella", kwargs={'id1': p1.pk})
    response = app.get(url)
    assert response.status_code == 302
    assert Prenotazione.objects.get(pk=p1.pk).stato_prenotazione == 'PG'
