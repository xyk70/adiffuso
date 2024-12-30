from datetime import datetime
import json

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.urls import reverse_lazy, reverse
from django.views.generic import FormView
from django.contrib.auth import authenticate, login as auth_login
from django.views import View
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpRequest, HttpResponseRedirect
from django.views import generic
from django.contrib.auth import logout as auth_logout

from .forms import LoginForm, PrenotazioneForm, CalendarioPrenotazioneForm, PagamentoForm
from .utils.utility import date_range, calcola_prezzo_totale
from .models import Camera, Proprieta, Prenotazione, PrezzoCamera, CalendarioPrenotazione, Foto, Visitatore, Stagione


def home(request: HttpRequest) -> HttpResponse:
    template_name = "albdif/home.html"
    return render(request, template_name)


class login(FormView):
    template_name = "albdif/login.html"
    form_class = LoginForm
    success_url = reverse_lazy('albdif:home')

    def form_valid(self, form):
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        user = authenticate(username=username, password=password)

        if user is not None:
            if user.is_active:
                auth_login(self.request, user)
                return HttpResponseRedirect(self.get_success_url())

        form.add_error(None, "Username o password errate!")
        return self.form_invalid(form)


class logout(View):
    """
    Esegue il logout dell'utente e ritorna ad home
    """
    def post(self, request, *args, **kwargs):
        auth_logout(request)
        return redirect('albdif:home')


# PROFILO UTENTE VISITATORE
class profilo(LoginRequiredMixin, generic.DetailView):
    """
    # pagina dell'utente visitatore
    """
    model = User
    template_name = "albdif/profilo.html"
    login_url = "/login/"

    def dispatch(self, request, *args, **kwargs):
        """ La pagina del profilo può essere acceduta solo dal suo utente """
        if self.get_object() != request.user:
            messages.warning(request, 'Accesso ad altre pagine profilo non consentito!')
            return redirect('albdif:home')
            #raise PermissionDenied("Accesso ad altre pagine profilo non consentito")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """Ritorna la lista delle prenotazioni di un utente"""
        context = super(profilo, self).get_context_data(**kwargs)
        utente_id = self.kwargs.get('pk')
        prenotazioni = CalendarioPrenotazione.objects.filter(prenotazione__visitatore__utente__id=utente_id,
                                                             data_inizio__gte=datetime.now())
        storico = CalendarioPrenotazione.objects.filter(prenotazione__visitatore__utente__id=utente_id,
                                                        data_inizio__lt=datetime.now())
        context['prenotazioni_list'] = prenotazioni
        context['storico_list'] = storico
        return context


# REGISTRAZIONE
class registrazione(generic.DetailView):
    """
    # pagina di registrazione
    """
    template_name = "albdif/registrazione.html"
    login_url = "/registrazione/"


# PROPRIETA'
class proprieta_detail(generic.ListView):
    """
    Ritorna la lista delle camere dell'AD selezionato ordinata per descrizione
    """
    template_name = "albdif/proprieta_detail.html"
    context_object_name = "camere_list"

    def get_queryset(self):
        prop = self.kwargs.get('pk')
        return Camera.objects.filter(proprieta__id=prop).order_by("descrizione")

    def get_context_data(self, **kwargs):
        context = super(proprieta_detail, self).get_context_data(**kwargs)
        prop = get_object_or_404(Proprieta, pk=self.kwargs.get('pk'))
        context['proprieta'] = prop                  # la proprietà (Albergo Diffuso X)
        context['camere_list'] = self.get_queryset() # le sue camere
        return context


class proprieta_partner(generic.ListView):
    """
    Ritorna la lista dei partner con le foto della proprietà
    """
    template_name = "albdif/proprieta_list.html"
    context_object_name = "proprieta_list"

    def get_queryset(self):
        return Proprieta.objects.filter(principale=False)

    def get_context_data(self, **kwargs):
        context = super(proprieta_partner, self).get_context_data(**kwargs)
        prop_e_foto = []
        for p in self.get_queryset():
            prop = {'prop': p, 'foto': Foto.objects.filter(proprieta__id=p.id)}
            prop_e_foto.append(prop)
        context['prop_e_foto'] = prop_e_foto      # ogni proprietà con le sue foto
        return context


