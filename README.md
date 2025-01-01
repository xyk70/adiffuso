# Benvenuti nel progetto PW14A

Titolo: **Albergo Diffuso Pegasus**

---
### Prerequisiti per l'avvio del progetto in locale (SO Windows)
1. installazione di python versione 3.12 (https://www.python.org/downloads/windows/)  
2. installazione di uv (https://docs.astral.sh/uv/getting-started/installation/)
> pip install uv

### Installazione del progetto
1. copia del codice dal repository Github 
> posizionarsi su una directory: es c:\prj ed eseguire il comando seguente
> git clone https://github.com/fabmeo/prj14a.git
2. accedere alla directory pw14a
> cd pw14a
3. installazione del virtualenv
> uv sync
> - alla fine dell'installazione il virtualenv si attiva automaticamente e il prompt è come segue:
> - (pw14a) C:\prj\pw14a>
3. verifica del progetto con l'esecuzione dei test
> pytest tests

4. impostazione delle variabili d'ambiente
> **NECESSARIE**
> ```
> set PEGASUS_MEDIA_URL=media/
> set PEGASUS_MEDIA_ROOT=c:/prj/pw14a/media/
> set PEGASUS_DATABASE_URL=sqlite:///C:/prj/pw14a/database/db.sqlite3
> set PEGASUS_SOCIAL_AUTH_REDIRECT_IS_HTTPS=0
> ```
> **OPZIONALI**
> ```
> a) Se si vuole attivare il SSO Github seguire la guida a questo link: https://python-social-auth.readthedocs.io/en/latest/backends/github.html
> b) e registrare una nuova app dalle impostazioni dello sviluppatore del proprio account Github: https://github.com/settings/applications/new 
> c) Questo permetterà di ottenere la coppia key/secret da imposare di seguito e consentire la registrazione immediata dell'account sull'applicazione AD Pegasus 
> set PEGASUS_SOCIAL_AUTH_GITHUB_KEY=<inserire la api key github>
> set PEGASUS_SOCIAL_AUTH_GITHUB_SECRET=<inserire la secret key github>
> set PEGASUS_SOCIAL_AUTH_GITHUB_REDIRECT_URI=http://localhost:8000/social/complete/github/
> ```
5. creazione del database (accesso alla sotto-directory src)
> ```
> cd src
> python manage.py migrate
> ```
6. creazione dei dati di test (include utente "guest")
> python manage.py crea_dati_test
7. avvio del server
> python manage.py runserver localhost:8000
8. Click sulla url del sito in esecuzione (vedi sotto)
> ```
> ...
> System check identified 3 issues (0 silenced).
> January 01, 2025 - 21:04:58
> Django version 4.2.17, using settings 'albdif.config.settings'
> Starting development server at http://localhost:8000/
> Quit the server with CTRL-BREAK.
> ```
9. Il sito è navigabile in modalità anonima ma può essere acceduto anche con le seguenti credenziali:
> utente: **guest**
> password: **password**

---

