from django.urls import path
from . import views

app_name = "albdif"
urlpatterns = [
    path("", views.home, name="home"),
    # ex: /login/
    path("login/", views.login.as_view(), name="login"),
    # ex: /logout/
    path("logout/", views.logout.as_view(), name="logout"),
    # ex: /profilo/1/
    path("profilo/<int:pk>/", views.profilo.as_view(), name="profilo"),

    # ex: /partner/   -> le proprietà dei partener
    path("partner/", views.proprieta_partner.as_view(), name="proprieta_partner"),
    # ex: /proprieta/1/
    path("proprieta/<int:pk>/", views.proprieta_detail.as_view(), name="proprieta_detail"),

    # ex: /camere/     -> solo quelle dell'AD principale
    path("camere/", views.camere_list.as_view(), name="camere_list"),
    # ex: /camera/1/
    path("camera/<int:pk>/", views.camera_detail.as_view(), name="camera_detail"),
    # ex: /prenota_camera/1/2/
    path("prenota_camera/<int:id1>/<int:id2>/", views.prenota_camera.as_view(), name="prenota_camera"),
    # ex: /prenota_modifica/1/
    path("prenota_modifica/<int:id1>/", views.prenota_modifica.as_view(), name="prenota_modifica"),
    # ex: /prenotazione/1/
    #path("prenota_dettaglio/<int:pk>/", views.prenotazione_detail.as_view(), name="prenotazione_detail"),

    # ex: /prezzi_camera/
    path("prezzi_camera/", views.prezzi_camera_list.as_view(), name="prezzi_camera_list"),
    # ex: /prezzo_camera/1/
    path("prezzo_camera/<int:pk>/", views.prezzo_camera_detail.as_view(), name="prezzo_camera_detail"),

    # ex: /prenotazioni/
    path("prenotazioni/", views.prenotazioni_list.as_view(), name="prenotazioni_list"),
    # ex: /prenotazione_utente/1/
    path("prenotazioni_utente/<int:pk>/", views.prenotazioni_utente_list.as_view(), name="prenotazioni_utente_list"),

    # ex: /calendario_prenotazioni/
    path("calendario_prenotazioni/", views.calendario_prenotazioni_list.as_view(), name="calendario_prenotazioni_list"),
    # ex: /calendario_prenotazione/1/
    path("calendario_prenotazione/<int:pk>/", views.calendario_prenotazione_detail.as_view(), name="calendario_prenotazione_detail"),

    #    path('calendario_camera/', views.calendario_camera, name='calendario_camera'),
]
