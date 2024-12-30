from typing import Any
import datetime

from albdif.models import Visitatore
from django.contrib.auth.models import User


def registra_utente(user: User | None = None, **kwargs: Any) -> dict[str, Any]:
    if user:
        if not Visitatore.objects.filter(utente=user).exists():
            v = Visitatore.objects.create(utente=user, registrazione=datetime.datetime.now())
            v.save()
    return {}
