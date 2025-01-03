import pytest
from django.core.management import call_command
from albdif.models import Proprieta, Camera, Prenotazione, Stagione, CalendarioPrenotazione, Host, Visitatore


@pytest.mark.django_db
def test_crea_dati_test():
    import os
    os.chdir('src')
    call_command('crea_dati_test', )
    os.chdir('..')
    
    assert Host.objects.count() == 4
    assert Visitatore.objects.count() == 4
    assert Proprieta.objects.count() == 4
    assert Camera.objects.count() == 16
    assert Prenotazione.objects.count() == 51
    assert Stagione.objects.count() == 5
    assert CalendarioPrenotazione.objects.count() == 51
    assert Proprieta.objects.filter(principale=True).count() == 1
