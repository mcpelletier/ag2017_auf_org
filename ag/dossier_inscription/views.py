# -*- encoding: utf-8 -*-
import collections
import datetime
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from ag.gestion import models as gestion_models
from ag.gestion import pdf
from ag.inscription.models import (
    Invitation,
    InvitationEnveloppe,
    Inscription,
    Adresse)
import ag.inscription.views as inscription_views
import auf.django.mailing.models as mailing
from ag.dossier_inscription import forms
from ag.dossier_inscription.models import InscriptionFermee
from ag.reference.models import Region, Pays

InfoVirement = collections.namedtuple(
    'InfoVirement', ('nom_region', 'releve', 'code_banque', 'code_guichet',
                     'num_compte', 'cle_rib', 'id_international', 'iban',
                     'bic', 'domiciliation', 'titulaire'))


def handle_invites_formset(request, inscription):
    if request.method == 'POST' and 'submit-invites-formset' in request.POST:
        invites_formset = forms.InvitesFormSet(request.POST)
        if envoyer_invitations(inscription, invites_formset):
            # si pas d'erreur on présente des formulaires vides pour
            # autres invités
            invites_formset = forms.InvitesFormSet()
    else:
        invites_formset = forms.InvitesFormSet()
    return invites_formset


def handle_plan_vol_form(request, dossier):
    if request.method == 'POST' and 'submit-plan-vol-form' in request.POST:
        form = forms.PlanVolForm(request.POST)
        if form.is_valid():
            infos = gestion_models.InfosDepartArrivee(**form.cleaned_data)
            dossier.set_infos_depart_arrivee(infos)
    else:
        infos = dossier.get_infos_depart_arrivee()
        # noinspection PyProtectedMember
        form = forms.PlanVolForm(initial=infos._asdict())
    return form


def handle_reseautage(request, inscription):
    liste_reseautage = Inscription.objects \
        .filter(reseautage=True, fermee=True) \
        .exclude(pk=inscription.id) \
        .select_related('invitation', 'invitation__etablissement',
                        'invitation__etablissement__region',
                        'invitation__etablissement__pays') \
        .order_by('nom', 'prenom')
    region = request.GET.get('region')
    pays = request.GET.get('pays') if region else None
    if region:
        liste_reseautage = liste_reseautage.filter(
            invitation__etablissement__region__id=region)
    if pays:
        liste_reseautage = liste_reseautage.filter(
            invitation__etablissement__pays__id=pays)
    regions_inscriptions = Inscription.objects \
        .filter(reseautage=True) \
        .values_list('invitation__etablissement__region', flat=True) \
        .distinct()
    regions = [(r.id, r.nom) for r in
               Region.objects.filter(id__in=regions_inscriptions)]
    """:type : list[int|None, str]"""
    pays_inscriptions = Inscription.objects \
        .filter(invitation__etablissement__region=region,
                reseautage=True) \
        .values_list('invitation__etablissement__pays', flat=True) \
        .distinct() if region else []
    payss = [(p.id, p.nom) for p in
             Pays.objects.filter(id__in=pays_inscriptions)]
    """:type : list[int|None, str]"""
    form_filtre_reseautage = forms.FiltreReseautageForm(
        [(None, 'Toutes')] + regions,
        [(None, 'Tous')] + payss, initial={'region': region,
                                           'pays': pays})
    return form_filtre_reseautage, liste_reseautage


def vue_dossier(request):
    inscription_id = request.session.get('inscription_id', None)
    if not inscription_id:
        return redirect('connexion_inscription')
    inscription = InscriptionFermee.objects.get(id=inscription_id)
    if not inscription.fermee:
        return redirect(reverse('connexion_inscription'))

    dossier = inscription.dossier
    adresse = dossier.get_adresse()
    participant = inscription.get_participant()

    activites = {a.code: a.libelle
                 for a in gestion_models.Activite.objects.all()}

    # noinspection PyProtectedMember
    context = {
        'dossier': dossier,
        'inscription': inscription,
        'participant': participant,
        'adresse': adresse,
        'suivi': inscription.get_suivi_dossier(),
        'solde': inscription.get_solde(),
        'form_adresse': forms.AdresseForm(initial=adresse._asdict()),
        'info_virement': INFOS_VIREMENT.get(inscription.get_region().code),
        'region': inscription.get_region(),
        'invitations_accompagnateurs':
            inscription.get_invitations_accompagnateurs(),
        'invites_formset': handle_invites_formset(request, inscription),
        'inscriptions_terminees': inscription_views.inscriptions_terminees(),
        'avant_31_decembre': (datetime.datetime.today() <
                              datetime.datetime(2017, 1, 31)),
        'plan_vol_form': handle_plan_vol_form(request, dossier),
        'activites': activites,
        'titre_facture': pdf.titre_facture(participant or inscription)
    }

    if participant:
        context['passeport_form'] = forms.AjoutPasseportForm(
            instance=participant)

    if inscription.reseautage:
        form_filtre_reseautage, liste_reseautage = handle_reseautage(
            request, inscription)
        context['liste_reseautage'] = list(liste_reseautage)
        context['form_filtre_reseautage'] = form_filtre_reseautage

    context.update(inscription_views.get_paypal_context(request))
    return render(request, 'dossier_inscription/dossier.html', context)