# CAMERE
class camera_detail(generic.DetailView):
    """
    # estraggo solo i periodi di prenotazione che comprendono la data corrente e i futuri
    """
    model = Camera
    template_name = "albdif/camera_detail.html"

    def get_context_data(self, **kwargs):
        context = super(camera_detail, self).get_context_data(**kwargs)
        gia_prenotate = []
        prenotazioni = Prenotazione.objects.filter(camera=self.object.pk)
        for p in prenotazioni:
            periodi = CalendarioPrenotazione.objects.filter(prenotazione=p.id, data_fine__gte=datetime.today())
            for periodo in periodi:
                for d in date_range(str(periodo.data_inizio), str(periodo.data_fine)):
                    gia_prenotate.append(d)

        foto = Foto.objects.filter(camera=self.object.pk)
        prenotazioni = []
        if self.request.user.is_authenticated:
            prenotazioni = CalendarioPrenotazione.objects.filter(prenotazione__visitatore__utente=self.request.user,
                                                                 prenotazione__camera=self.object,
                                                                 data_inizio__gte=datetime.now())
        context['disabled_dates'] = json.dumps(gia_prenotate)
        context['foto'] = foto
        context['prenotazioni_list'] = prenotazioni
        return context


class prenota_camera(generic.DetailView):
    """
    Gestisce la pagina del form di prenotazione con i form Prenotazione e CalendarioPrenotazione
    """
    template_name = "albdif/form_prenotazione.html"

    def get(self, request, *args, **kwargs):
        visitatore = Visitatore.objects.get(utente__id=self.kwargs["id1"])
        camera = get_object_or_404(Camera, id=self.kwargs["id2"])
        prenotazione_form = PrenotazioneForm(initial={'visitatore': visitatore.id, 'camera': camera.id})
        calendario_form = CalendarioPrenotazioneForm()
        stagioni = Stagione.objects.filter(data_fine__gt=datetime.now()).order_by("data_inizio")
        return render(request, self.template_name, {
            'visitatore': visitatore,
            'camera': camera,
            'prenotazione_form': prenotazione_form,
            'calendario_form': calendario_form,
            'stagioni': stagioni
        })

    def post(self, request, *args, **kwargs):
        visitatore = Visitatore.objects.get(utente__id=self.kwargs["id1"])
        camera = get_object_or_404(Camera, id=self.kwargs["id2"])
        prenotazione_form = PrenotazioneForm(request.POST)
        prenotazione_form.instance.visitatore = visitatore
        prenotazione_form.instance.camera = camera
        prenotazione_form.instance.stato_prenotazione = Prenotazione.PRENOTATA
        prenotazione_form.instance.data_prenotazione = datetime.now()

        calendario_form = CalendarioPrenotazioneForm(request.POST)
        calendario_form.instance.prenotazione = prenotazione_form.instance
        stagioni = Stagione.objects.filter(data_fine__gt=datetime.now()).order_by("data_inizio")

        if prenotazione_form.is_valid() and calendario_form.is_valid():
            prenotazione = prenotazione_form.save()
            calendario = calendario_form.save(commit=False)
            calendario.prenotazione = prenotazione
            calendario.save()
            messages.success(request, 'Prenotazione avvenuta con successo')
            #@TODO invio email all'utente
            return HttpResponseRedirect(reverse('albdif:profilo', kwargs={'pk': visitatore.utente.id}))
        else:
            messages.error(request, 'Sono presenti degli errori: ricontrollare i dati inseriti')

        return render(request, self.template_name, {
            'visitatore': visitatore,
            'camera': camera,
            'prenotazione_form': prenotazione_form,
            'calendario_form': calendario_form,
            'stagioni': stagioni
        })


