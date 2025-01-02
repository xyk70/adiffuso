## COMANDI DI UTILITA'

1. Dump dei dati sul database
> python manage.py dumpdata > albdif\fixtures\albdif_new

---

## AVVIARE IL SERVER

1. avviare il virtualenv
> .venv\scripts\activate
2. Dalla directory: (pw14a-3.12) C:\prj\pw14a digitare il comando sotto
> python manage.py runserver

VARIABILI AMBIENTE DA IMPOSTARE:
- export PEGASUS_MEDIA_URL='media/'
- export PEGASUS_MEDIA_ROOT='c:/prj/pw14a/media/'
- export PEGASUS_DATABASE_URL='sqlite:///C:/prj/pw14a/src/db.sqlite3'

---

## AVVIARE I TEST

1. avviare il virtualenv
> .venv\scripts\activate
2. Dalla directory: (pw14a-3.13) C:\prj\pw14a digitare il comando sotto
> pytest tests
3. test con il coverage
> pytest tests

---

