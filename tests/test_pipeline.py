import pytest
from django.contrib.auth.models import User
from albdif.models import Visitatore
from albdif.utils.pipeline import registra_utente

@pytest.mark.django_db
def test_registra_utente_crea_visitatore():
    user = User.objects.create_user(username='fabio', password='12345678')
    result = registra_utente(user=user)
    
    assert Visitatore.objects.filter(utente=user).exists()
    assert result == {}

@pytest.mark.django_db
def test_registra_utente_senza_user():
    result = registra_utente()
    
    assert result == {}