class prenota_modifica(generic.DetailView):
    """
    Gestisce la modifica di una prenotazione
    """
    template_name = "albdif/form_prenotazione_modifica.html"

    def dispatch(self, request, *args, **kwargs):
        """ La pagina della prenotazione può essere acceduta solo dal suo utente """
        prenotazione = get_object_or_404(Prenotazione, id=self.kwargs["id1"])
        if prenotazione.visitatore.utente.id != request.user.id:
            messages.warning(request, 'Accesso ad altre pagine prenotazione non consentito!')
            return HttpResponseRedirect(reverse('albdif:camera_detail', kwargs={'pk': prenotazione.camera.id}))

        """ Non è possibile modificare una prenotazione già pagata"""
        p = get_object_or_404(Prenotazione, id=self.kwargs["id1"])
        if p.stato_prenotazione == "PG":
            messages.warning(request, 'Non è possibile modificare una prenotazione già pagata!')
            return HttpResponseRedirect(reverse('albdif:camera_detail', kwargs={'pk': prenotazione.camera.id}))

        """ Non è possibile modificare una prenotazione passata"""
        cp = CalendarioPrenotazione.objects.filter(prenotazione__id=self.kwargs["id1"]).order_by("data_inizio").first()
        if cp.data_inizio < datetime.today().date():
            messages.warning(request, 'Non è possibile modificare una prenotazione passata!')
            return HttpResponseRedirect(reverse('albdif:camera_detail', kwargs={'pk': prenotazione.camera.id}))

        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        prenotazione = get_object_or_404(Prenotazione, id=self.kwargs["id1"])
        calendario = get_object_or_404(CalendarioPrenotazione, prenotazione__id=prenotazione.id)
        visitatore = get_object_or_404(Visitatore, id=prenotazione.visitatore.id)
        camera = get_object_or_404(Camera, id=prenotazione.camera.id)
        prenotazione_form = PrenotazioneForm(instance=prenotazione)
        calendario_form = CalendarioPrenotazioneForm(instance=calendario)
        stagioni = Stagione.objects.filter(data_fine__gt=datetime.now()).order_by("data_inizio")

        return render(request, self.template_name, {
            'visitatore': visitatore,
            'camera': camera,
            'prenotazione_form': prenotazione_form,
            'calendario_form': calendario_form,
            'stagioni': stagioni
        })

    def post(self, request, *args, **kwargs):
        prenotazione = get_object_or_404(Prenotazione, id=self.kwargs["id1"])
        calendario = get_object_or_404(CalendarioPrenotazione, prenotazione__id=prenotazione.id)
        visitatore = get_object_or_404(Visitatore, id=prenotazione.visitatore.id)
        camera = get_object_or_404(Camera, id=prenotazione.camera.id)
        stagioni = Stagione.objects.filter(data_fine__gt=datetime.now()).order_by("data_inizio")
        tot = calcola_prezzo_totale(calendario.data_inizio, calendario.data_fine, stagioni)
        if prenotazione.costo_soggiorno and prenotazione.costo_soggiorno != tot:
            messages.info(request, 'Il prezzo è stato aggiornato')
            prenotazione.costo_soggiorno = tot
        prenotazione_form = PrenotazioneForm(request.POST, instance=prenotazione)
        calendario_form = CalendarioPrenotazioneForm(request.POST, instance=calendario)

        if prenotazione_form.is_valid() and calendario_form.is_valid():
            prenotazione_form.save()
            calendario_form.save()
            messages.success(request, 'Prenotazione modificata con successo')
            #@TODO invio email all'utente
            return HttpResponseRedirect(reverse('albdif:profilo', kwargs={'pk': visitatore.utente.id}))

        return render(request, self.template_name, {
            'visitatore': visitatore,
            'camera': camera,
            'prenotazione_form': prenotazione_form,
            'calendario_form': calendario_form,
            'stagioni': stagioni
        })


