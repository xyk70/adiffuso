import sys
from pathlib import Path
from typing import TYPE_CHECKING

import pytest
from _pytest.fixtures import SubRequest

if TYPE_CHECKING:
    from django_webtest import DjangoTestApp
    from django_webtest.pytest_plugin import MixinWithInstanceVariables

    from albdif.models import Camera, Prenotazione

here = Path(__file__).parent
sys.path.insert(0, str(here / "../src"))


@pytest.fixture
def user(db):
    from albdif.utils.fixtures import UserFactory

    return UserFactory()


@pytest.fixture
def visitatore(db):
    from albdif.utils.fixtures import VisitatoreFactory

    return VisitatoreFactory()


@pytest.fixture
def host(db):
    from albdif.utils.fixtures import HostFactory

    return HostFactory()


@pytest.fixture
def prenotazione(request: SubRequest, camera: "Camera"):
    from albdif.utils.fixtures import PrenotazioneFactory

    app: DjangoTestApp = request.getfixturevalue("app")

    return PrenotazioneFactory(camera=camera, visitatore=app._visitatore)


@pytest.fixture
def calendario_prenotazione(request: SubRequest, prenotazione: "Prenotazione"):
    from albdif.utils.fixtures import CalendarioPrenotazioneFactory

    app: DjangoTestApp = request.getfixturevalue("app")

    return CalendarioPrenotazioneFactory(prenotazione=prenotazione)


@pytest.fixture()
def app(django_app_factory: "MixinWithInstanceVariables", user: "User") -> "DjangoTestApp":
    django_app = django_app_factory(csrf_checks=False)
    django_app.set_user(user)
    django_app._user = user
    return django_app
