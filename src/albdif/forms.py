import datetime
from gc import disable

from django import forms
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.forms.widgets import DateInput, HiddenInput, Input

from .models import Prenotazione, CalendarioPrenotazione


class LoginForm(forms.Form):
    username = forms.CharField(max_length=254)
    password = forms.CharField(widget=forms.PasswordInput)


class PrenotazioneForm(forms.ModelForm):
    richiesta = forms.CharField(widget=forms.Textarea(attrs={"rows": 3, "cols": 80}))
    numero_persone = forms.IntegerField()
    costo_soggiorno = forms.DecimalField(max_digits=7, decimal_places=2, localize=True, widget=HiddenInput())

    class Meta:
        model = Prenotazione
        fields = ['richiesta', 'numero_persone', 'costo_soggiorno']
        # exclude = ['visitatore', 'camera', 'stato_prenotazione', 'data_prenotazione', 'data_pagamento']


class CalendarioPrenotazioneForm(forms.ModelForm):

    class Meta:
        model = CalendarioPrenotazione
        #fields = '__all__'
        exclude = ['prenotazione']
        widgets = {
            'data_inizio': Input(attrs={
                'class': 'data_calendario',
                'type': 'date'
            }),
            'data_fine': Input(attrs={
                'class': 'data_calendario',
                'type': 'date'
            }),
        }

    def clean(self):
        cleaned_data = super(CalendarioPrenotazioneForm, self).clean()
        di = cleaned_data.get("data_inizio")
        df = cleaned_data.get("data_fine")
        if not (df and di):
            raise ValidationError("Inserire le date per favore")
        if df < di:
            raise ValidationError("La data fine non può essere antecedente alla data inizio")
        if di <= datetime.datetime.now().date():
            raise ValidationError("La data inizio deve essere futura")
        gia_prenotata = CalendarioPrenotazione.objects.filter(
            Q(prenotazione__camera=self.instance.prenotazione.camera),
            Q(data_fine__gte=di), Q(data_inizio__lte=df),
            ~Q(prenotazione__visitatore=self.instance.prenotazione.visitatore)).count()
        if gia_prenotata > 0:
            raise ValidationError("Spiacenti: la camera è stata già prenotata")
        gia_prenotata = CalendarioPrenotazione.objects.filter(
            Q(prenotazione__camera=self.instance.prenotazione.camera),
            Q(data_fine__gte=di), Q(data_inizio__lte=df),
            ~Q(prenotazione__id=self.instance.prenotazione.id),
            ~Q(prenotazione__stato_prenotazione="CA"),
            Q(prenotazione__visitatore=self.instance.prenotazione.visitatore)).count()
        if gia_prenotata > 0:
            raise ValidationError("Spiacenti: le date si sovrappongono ad un'altra tua prenotazione")

        return cleaned_data


class PagamentoForm(forms.ModelForm):
    costo_soggiorno = forms.DecimalField(max_digits=7, decimal_places=2, disabled=True)

    class Meta:
        model = Prenotazione
        #fields = '__all__'
        exclude = ['visitatore', 'camera', 'stato_prenotazione', 'data_prenotazione',
                   'data_pagamento', 'richiesta', 'numero_persone']