class prenota_cancella(generic.DetailView):
    """
    Gestisce la cancellazione di una prenotazione
    """
    template_name = "albdif/camera_detail.html"

    def dispatch(self, request, *args, **kwargs):
        """ La pagina della prenotazione può essere acceduta solo dal suo utente """
        prenotazione = get_object_or_404(Prenotazione, id=self.kwargs["id1"])
        if prenotazione.visitatore.utente.id != request.user.id:
            messages.error(request, 'Accesso ad altre pagine prenotazione non consentito!')
            return HttpResponseRedirect(reverse('albdif:camera_detail', kwargs={'pk': prenotazione.camera.id}))

        """ Non è possibile cancellare una prenotazione già pagata"""
        p = get_object_or_404(Prenotazione, id=self.kwargs["id1"])
        if p.stato_prenotazione == "PG":
            messages.warning(request, 'Non è possibile cancellare una prenotazione già pagata!')
            return HttpResponseRedirect(reverse('albdif:camera_detail', kwargs={'pk': prenotazione.camera.id}))

        """ Non è possibile cancellare una prenotazione passata"""
        cp = CalendarioPrenotazione.objects.filter(prenotazione__id=self.kwargs["id1"]).order_by("data_inizio").first()
        if cp.data_inizio < datetime.today().date():
            messages.warning(request, 'Non è possibile cancellare una prenotazione passata!')
            return HttpResponseRedirect(reverse('albdif:camera_detail', kwargs={'pk': prenotazione.camera.id}))

        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self, *args, **kwargs):
        p = get_object_or_404(Prenotazione, id=self.kwargs["id1"])
        return p

    def get(self, request, *args, **kwargs):
        prenotazione = self.get_queryset()
        prenotazione.stato_prenotazione = prenotazione.CANCELLATA
        prenotazione.save()
        messages.success(request, 'Prenotazione cancellata con successo')

        return HttpResponseRedirect(reverse('albdif:camera_detail', kwargs={'pk': prenotazione.camera.id}))


class prenota_paga(generic.DetailView):
    """
    Gestisce il pagamento di una prenotazione
    """
    template_name = "albdif/form_pagamento.html"

    def dispatch(self, request, *args, **kwargs):
        """ La pagina del pagamento della prenotazione può essere acceduta solo dal suo utente """
        prenotazione = get_object_or_404(Prenotazione, id=self.kwargs["id1"])
        if prenotazione.visitatore.utente.id != request.user.id:
            messages.warning(request, 'Accesso ad altre pagine prenotazione non consentito!')
            return HttpResponseRedirect(reverse('albdif:camera_detail', kwargs={'pk': prenotazione.camera.id}))

        """ Il pagamento è stato già effettuato"""
        p = get_object_or_404(Prenotazione, id=self.kwargs["id1"])
        if p.stato_prenotazione == "PG":
            messages.warning(request, 'Il pagamento risulta già effettuato!')
            return HttpResponseRedirect(reverse('albdif:camera_detail', kwargs={'pk': prenotazione.camera.id}))

        """ Non è possibile modificare una prenotazione passata"""
        cp = CalendarioPrenotazione.objects.filter(prenotazione__id=self.kwargs["id1"]).order_by("data_inizio").first()
        if cp.data_inizio < datetime.today().date():
            messages.warning(request, 'Non è possibile modificare una prenotazione passata!')
            return HttpResponseRedirect(reverse('albdif:camera_detail', kwargs={'pk': prenotazione.camera.id}))

        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        prenotazione = get_object_or_404(Prenotazione, id=self.kwargs["id1"])
        calendario = get_object_or_404(CalendarioPrenotazione, prenotazione__id=prenotazione.id)
        visitatore = get_object_or_404(Visitatore, id=prenotazione.visitatore.id)
        camera = get_object_or_404(Camera, id=prenotazione.camera.id)
        stagioni = Stagione.objects.filter(data_fine__gt=datetime.now()).order_by("data_inizio")
        if prenotazione.costo_soggiorno is None:
            prenotazione.costo_soggiorno = calcola_prezzo_totale(calendario.data_inizio, calendario.data_fine, stagioni)
        pagamento_form = PagamentoForm(instance=prenotazione)

        return render(request, self.template_name, {
            'visitatore': visitatore,
            'camera': camera,
            'pagamento_form': pagamento_form,
        })

    def post(self, request, *args, **kwargs):
        prenotazione = get_object_or_404(Prenotazione, id=self.kwargs["id1"])
        visitatore = get_object_or_404(Visitatore, id=prenotazione.visitatore.id)
        camera = get_object_or_404(Camera, id=prenotazione.camera.id)
        pagamento_form = PagamentoForm(request.POST, instance=prenotazione)

        if pagamento_form.is_valid():
            prenotazione.data_pagamento = datetime.now()
            prenotazione.stato_prenotazione = prenotazione.PAGATA
            pagamento = pagamento_form.save()
            messages.success(request, 'Pagamento effettuto con successo')
            #@TODO invio email all'utente
            return HttpResponseRedirect(reverse('albdif:profilo', kwargs={'pk': visitatore.utente.id}))

        return render(request, self.template_name, {
            'visitatore': visitatore,
            'camera': camera,
            'pagamento_form': pagamento_form,
        })