@require_POST
def upload_passeport(request):
    inscription = InscriptionFermee.objects.get(
        id=request.session.get('inscription_id', None))
    if not inscription.a_televerse_passeport():
        fichier = gestion_models.Fichier(
            participant=inscription.get_participant())
        form = forms.AjoutPasseportForm(
            request.POST, request.FILES, instance=fichier)
        if form.is_valid():
            form.save()
    return redirect(reverse('dossier_inscription') + '#passeport')


@require_POST
def set_adresse(request):
    inscription_id = request.session.get('inscription_id', None)
    if not inscription_id:
        return redirect('connexion_inscription')
    dossier = InscriptionFermee.objects.get(id=inscription_id).dossier
    form_adresse = forms.AdresseForm(request.POST)
    if form_adresse.is_valid():
        adresse_courante = dossier.get_adresse()
        nouvelle_adresse = Adresse(
            telephone=adresse_courante.telephone,
            telecopieur=adresse_courante.telecopieur,
            **form_adresse.cleaned_data)
        dossier.set_adresse(nouvelle_adresse)
    return render(request, 'dossier_inscription/includes/adresse.html',
                  {'adresse': dossier.get_adresse(),
                   'form_adresse': form_adresse})


def envoyer_invitations(inscription, formset):
    if (inscription.fermee and inscription.est_pour_mandate() and
            not inscription_views.inscriptions_terminees()):
        if formset.is_valid():
            modele_courriel = mailing.ModeleCourriel.objects.get(code='acc')
            for form in formset:
                if not form.cleaned_data:
                    continue
                nom = form.cleaned_data['nom']
                prenom = form.cleaned_data['prenom']
                adresse = form.cleaned_data['courriel']
                if not Invitation.objects.filter(courriel=adresse).count():
                    enveloppe = mailing.Enveloppe(modele=modele_courriel)
                    enveloppe.save()
                    invitation = Invitation(
                        courriel=adresse, pour_mandate=False,
                        etablissement=inscription.get_etablissement(),
                        nom=nom, prenom=prenom
                    )
                    invitation.save()
                    invitation_enveloppe = InvitationEnveloppe(
                        invitation=invitation, enveloppe=enveloppe
                    )
                    invitation_enveloppe.save()
            return True
        else:
            return False


@require_POST
def reseautage_on_off(request):
    inscription_id = request.session.get('inscription_id', None)
    if not inscription_id:
        return redirect('connexion_inscription')
    inscription = InscriptionFermee.objects.get(id=inscription_id)
    if request.POST.get('accepte_reseautage'):
        inscription.reseautage = True
        inscription.save()
    if request.POST.get('refuse_reseautage'):
        inscription.reseautage = False
        inscription.save()
    return redirect(reverse('dossier_inscription') + '#reseautage')


INFOS_VIREMENT = {
    "AP": InfoVirement(
        nom_region="Asie Pacifique",
        releve="RIB_AP", 
        code_banque="codebnk_AP",
        code_guichet="codguic_AP",
        num_compte="numcpt_AP",
        cle_rib="clerib_AP",
        id_international="idint_AP",
        iban="iban_AP",
        bic="bic_AP",
        domiciliation="domic_AP",
        titulaire="titulaire_AP"
    ),
    "MO": InfoVirement(
        nom_region="Moyen-Orient",
        releve="RIB_MO", 
        code_banque="codebnk_MO",
        code_guichet="codguic_MO",
        num_compte="numcpt_MO",
        cle_rib="clerib_MO",
        id_international="idint_MO",
        iban="iban_MO",
        bic="bic_MO",
        domiciliation="domic_MO",
        titulaire="titulaire_MO"
    ),
    "M": InfoVirement(
        nom_region="Maghreb",
        releve="RIB_M", 
        code_banque="codebnk_M",
        code_guichet="codguic_M",
        num_compte="numcpt_M",
        cle_rib="clerib_M",
        id_international="idint_M",
        iban="iban_M",
        bic="bic_M",
        domiciliation="domic_M",
        titulaire="titulaire_M"
    ),
    "EO": InfoVirement(
        nom_region="Europe occidentale",
        releve="RIB_EO", 
        code_banque="codebnk_EO",
        code_guichet="codguic_EO",
        num_compte="numcpt_EO",
        cle_rib="clerib_EO",
        id_international="idint_EO",
        iban="iban_EO",
        bic="bic_EO",
        domiciliation="domic_EO",
        titulaire="titulaire_EO"
    ),
    
}


def facture_dossier(request):
    inscription_id = request.session.get('inscription_id', None)
    inscription = get_object_or_404(InscriptionFermee, id=inscription_id)
    return pdf.facture_response(inscription.get_participant() or inscription)


def coupon_transport_dossier(request):
    inscription_id = request.session.get('inscription_id', None)
    inscription = get_object_or_404(InscriptionFermee, id=inscription_id)
    return pdf.coupon_transport_response(inscription.get_participant())
