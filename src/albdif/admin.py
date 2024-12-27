from django.contrib import admin

from .models import Visitatore, Host, Proprieta, Camera, Foto, Prenotazione, CalendarioPrenotazione, Stagione, \
    PrezzoCamera


class FotoAdmin(admin.ModelAdmin):
    search_fields = ['descrizione', ]
    list_filter = ['proprieta__descrizione', 'camera__descrizione']


class ProprietaAdmin(admin.ModelAdmin):
    list_display = ['host', 'descrizione', 'principale']
    search_fields = ['descrizione', ]
    list_filter = ['principale', ]


class CameraAdmin(admin.ModelAdmin):
    list_display = ['nome', 'proprieta']
    search_fields = ['descrizione', ]
    list_filter = ['proprieta', ]


class PrenotazioneAdmin(admin.ModelAdmin):
    list_display = ['id', 'visitatore', 'stato_prenotazione', 'data_prenotazione', 'camera']
    search_fields = ['richiesta', ]
    list_filter = ['visitatore', 'camera', 'camera__proprieta', 'stato_prenotazione', 'data_prenotazione']


class CalendarioPrenotazioneAdmin(admin.ModelAdmin):
    list_display = ['prenotazione', 'data_inizio', 'data_fine'] #, 'prenotazione__data_prenotazione', 'prenotazione__visitatore']
    search_fields = ['prenotazione__visitatore', ]
    list_filter = ['data_inizio'] #, 'prenotazione__visitatore', 'prenotazione__camera']


admin.site.register(Foto, FotoAdmin)
admin.site.register(Proprieta, ProprietaAdmin)
admin.site.register(Camera, CameraAdmin)
admin.site.register(Prenotazione, PrenotazioneAdmin)
admin.site.register(CalendarioPrenotazione, CalendarioPrenotazioneAdmin)

admin.site.register(Visitatore)
admin.site.register(Host)
admin.site.register(Stagione)
admin.site.register(PrezzoCamera)