class camere_list(generic.ListView):
    """
    Ritorna la lista delle camere dell'AD principale ordinata per descrizione
    """
    template_name = "albdif/camere_list.html"
    context_object_name = "camere_list"

    def get_queryset(self):
        return Camera.objects.filter(proprieta__principale=True).order_by("descrizione")


class prezzo_camera_detail(generic.DetailView):
    model = PrezzoCamera
    template_name = "albdif/prezzo_camera_detail.html"


class prezzi_camera_list(generic.ListView):
    """
    Ritorna la lista dei prezzi di una camera
    @TODO modificare per accettare parametro ed elencare solo i prezzi di  una camera
    """
    template_name = "albdif/prezzi_camera_list.html"
    context_object_name = "prezzi_camera_list"

    def get_queryset(self):
        return PrezzoCamera.objects.order_by("camera.descrizione")


# PRENOTAZIONI
# class prenotazione_detail(generic.DetailView):
#     model = Prenotazione
#     template_name = "albdif/prenotazione_detail.html"
#
#     def get_context_data(self, **kwargs):
#         context = super(prenotazione_detail, self).get_context_data(**kwargs)
#
#         gia_prenotate = []
#         # estraggo solo i periodi che comprendono la data corrente e i futuri
#         periodi = CalendarioPrenotazione.objects.filter(prenotazione=self.object.pk, data_fine__gte=datetime.today())
#         for periodo in periodi:
#             for d in date_range(str(periodo.data_inizio), str(periodo.data_fine)):
#                 gia_prenotate.append(d)
#
#         context['disabled_dates'] = json.dumps(gia_prenotate)
#         return context


class prenotazioni_list(generic.ListView):
    template_name = "albdif/prenotazioni_list.html"
    context_object_name = "prenotazioni_list"

    def get_queryset(self):
        """Ritorna la lista delle prenotazioni ordinata per data più reente"""
        return Prenotazione.objects.order_by("-data_prenotazione")


# class prenotazioni_utente_list(generic.ListView):
#     template_name = "albdif/prenotazioni_list.html"
#     context_object_name = "prenotazioni_list"
#
#     def dispatch(self, request, *args, **kwargs):
#         """ La pagina del profilo può essere acceduta solo dal suo utente """
#         utente = Visitatore.objects.get(utente__pk=self.kwargs.get('pk'))
#         if utente != request.user:
#             messages.warning(request, 'Accesso ad altre prenotazioni non consentito!')
#             return redirect('albdif:home')
#             #raise PermissionDenied("Accesso ad altre prenotazioni non consentito")
#         return super().dispatch(request, *args, **kwargs)
#
#     def get_queryset(self):
#         """Ritorna la lista delle prenotazioni di un utente"""
#         utente_id = self.kwargs.get('pk')
#         return Prenotazione.objects.filter(visitatore__utente__id=utente_id).order_by("-data_prenotazione")
#
#     def get_context_data(self, **kwargs):
#         context = super(prenotazioni_utente_list, self).get_context_data(**kwargs)
#         return context


class calendario_prenotazione_detail(generic.DetailView):
    model = CalendarioPrenotazione
    template_name = "albdif/calendario_prenotazione_detail.html"


class calendario_prenotazioni_list(generic.ListView):
    template_name = "albdif/calendario_prenotazioni_list.html"
    context_object_name = "calendario_prenotazioni_list"

    def get_queryset(self):
        """Ritorna la lista delle date di prenotazione ordinata per data"""
        return CalendarioPrenotazione.objects.order_by("data_inizio")

