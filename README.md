# Albergo Diffuso Pegaso

Nome del progetto: **PW14A** 

---

## COMANDI DI UTILITA'

1. Dati di test
> python manage.py dumpdata > albdif\fixtures\albdif_new

---

## COME AVVIARE IL SERVER

1. avviare il virtualenv
> .venv\scripts\activate
2. Dalla directory: (pw14a-3.13) C:\prj\pw14a digitare il comando sotto
>python manage.py runserver

VARIABILI AMBIENTE DA IMPOSTARE:
- export PEGASO_MEDIA_URL='media/'
- export PEGASO_MEDIA_ROOT='c:/prj/pw14a/media/'
- export PEGASO_DATABASE_URL='sqlite:///C:/prj/pw14a/src/db.sqlite3'

## AVVIARE I TEST

1. avviare il virtualenv
> .venv\scripts\activate
2. Dalla directory: (pw14a-3.13) C:\prj\pw14a digitare il comando sotto
> pytest tests
3. test con il coverage
> pytest -vvv -s --disable-warnings --cov-report=html --cov=src/albdif tests

---

## DOCKER

Comandi di utilità

Prima di codificare lo yaml
> docker build -t pw14a .

> docker run -p 8000:8000 pw14a

> docker run --env-file .envdkc -p 8000:8000 pw14a

Dopo la codifica dello yaml
> docker-compose up --build -d

bash
docker stop <container_id>
docker run -d -p 8080:8080 hello-world-go
docker exec -it <container_id> bash
 