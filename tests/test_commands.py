import pytest
from django.core.management import call_command
from albdif.models import Proprieta, Camera, Prenotazione, Stagione, CalendarioPrenotazione, Host, Visitatore


@pytest.mark.django_db
def test_crea_dati_test():
    call_command('crea_dati_test')
    
    assert Host.objects.count() == 4
    assert Visitatore.objects.count() == 16
    assert Proprieta.objects.count() == 4
    assert Camera.objects.count() == 16
    assert Prenotazione.objects.count() == 16
    assert Stagione.objects.count() == 4
    assert CalendarioPrenotazione.objects.count() == 16
    assert Proprieta.objects.filter(principale=True).count() == 1
