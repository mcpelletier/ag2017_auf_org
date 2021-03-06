# -*- encoding: utf-8 -*-
import uuid
import datetime
import unittest
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.core import mail
from django.test import TestCase
from django.conf import settings
import html5lib


from ag.core import test_utils
from ag.gestion import consts
from ag.gestion import transfert_inscription
# noinspection PyUnresolvedReferences
from ag.gestion import notifications  # NOQA
from ag.gestion.models import *
from ag.gestion.models import get_fonction_repr_universitaire, \
    get_fonction_instance_seulement, get_fonction_personnel_auf
from ag.inscription.models import Inscription, Invitation, PaypalResponse, \
    get_forfaits, Forfait
from ag.core.test_utils import (
    find_input_by_id,
    find_input_by_name,
    find_checked_input_by_name,
    TypeInstitutionFactory,
    FonctionFactory,
    InstitutionFactory, ImplantationFactory)
from ag.tests import create_fixtures, creer_participant
from ag.reference.models import Etablissement, Pays, Region, Implantation


CODE_HOTEL = 'gtulip'
TYPE_CHAMBRE_TEST = consts.CHAMBRE_DOUBLE

VOL_TEST_DATA = {
    u'vols-TOTAL_FORMS': u'2',
    u'vols-INITIAL_FORMS': u'0',
    u'vols-MAX_NUM_FORMS': u'',
    u'vols-0-date_depart': u'02/06/2013',
    u'vols-0-heure_depart': u'12:00',
    u'vols-0-ville_depart': u'MONTREAL',
    u'vols-0-date_arrivee': u'03/06/2013',
    u'vols-0-heure_arrivee': u'15:00',
    u'vols-0-ville_arrivee': u'SAO PAOLO',
    u'vols-0-compagnie': u'AIR CANADA',
    u'vols-0-numero_vol': u'AC455',
    u'vols-0-prix': u'123,0',
    u'vols-0-DELETE': u'',
    u'vols-0-id': u'',
}


class GestionTestCase(TestCase):
    fixtures = ['test_data.json']

    def setUp(self):
        create_fixtures(self)
        self.client.login(username='john', password='johnpassword')

        self.participant = creer_participant()  # type: Participant

        participant_etablissement_membre = Participant()
        participant_etablissement_membre.nom = \
            'participant_etablissement_membre'
        participant_etablissement_membre.prenom = 'Testmembre'
        participant_etablissement_membre.adresse = 'adresse1'
        participant_etablissement_membre.code_postal = 'HHH 333'
        participant_etablissement_membre.courriel = 'adr.courriel@test.org'
        participant_etablissement_membre.date_naissance = \
            datetime.date(1973, 07, 04)
        participant_etablissement_membre.fonction = \
            self.fonction_repr_etablissement
        participant_etablissement_membre.etablissement \
            = Etablissement.objects.get(id=self.etablissement_id)
        participant_etablissement_membre.save()
        participant_etablissement_membre.suivi.add(
            PointDeSuivi.objects.get(code=POINT_DE_SUIVI_1)
        )
        participant_etablissement_membre.save()
        self.participant_etablissement_membre = \
            participant_etablissement_membre

    def tearDown(self):
        self.client.logout()

    def url_fiche_participant(self):
        return reverse('fiche_participant', args=[self.participant.id])

    def test_nom_institution_etablissement(self):
        participant = self.participant
        participant.fonction = get_fonction_repr_universitaire()
        etablissement = Etablissement.objects.get(id=self.etablissement_id)
        participant.etablissement = etablissement
        self.assertEquals(participant.nom_institution(), etablissement.nom)

    def test_nom_institution_instance_seulement(self):
        participant = self.participant
        participant.fonction = get_fonction_instance_seulement()
        participant.instance_auf = 'A'
        assert u"administration" in participant.nom_institution()

    def test_nom_institution_personnel_auf(self):
        participant = self.participant
        participant.fonction = get_fonction_personnel_auf()
        participant.implantation = ImplantationFactory(nom=u"impltest")
        assert participant.implantation.nom in participant.nom_institution()

    def test_nom_autre_institution(self):
        participant = self.participant
        type_institution = TypeInstitutionFactory()
        fonction = FonctionFactory(type_institution=type_institution)
        institution = InstitutionFactory(type_institution=type_institution)
        participant.fonction = fonction
        participant.institution = institution
        self.assertEquals(participant.nom_institution(),
                          institution.nom)

    def test_recherche_participant(self):
        response = self.client.get(reverse('participants'))
        self.assertEquals(response.status_code, 200)
        response = self.client.get(
            reverse('participants'),
            data={
                'nom': 'participant_etablissement_membre'})
        self.assertContains(response, reverse(
            'fiche_participant',
            args=[
                self.participant_etablissement_membre.id]))
        response = self.client.get(
            reverse('participants'),
            data={'etablissement': str(self.etablissement_id)})
        self.assertContains(
            response,
            reverse('fiche_participant',
                    args=[self.participant_etablissement_membre.id]))
        point_de_suivi = PointDeSuivi.objects.get(code=POINT_DE_SUIVI_1)
        response = self.client.get(reverse('participants'),
                                   data={'suivi': str(point_de_suivi.id)})
        self.assertContains(
            response,
            reverse('fiche_participant',
                    args=[self.participant_etablissement_membre.id]))

    def test_nouveau_participant_get_form(self):
        response = self.client.get(reverse('ajout_participant'))
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, u"Enregistrer et ajouter")

    def test_nouveau_participant_cancel_form(self):
        response = self.client.post(reverse('ajout_participant'),
                                    data={u'annuler': u'on'})
        self.assertRedirects(response, reverse('participants'))

    def nouveau_participant_data(self):
        return {
            u'nom': u'test_ajout_nom',
            u'prenom': u'test_prenom',
            u'courriel': u'test@test.com',
            u'etablissement': str(self.etablissement_id),
            u'etablissement_nom': u"jkjhjhghj",
            u'fonction': str(get_fonction_repr_universitaire().id),
        }

    def test_nouveau_participant(self):
        nb_participant_avant = Participant.objects.count()
        data = self.nouveau_participant_data()
        response = self.client.post(reverse('ajout_participant'), data=data)
        self.assertEquals(response.status_code, 302)
        self.assertEqual(Participant.objects.count(), nb_participant_avant + 1)
        participant = Participant.objects.get(nom=u'test_ajout_nom')
        self.assertRedirects(response, reverse('fiche_participant',
                                               args=[participant.id]))

    def test_nouveau_participant_puis_nouveau(self):
        data = self.nouveau_participant_data()
        data[u'enregistrer_et_nouveau'] = u'on'
        response = self.client.post(reverse('ajout_participant'), data=data)
        self.assertRedirects(response, reverse('ajout_participant', args=[]))

    def test_nouveau_participant_sans_etablissement(self):
        data = self.nouveau_participant_data()
        data[u'etablissement'] = u''
        response = self.client.post(reverse('ajout_participant'), data=data)
        self.assertContains(response, 'errors')

    def test_nouveau_participant_sans_institution(self):
        data = self.nouveau_participant_data()
        data[u'fonction'] = FonctionFactory(
            type_institution=TypeInstitutionFactory()).id
        response = self.client.post(reverse('ajout_participant'), data=data)
        self.assertContains(response, 'errors')

    def test_nouveau_participant_instance_seulement_pas_d_instance(self):
        data = self.nouveau_participant_data()
        data[u'fonction'] = get_fonction_instance_seulement().id
        response = self.client.post(reverse('ajout_participant'), data=data)
        self.assertContains(response, 'errors')

    def test_nouveau_participant_instance_seulement_ca(self):
        data = self.nouveau_participant_data()
        data[u'fonction'] = get_fonction_instance_seulement().id
        data[u'instance_auf'] = consts.CA
        response = self.client.post(reverse('ajout_participant'), data=data)
        self.assertContains(response, 'errors')

    def test_nouveau_participant_avec_institution(self):
        data = self.nouveau_participant_data()
        data[u'type_institution'] = u'I'
        data[u'nom'] = u'test_inst_auf'
        data[u'instance_auf'] = u'A'
        data[u'region'] = self.region.id
        response = self.client.post(reverse('ajout_participant'), data=data)
        participant = Participant.objects.get(nom=u'test_inst_auf')
        self.assertRedirects(response, reverse('fiche_participant',
                                               args=[participant.id]))

    def test_reservation_hotel(self):
        participant = self.participant
        participant.reserver_chambres('S', 1)
        participant.hotel = Hotel.objects.get(code=CODE_HOTEL)
        participant.date_arrivee_hotel = Participant.DATE_HOTEL_MIN
        participant.date_depart_hotel = Participant.DATE_HOTEL_MAX
        participant.save()
        self.assertEqual(participant.get_nombre_chambres('S'), 1)
        self.assertEqual(participant.get_nombre_chambres_total(), 1)
        reservations = ReservationChambre.objects.filter(
            participant=participant
        )
        self.assertEqual(len(reservations), 1)
        reservation = reservations[0]
        self.assertEqual(reservation.type_chambre, 'S')
        self.assertEqual(reservation.nombre, 1)
        hotel = Hotel.objects.get(code=CODE_HOTEL)
        self.assertEquals(
            hotel.nombre_chambres_simples_reservees(), 1)
        self.assertEquals(
            hotel.nombre_chambres_doubles_reservees(), 0)
        participant.reserver_chambres('D', 2)
        participant.save()
        participant = Participant.objects.get(id=participant.id)
        self.assertEqual(participant.get_nombre_chambres('S'), 1)
        self.assertEqual(participant.get_nombre_chambres('D'), 2)
        self.assertEqual(participant.get_nombre_chambres_total(), 3)
        reservations = ReservationChambre.objects \
            .filter(participant=participant, type_chambre='S')
        self.assertEqual(len(reservations), 1)
        reservation = reservations[0]
        self.assertEqual(reservation.type_chambre, consts.CHAMBRE_SIMPLE)
        self.assertEqual(reservation.nombre, 1)
        reservations = ReservationChambre.objects \
            .filter(participant=participant, type_chambre='D')
        self.assertEqual(len(reservations), 1)
        reservation = reservations[0]
        self.assertEqual(reservation.type_chambre, consts.CHAMBRE_DOUBLE)
        self.assertEqual(reservation.nombre, 2)
        hotel = Hotel.objects.get(code=CODE_HOTEL)
        self.assertEquals(
            hotel.nombre_chambres_simples_reservees(), 1)
        self.assertEquals(
            hotel.nombre_chambres_doubles_reservees(), 2)
        self.assertEquals(
            hotel.nombre_total_chambres_reservees(), 3)
        chambres = hotel.chambres()
        self.assertEquals(
            chambres[consts.CHAMBRE_SIMPLE]['nb_reservees'], 1)
        self.assertEquals(
            chambres[consts.CHAMBRE_DOUBLE]['nb_reservees'], 2)

    def test_fiche_participant(self):
        participant = self.participant
        response = self.client.get(reverse('fiche_participant',
                                           args=[participant.id]))
        self.assertEqual(response.status_code, 200)

    def test_renseignements_personnels_type_etablissement_obligatoire(self):
        data = {
            'nom': u'nom_nouveau',
            'prenom': u'prenom_nouveau',
            'courriel': u'nouveau@nouveau.org',
            'etablissement_nom': u'',
            'fonction': str(get_fonction_repr_universitaire().id),
        }
        response = self.client.post(reverse('ajout_participant'), data)
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, u"Ce champ est obligatoire")

    def test_sejour_form(self):
        participant = self.participant
        response = self.client.get(reverse('sejour', args=[participant.id]))
        self.assertEqual(response.status_code, 200)
        data = {}
        for activite in Activite.objects.all():
            self.assertContains(response, activite.libelle)
            data[u'activite_' + str(activite.id)] = u'on'
        data[u'reservation_par_auf'] = u'0'
        response = self.client.post(reverse('sejour', args=[participant.id]),
                                    data=data)
        self.assertRedirects(response, self.url_fiche_participant())
        participant = Participant.objects.get(pk=participant.id)
        for activite in Activite.objects.all():
            self.assertTrue(participant.get_participation_activite(activite))

    def test_notes_de_frais_form(self):
        participant = self.participant
        response = self.client.get(
            reverse('notes_de_frais', args=[participant.id]))
        self.assertEqual(response.status_code, 200)
        data = {
            u'frais_quantite_autres': u'1',
            u'frais_montant_autres': u'100',
            u'frais_quantite_taxi': u'2',
            u'frais_montant_taxi': u'100',
            u'modalite_versement_frais_sejour': u'I'
        }
        response = self.client.post(
            reverse('notes_de_frais', args=[participant.id]),
            data=data)
        self.assertRedirects(response, self.url_fiche_participant())
        participant = Participant.objects.get(pk=participant.id)
        self.assertEquals(participant.get_frais(
            TypeFrais.AUTRES_FRAIS).total(), 100)
        self.assertEquals(participant.get_frais(TypeFrais.TAXI).total(), 200)
        self.assertEquals(participant.modalite_versement_frais_sejour, u'I')

    def test_sejour_form_reservation_sans_hotel_sans_date_sans_chambre(self):
        participant = self.participant
        data = {u'reservation_par_auf': u'1'}
        response = self.client.post(reverse('sejour', args=[participant.id]),
                                    data=data)
        self.assertRedirects(response, self.url_fiche_participant())

    def test_sejour_form_reservation_avec_hotel_sans_date_sans_chambre(self):
        participant = self.participant
        data = {
            u'reservation_par_auf': u'1',
            u'hotel': unicode(str(Hotel.objects.get(code=CODE_HOTEL).id)),
        }
        response = self.client.post(reverse('sejour', args=[participant.id]),
                                    data=data)
        # si un hôtel est choisi, il faut le nb de chambres et les dates
        self.assertContains(response, 'error')

    def test_sejour_form_reservation_avec_hotel_avec_date_avec_chambre(self):
        participant = self.participant
        data = {
            u'reservation_par_auf': u'1',
            u'hotel': unicode(str(Hotel.objects.get(code=CODE_HOTEL).id)),
            u'chambre_S': u'1',
            u'chambre_D': u'0',
            u'date_arrivee': u'02/06/2013',
            u'date_depart': u'04/06/2013',
        }
        response = self.client.post(reverse('sejour', args=[participant.id]),
                                    data=data)
        self.assertRedirects(response, self.url_fiche_participant())
        reservations = participant.chambres_reservees()
        self.assertEqual(len(reservations), 1)
        self.assertEqual(reservations[0]['type']['code'], 'S')
        self.assertEqual(reservations[0]['nombre'], 1)

    def test_sejour_form_reservation_avec_hotel_avec_date_erronee(self):
        participant = self.participant
        data = {
            u'reservation_par_auf': u'1',
            u'hotel': unicode(str(Hotel.objects.get(code=CODE_HOTEL).id)),
            u'chambre_S': u'1',
            u'chambre_D': u'0',
            u'date_arrivee': u'04/06/2013',
            u'date_depart': u'02/06/2013',
        }
        # erreur si la date d'arrivée est postérieure à la date de départ
        response = self.client.post(reverse('sejour', args=[participant.id]),
                                    data=data)
        self.assertContains(response, 'error')

    def test_sejour_form_reservation_avec_hotel_avec_date_sans_chambre(self):
        participant = self.participant
        data = {
            u'reservation_par_auf': u'1',
            u'hotel': unicode(str(Hotel.objects.get(code=CODE_HOTEL).id)),
            u'chambre_S': u'0',
            u'chambre_D': u'0',
            u'date_arrivee': u'02/06/2013',
            u'date_depart': u'04/06/2013',
        }
        response = self.client.post(reverse('sejour', args=[participant.id]),
                                    data=data)
        self.assertContains(response, 'error')

    def test_sejour_form_reservation_avec_hotel_sans_date_avec_chambre(self):
        participant = self.participant
        data = {
            u'reservation_par_auf': u'1',
            u'hotel': unicode(str(Hotel.objects.get(code=CODE_HOTEL).id)),
            u'chambre_S': u'1',
            u'chambre_D': u'0',
        }
        response = self.client.post(reverse('sejour', args=[participant.id]),
                                    data=data)
        self.assertContains(response, 'error')

    def test_sejour_form_sans_reservation_avec_hotel_sans_date_sans_chambre(
            self):
        participant = self.participant
        data = {
            u'reservation_par_auf': u'0',
            u'hotel': unicode(str(Hotel.objects.get(code=CODE_HOTEL).id)),
        }
        response = self.client.post(reverse('sejour', args=[participant.id]),
                                    data=data)
        self.assertRedirects(response, self.url_fiche_participant())

    def test_activites(self):
        participant = self.participant
        for activite in Activite.objects.all():
            self.assertFalse(participant.get_participation_activite(activite))
        for activite in Activite.objects.all():
            participant.inscrire_a_activite(activite, avec_invites=True)
        for activite in Activite.objects.all():
            self.assertTrue(
                participant.get_participation_activite(activite).avec_invites
            )

    def test_activites_forfaits_ajoutes(self):
        participant = self.participant
        activites = list(Activite.objects.filter(forfait_invite__isnull=False))
        participant.inscrire_a_activite(activites[0], avec_invites=True)
        participant.inscrire_a_activite(activites[1], avec_invites=False)
        forfaits_participant = participant.forfaits.all()
        assert activites[0].forfait_invite in forfaits_participant
        assert activites[1].forfait_invite not in forfaits_participant

    def test_activites_forfaits_retires(self):
        participant = self.participant
        activites = list(Activite.objects.filter(forfait_invite__isnull=False))
        participant.inscrire_a_activite(activites[0], avec_invites=True)
        participant.desinscrire_d_activite(activites[0])
        forfaits_participant = participant.forfaits.all()
        assert activites[0].forfait_invite not in forfaits_participant

    def test_transport_organise_participant(self):
        participant = self.participant
        response = self.client.get(reverse('transport', args=[participant.id]))
        self.assertEqual(response.status_code, 200)
        data = {
            u'vols-TOTAL_FORMS': u'1',
            u'vols-INITIAL_FORMS': u'0',
            u'vols-MAX_NUM_FORMS': u'',
            u'vols-0-date_depart': u'',
            u'vols-0-heure_depart': u'',
            u'vols-0-ville_depart': u'',
            u'vols-0-date_arrivee': u'',
            u'vols-0-heure_arrivee': u'',
            u'vols-0-ville_arrivee': u'',
            u'vols-0-compagnie': u'',
            u'vols-0-numero_vol': u'',
            u'vols-0-prix': u'',
            u'vols-0-DELETE': u'',
            u'vols-0-id': u'',
            u'top-transport_organise_par_auf': u'False',
            u'arrdep-date_depart': u'2/6/2013',
            u'arrdep-heure_depart': u'12:00',
            u'arrdep-compagnie_depart': u'AIR FRANCE',
            u'arrdep-numero_vol_depart': u'AF627',
            u'arrdep-date_arrivee': u'5/6/2013',
            u'arrdep-heure_arrivee': u'15:00',
            u'arrdep-compagnie_arrivee': u'AIR FRANCE',
            u'arrdep-numero_vol_arrivee': u'AF627',
        }
        response = self.client.post(
            reverse('transport', args=[participant.id]),
            data=data
        )
        self.assertRedirects(response, self.url_fiche_participant())
        response = self.client.get(reverse('transport', args=[participant.id]))
        infos = participant.get_infos_depart()
        self.assertEquals(infos.compagnie, u'AIR FRANCE')
        infos = participant.get_infos_arrivee()
        self.assertEquals(infos.numero_vol, u'AF627')
        tree = html5lib.parse(response.content, treebuilder='lxml',
                              namespaceHTMLElements=False)
        input_element = find_input_by_name(tree,
                                           "top-transport_organise_par_auf")

        self.assertEqual(input_element.get("value"), "False")
        input_element = find_input_by_id(tree,
                                         "id_arrdep-date_arrivee")
        self.assertEqual(input_element.get("value"), "05/06/2013")

    def test_transport_organise_auf(self):
        participant = self.participant
        data = {
            u'top-transport_organise_par_auf': u'True',
            u'top-statut_dossier_transport': u'E',
            u'top-numero_dossier_transport': u'4544',
            u'top-modalite_retrait_billet': u'0'
        }
        data.update(VOL_TEST_DATA)
        response = self.client.post(
            reverse('transport', args=[participant.id]),
            data=data
        )
        self.assertRedirects(response, self.url_fiche_participant())
        participant = Participant.objects.get(id=participant.id)
        assert participant.transport_organise_par_auf
        response = self.client.get(reverse('transport', args=[participant.id]))
        # with open("/media/benselme/data/output.txt", "w") as text_file:
        #     text_file.write(response.content)
        tree = html5lib.parse(response.content, treebuilder='lxml',
                              namespaceHTMLElements=False)
        input_element = find_checked_input_by_name(
            tree, "top-transport_organise_par_auf")

        self.assertEqual(input_element.get("value"), "True")
        input_element = find_input_by_id(tree,
                                         "id_vols-0-date_depart")
        self.assertEqual(input_element.get("value"), "02/06/2013")

    def test_invites(self):
        participant = self.participant
        response = self.client.get(reverse('transport', args=[participant.id]))
        self.assertContains(response, u'Aucun invité')
        response = self.client.get(reverse('invites', args=[participant.id]))
        self.assertEqual(response.status_code, 200)
        data = {
            u'invite_set-TOTAL_FORMS': u'1',
            u'invite_set-INITIAL_FORMS': u'0',
            u'invite_set-MAX_NUM_FORMS': u'',
            u'invite_set-0-genre': u'M',
            u'invite_set-0-nom': u'nom_invite',
            u'invite_set-0-prenom': u'prenom_invite',
            u'invite_set-0-DELETE': u'',
            u'invite_set-0-participant': unicode(participant.id),
            # u'invite_set-0-id': u'None',
        }
        response = self.client.post(reverse('invites', args=[participant.id]),
                                    data=data)
        self.assertRedirects(response, self.url_fiche_participant())
        response = self.client.get(reverse('invites', args=[participant.id]))
        tree = html5lib.parse(response.content, treebuilder='lxml',
                              namespaceHTMLElements=False)
        input_element = find_input_by_name(tree, "invite_set-0-nom")
        self.assertEqual(input_element.get('value'), "nom_invite")
        response = self.client.get(reverse('transport', args=[participant.id]))
        self.assertContains(response, u'1 invité')

    def test_facturation_edition(self):
        participant = self.participant
        imp_id = Implantation.objects.create(nom='aa', nom_court='nb').id
        response = self.client.get(
            reverse('facturation', args=[participant.id])
        )
        self.assertEquals(response.status_code, 200)
        data = {
            u'prise_en_charge_hebergement': u'on',
            u'prise_en_charge_sejour': u'on',
            u'facturation_validee': u'',
            u'date_facturation': u'',
            u'imputation': u'A0394DRI017B3',
            u'notes_facturation': u'',
            u'paiement_set-TOTAL_FORMS': u'1',
            u'paiement_set-INITIAL_FORMS': u'0',
            u'paiement_set-MAX_NUM_FORMS': u'1000',
            u'paiement_set-0-id': u'',
            u'paiement_set-0-date': u'26/10/2016',
            u'paiement_set-0-moyen': u'VB',
            u'paiement_set-0-implantation': unicode(imp_id),
            u'paiement_set-0-ref': u'abcd',
            u'paiement_set-0-montant_euros': u'100.30',
            u'paiement_set-0-participant': unicode(participant.id),
        }
        response = self.client.post(
            reverse('facturation', args=[participant.id]),
            data=data
        )
        self.assertRedirects(response, self.url_fiche_participant())
        participant = Participant.objects.get(pk=participant.id)
        response = self.client.get(
            reverse('facturation', args=[participant.id])
        )
        tree = html5lib.parse(response.content, treebuilder='lxml',
                              namespaceHTMLElements=False)
        input_element = tree.find("//option[@value='{0}']".format(
            data[u'imputation']))
        self.assertEqual(input_element.get('selected'), 'selected')

    def test_numero_facture(self):
        participant = self.participant
        self.assertTrue(participant.numero_facture is None)
        participant.facturation_validee = True
        participant.save()
        self.assertEquals(participant.numero_facture, 1)
        self.assertEquals(
            participant.date_facturation, datetime.datetime.now().date()
        )
        # vérifie qu'on ne génère pas un numéro lorsqu'il y en a déjà un
        participant.facturation_validee = True
        participant.save()
        self.assertEquals(participant.numero_facture, 1)
        self.assertEquals(
            participant.date_facturation, datetime.datetime.now().date()
        )
        participant.facturation_validee = False
        participant.save()
        self.assertTrue(participant.numero_facture is None)
        self.assertTrue(participant.date_facturation is None)
        # teste que les numéros s'incrémentent bien par établissement
        participant = self.participant_etablissement_membre
        participant.facturation_validee = True
        participant.save()
        self.assertEquals(participant.numero_facture, 1)
        # on en crée un deuxième dans le même établissement
        participant.id = None
        participant.facturation_validee = False
        participant.numero_facture = None
        participant.date_facturation = None
        participant.save()
        self.assertTrue(participant.numero_facture is None)
        participant.facturation_validee = True
        participant.save()
        self.assertEquals(participant.numero_facture, 2)
        participant.id = None
        participant.facturation_validee = False
        participant.numero_facture = None
        participant.date_facturation = None
        participant.etablissement = Etablissement.objects.get(
            pk=self.etablissement_nord_id
        )
        participant.save()
        self.assertTrue(participant.numero_facture is None)
        participant.facturation_validee = True
        participant.save()
        self.assertEquals(participant.numero_facture, 1)

    def test_montants_facturation(self):
        participant = Participant.objects \
            .sql_extra_fields('total_frais') \
            .get(id=self.participant.id)
        forfaits = get_forfaits()
        self.assertEquals(participant.total_frais,
                          forfaits[consts.CODE_FRAIS_INSCRIPTION].montant)

        invite = Invite(genre='M', nom='nom_invite', prenom='prenom_invite')
        invite.participant = participant
        invite.save()
        participant = Participant.objects \
            .sql_extra_fields('total_frais') \
            .get(id=self.participant.id)
        montant_attendu = forfaits[consts.CODE_FRAIS_INSCRIPTION].montant
        self.assertEquals(participant.total_frais, montant_attendu)

        activite = Activite.objects.get(code='gala')
        participant.inscrire_a_activite(activite, avec_invites=False)
        participant = Participant.objects \
            .sql_extra_fields('total_frais', 'total_facture') \
            .get(id=self.participant.id)
        self.assertEquals(participant.total_frais, montant_attendu)
        self.assertEquals(participant.total_facture, montant_attendu)

        participant.inscrire_a_activite(activite, avec_invites=True)
        participant = Participant.objects \
            .sql_extra_fields('total_frais', 'total_facture') \
            .get(id=self.participant.id)
        if activite.forfait_invite:
            montant_attendu += activite.forfait_invite.montant
        self.assertEquals(participant.total_frais, montant_attendu)
        self.assertEquals(participant.total_facture, montant_attendu)

        infos_vol = InfosVol(prix=999, participant=participant,
                             type_infos=consts.VOL_ORGANISE)
        infos_vol.save()
        participant.prise_en_charge_transport = True
        participant.transport_organise_par_auf = True
        participant.save()
        participant = Participant.objects \
            .sql_extra_fields('total_frais', 'total_facture') \
            .get(id=self.participant.id)
        self.assertEquals(participant.total_facture, montant_attendu)
        participant.prise_en_charge_transport = False
        participant.save()
        participant = Participant.objects \
            .sql_extra_fields('total_frais', 'total_facture') \
            .get(id=self.participant.id)
        montant_attendu += infos_vol.prix
        self.assertEquals(participant.total_frais, montant_attendu)
        self.assertEquals(participant.total_facture, montant_attendu)

        montant_avant_frais = montant_attendu
        participant.set_frais(TypeFrais.AUTRES_FRAIS, 1, 99)
        participant = Participant.objects \
            .sql_extra_fields('total_frais', 'total_facture') \
            .get(id=self.participant.id)
        self.assertEquals(participant.total_facture, montant_avant_frais)
        montant_attendu += 99
        self.assertEquals(participant.total_frais, montant_attendu)

        participant.set_frais(TypeFrais.REPAS, 1, 101)
        participant = Participant.objects \
            .sql_extra_fields('total_frais', 'total_facture') \
            .get(id=self.participant.id)
        self.assertEquals(participant.total_facture, montant_avant_frais)
        montant_attendu += 101
        self.assertEquals(participant.total_frais, montant_attendu)

    def set_hotel_participant(self):
        participant = self.participant
        hotel = Hotel.objects.get(code=CODE_HOTEL)
        participant.hotel = hotel
        participant.reserver_chambres(TYPE_CHAMBRE_TEST, 1)
        participant.reservation_hotel_par_auf = True
        participant.prise_en_charge_sejour = True
        participant.save()
        return hotel

    def test_facturation_hotel_nb_jours(self):
        participant = Participant.objects \
            .sql_extra_fields('total_frais', 'total_facture') \
            .get(id=self.participant.id)
        montant_frais_sans_hotel = participant.total_frais
        montant_facture_sans_hotel = participant.total_facture
        hotel = self.set_hotel_participant()
        participant = Participant.objects \
            .sql_extra_fields('total_frais', 'total_facture') \
            .get(id=self.participant.id)
        participant.date_arrivee_hotel = Participant.DATE_HOTEL_MIN
        participant.date_depart_hotel = (participant.date_arrivee_hotel +
                                         datetime.timedelta(days=1))
        participant.save()
        prix_chambre = hotel.chambre_set.get(
            type_chambre=TYPE_CHAMBRE_TEST).prix

        participant = Participant.objects \
            .sql_extra_fields('total_frais', 'total_facture') \
            .get(id=self.participant.id)
        self.assertEqual(participant.total_frais,
                         montant_frais_sans_hotel + prix_chambre,
                         msg=str(participant.total_frais) + '/' + str(
                             participant.total_facture))
        self.assertEqual(participant.total_facture,
                         montant_facture_sans_hotel)
        participant.date_depart_hotel = (participant.date_arrivee_hotel +
                                         datetime.timedelta(days=2))
        participant.save()
        participant = Participant.objects \
            .sql_extra_fields('total_frais', 'total_facture') \
            .get(id=self.participant.id)
        self.assertEqual(participant.total_frais,
                         montant_frais_sans_hotel + prix_chambre * 2)
        self.assertEqual(participant.total_facture,
                         montant_facture_sans_hotel)
        participant.prise_en_charge_sejour = False
        participant.save()
        participant = Participant.objects \
            .sql_extra_fields('total_frais', 'total_facture') \
            .get(id=self.participant.id)
        self.assertEqual(participant.total_frais,
                         montant_frais_sans_hotel + prix_chambre * 2)
        self.assertEqual(participant.total_facture,
                         participant.total_frais)
        participant.ajouter_forfait(consts.CODE_SUPPLEMENT_CHAMBRE_DOUBLE)
        participant.prise_en_charge_sejour = True
        participant.save()
        montant_supplement_chambre_double = \
            get_forfaits()[consts.CODE_SUPPLEMENT_CHAMBRE_DOUBLE].montant
        participant = Participant.objects \
            .sql_extra_fields('total_frais', 'total_facture') \
            .get(id=self.participant.id)
        self.assertEqual(participant.total_frais,
                         montant_frais_sans_hotel + prix_chambre * 2)
        self.assertEqual(participant.total_facture,
                         montant_frais_sans_hotel +
                         montant_supplement_chambre_double)

    def test_problemes_hotel(self):
        participant = self.participant
        participant.prise_en_charge_sejour = True
        participant.reservation_hotel_par_auf = True
        participant.hotel = None
        participant.save()
        participant = Participant.objects \
            .sql_extra_fields('problematique', 'hotel_manquant') \
            .get(id=self.participant.id)
        self.assertTrue(participant.problematique)
        self.assertTrue(participant.hotel_manquant)
        participant.reserver_chambres('S', 1)
        participant.hotel = Hotel.objects.get(code=CODE_HOTEL)
        participant.save()
        participant = Participant.objects \
            .sql_extra_fields('hotel_manquant') \
            .get(id=self.participant.id)
        self.assertFalse(participant.hotel_manquant)
        invite = Invite(genre='M', nom='test_invite', prenom='prenom_invite')
        invite.participant = participant
        invite.save()
        participant = Participant.objects \
            .sql_extra_fields('problematique', 'nb_places_incorrect') \
            .get(id=self.participant.id)
        self.assertTrue(participant.problematique)
        self.assertTrue(participant.nb_places_incorrect)

    def test_nombres_activites(self):
        participant = self.participant
        for activite in Activite.objects.with_stats().all():
            participant.inscrire_a_activite(activite, avec_invites=False)
        for activite in Activite.objects.with_stats().all():
            with self.assertNumQueries(0):
                self.assertEqual(activite.nombre_non_pris_en_charge(), 1)
        participant2 = participant
        participant2.id = None
        participant2.prise_en_charge_activites = True
        participant2.save()
        for activite in Activite.objects.with_stats().all():
            participant2.inscrire_a_activite(activite, avec_invites=False)
        for activite in Activite.objects.with_stats().all():
            with self.assertNumQueries(0):
                self.assertEqual(activite.nombre_non_pris_en_charge(), 1)
                self.assertEqual(activite.nombre_pris_en_charge(), 1)
        participant3 = participant
        participant3.id = None
        participant3.prise_en_charge_activites = True
        participant3.save()
        invite = Invite(
            genre='M', nom='invite', prenom='prenom', participant=participant3
        )
        invite.save()
        self.assertEqual(participant3.nombre_invites(), 1)
        for activite in Activite.objects.with_stats().all():
            participant3.inscrire_a_activite(activite, avec_invites=True)

        for activite in Activite.objects.with_stats().all():
            with self.assertNumQueries(0):
                self.assertEqual(activite.nombre_non_pris_en_charge(), 1)
                self.assertEqual(activite.nombre_pris_en_charge(), 2)
                self.assertEqual(activite.nombre_invites(), 1)

    def test_frais(self):
        participant = self.participant
        participant.set_frais(TypeFrais.AUTRES_FRAIS, 1, 99)
        self.assertEquals(
            participant.get_frais(TypeFrais.AUTRES_FRAIS).total(), 99)
        participant.set_frais(TypeFrais.AUTRES_FRAIS, 1, 0)
        self.assertEquals(participant.get_frais(TypeFrais.AUTRES_FRAIS), None)
        participant.set_frais(TypeFrais.AUTRES_FRAIS, 2, 100)
        self.assertEquals(
            participant.get_frais(TypeFrais.AUTRES_FRAIS).total(), 200)

    def test_frais_transport(self):
        participant = self.participant
        participant.transport_organise_par_auf = True
        participant.save()
        infos_vol = InfosVol()
        infos_vol.date_depart = datetime.date.today()
        infos_vol.ville_depart = u'PARIS'
        infos_vol.date_arrivee = datetime.date.today()
        infos_vol.ville_depart = u'SAO PAULO'
        infos_vol.prix = 100
        infos_vol.TYPE_VOL = consts.VOL_ORGANISE
        infos_vol.participant = participant
        infos_vol.save()
        participant = Participant.actifs.sql_extra_fields('frais_transport') \
            .get(id=participant.id)
        self.assertEqual(participant.frais_transport, 100)
        infos_vol = InfosVol()
        infos_vol.date_depart = datetime.date.today()
        infos_vol.ville_depart = u'SAO PAULO'
        infos_vol.date_arrivee = datetime.date.today()
        infos_vol.ville_depart = u'PARIS'
        infos_vol.TYPE_VOL = consts.VOL_ORGANISE
        infos_vol.participant = participant
        infos_vol.save()
        # on vérifie que pour qu'un prix NULL est considéré comme 0
        participant = Participant.actifs.sql_extra_fields('frais_transport') \
            .get(id=participant.id)
        self.assertEqual(participant.frais_transport, 100)
        # on vérifie que les frais ne sont pas comptabilisés si le transport
        # n'est pas organisé par l'AUF
        participant.transport_organise_par_auf = False
        participant.save()
        participant = Participant.actifs.sql_extra_fields('frais_transport') \
            .get(id=participant.id)
        self.assertEqual(participant.frais_transport, 0)

    def test_forfaits_invites(self):
        p = Participant.objects.sql_extra_fields('forfaits_invites') \
            .get(id=self.participant.id)
        self.assertEqual(p.forfaits_invites, 0)
        invite = Invite(nom=u"invité", prenom=u"prénom", participant=p)
        invite.save()
        avec_invites = True
        for activite in Activite.objects.all():
            forfaits_invites = p.forfaits_invites
            p.inscrire_a_activite(activite, avec_invites=avec_invites)
            p = Participant.objects.sql_extra_fields('forfaits_invites') \
                .get(id=self.participant.id)
            self.assertTrue(p.get_participation_activite(activite))
            self.assertEqual(p.forfaits_invites - forfaits_invites,
                             (activite.forfait_invite.montant
                              if activite.forfait_invite else 0)
                             if avec_invites else 0)
            avec_invites = not avec_invites

    def test_deja_paye(self):
        p = test_utils.ParticipantFactory()  # type: Participant
        test_utils.PaiementFactory(participant=p, montant_euros=50)
        test_utils.PaiementFactory(participant=p, montant_euros=50)
        assert p.total_deja_paye == 100

    def test_deja_paye_paypal(self):
        p = self.get_participant_avec_paypal()
        assert p.total_deja_paye == 175

    @staticmethod
    def get_participant_avec_paypal():
        i = test_utils.InscriptionFactory()  # type: Inscription
        p = test_utils.ParticipantFactory(inscription=i)  # type: Participant
        test_utils.PaiementFactory(participant=p, montant_euros=50)
        test_utils.PaiementFactory(participant=p, montant_euros=50)
        inv1_uid = uuid.uuid4()
        inv2_uid = uuid.uuid4()
        PaypalResponse.objects.create(
            montant=50, inscription=i, invoice_uid=inv1_uid,
            validated=True, type_reponse='IPN', statut='Completed',
            txn_id='A')
        PaypalResponse.objects.create(
            montant=50, inscription=i, invoice_uid=inv1_uid,
            validated=True, type_reponse='PDT', statut='Completed',
            txn_id='A')
        PaypalResponse.objects.create(
            montant=25, inscription=i, invoice_uid=inv2_uid,
            validated=True, type_reponse='IPN', statut='Completed',
            txn_id='B')
        return p

    # noinspection PyMethodMayBeStatic
    def test_verse_en_trop(self):
        p = test_utils.ParticipantFactory()  # type: Participant
        test_utils.PaiementFactory(participant=p, montant_euros=100)
        p.total_facture = 50
        assert p.get_verse_en_trop() == 50
        p.total_facture = 150
        assert p.get_verse_en_trop() == 0

    # noinspection PyMethodMayBeStatic
    def test_solde_a_payer(self):
        p = test_utils.ParticipantFactory()  # type: Participant
        test_utils.PaiementFactory(participant=p, montant_euros=100)
        p.total_facture = 50
        assert p.get_solde_a_payer() == 0
        p.total_facture = 150
        assert p.get_solde_a_payer() == 50

    def test_total_deja_paye__sans_paypal_sql(self):
        p = test_utils.ParticipantFactory()  # type: Participant
        test_utils.PaiementFactory(participant=p, montant_euros=100)
        test_utils.PaiementFactory(participant=p, montant_euros=100)
        p = Participant.objects \
            .sql_extra_fields('total_deja_paye_sql').get(id=p.id)
        assert p.total_deja_paye_sql == 200

    def test_total_deja_paye_zero(self):
        p = test_utils.ParticipantFactory()  # type: Participant
        p = Participant.objects \
            .sql_extra_fields('total_deja_paye_sql').get(id=p.id)
        assert p.total_deja_paye_sql == 0

    def test_total_deja_paye_sql_paypal(self):
        p = self.get_participant_avec_paypal()
        p = Participant.objects \
            .sql_extra_fields('total_deja_paye_sql').get(id=p.id)
        assert p.total_deja_paye_sql == 175

    def test_problemes_solde(self):
        def get_participant():
            return Participant.actifs \
                .sql_extra_fields('problematique', 'hotel_manquant', 'solde',
                                  'solde_a_payer', 'paiement_en_trop',
                                  'total_facture', 'frais_inscription') \
                .get(id=id_participant)

        id_participant = self.participant.id
        participant = get_participant()
        self.assertTrue(participant.problematique)
        self.assertTrue(participant.solde_a_payer)
        self.assertFalse(participant.paiement_en_trop)
        response = self.client.get(
            reverse('fiche_participant', args=(participant.id,)))
        self.assertNotContains(response,
                               consts.PROBLEMES['paiement_en_trop']['libelle'])
        self.assertContains(response,
                            consts.PROBLEMES['solde_a_payer']['libelle'])
        test_utils.PaiementFactory(montant_euros=participant.solde,
                                   moyen='VB', participant=participant)
        participant.save()
        participant = get_participant()
        self.assertFalse(participant.solde_a_payer)
        self.assertFalse(participant.paiement_en_trop)
        response = self.client.get(
            reverse('fiche_participant', args=(participant.id,)))
        self.assertNotContains(response,
                               consts.PROBLEMES['paiement_en_trop']['libelle'])
        self.assertNotContains(response,
                               consts.PROBLEMES['solde_a_payer']['libelle'])
        test_utils.PaiementFactory(montant_euros=1, moyen='VB',
                                   participant=participant)
        participant = get_participant()
        self.assertTrue(participant.problematique)
        self.assertFalse(participant.solde_a_payer)
        self.assertTrue(participant.paiement_en_trop)
        response = self.client.get(
            reverse('fiche_participant', args=(participant.id,)))
        self.assertContains(response,
                            consts.PROBLEMES['paiement_en_trop']['libelle'])
        self.assertNotContains(response,
                               consts.PROBLEMES['solde_a_payer']['libelle'])

    def tests_probleme_reservation_hotel_manquante(self):
        p = self.participant
        p.prise_en_charge_sejour = True
        p.save()
        p = Participant.objects \
            .sql_extra_fields('problematique', 'reservation_hotel_manquante') \
            .get(id=p.id)
        self.assertTrue(p.problematique)
        self.assertTrue(p.reservation_hotel_manquante)
        p.prise_en_charge_sejour = False
        p.save()
        p = Participant.objects \
            .sql_extra_fields('problematique', 'reservation_hotel_manquante') \
            .get(id=p.id)
        self.assertFalse(p.reservation_hotel_manquante)

    def test_probleme_trajet_manquant(self):
        p = self.participant
        p.prise_en_charge_transport = True
        p.transport_organise_par_auf = True
        p.save()
        p = Participant.objects \
            .sql_extra_fields('problematique', 'trajet_manquant') \
            .get(id=p.id)
        self.assertTrue(p.problematique)
        self.assertTrue(p.trajet_manquant)

    def test_probleme_transport_non_organise(self):
        p = self.participant
        p.prise_en_charge_transport = True
        p.transport_organise_par_auf = False
        p.save()
        p = Participant.objects \
            .sql_extra_fields('problematique', 'transport_non_organise') \
            .get(id=p.id)
        self.assertTrue(p.problematique)
        self.assertTrue(p.transport_non_organise)
        p.transport_organise_par_auf = True
        p.save()
        p = Participant.objects \
            .sql_extra_fields('problematique', 'transport_non_organise') \
            .get(id=p.id)
        self.assertFalse(p.transport_non_organise)

    def creer_vol_groupe(self):
        vol_groupe = VolGroupe(nom=u"Test vol groupé", nombre_de_sieges=50)
        vol_groupe.save()
        infos_vol_aller = InfosVol(
            date_depart=datetime.date(2013, 5, 1),
            heure_depart=datetime.time(15, 10),
            ville_depart='PARIS',
            date_arrivee=datetime.date(2013, 5, 2),
            heure_arrivee=datetime.time(17, 10),
            ville_arrivee='SAO PAULO',
            compagnie='AIR FRANCE',
            numero_vol='AF615',
            prix=500,
            vol_groupe=vol_groupe,
            type_infos=consts.VOL_GROUPE
        )
        infos_vol_aller.save()
        infos_vol_retour = InfosVol(
            date_depart=datetime.date(2013, 5, 4),
            heure_depart=datetime.time(15, 10),
            ville_depart='SAO PAULO',
            date_arrivee=datetime.date(2013, 5, 5),
            heure_arrivee=datetime.time(17, 10),
            ville_arrivee='PARIS',
            compagnie='AIR FRANCE',
            numero_vol='AF616',
            prix=600,
            vol_groupe=vol_groupe,
            type_infos=consts.VOL_GROUPE
        )
        infos_vol_retour.save()
        participant = self.participant
        participant.transport_organise_par_auf = True
        participant.vol_groupe = vol_groupe
        participant.save()
        return vol_groupe, infos_vol_aller, infos_vol_retour

    def test_vol_groupe(self):
        vol_groupe, infos_vol_aller, infos_vol_retour = self.creer_vol_groupe()
        participant = self.participant
        participant = Participant.actifs.sql_extra_fields('frais_transport') \
            .get(id=participant.id)
        self.assertEqual(participant.frais_transport,
                         infos_vol_aller.prix + infos_vol_retour.prix)
        itineraire = participant.itineraire()
        self.assertEqual(itineraire[0], infos_vol_aller)
        self.assertEqual(itineraire[1], infos_vol_retour)

    def test_vols_groupe_et_non_groupe(self):
        vol_groupe, infos_vol_aller_groupe, infos_vol_retour_groupe = \
            self.creer_vol_groupe()
        participant = self.participant
        infos_vol_aller_organise = InfosVol(
            date_depart=datetime.date(2013, 4, 30),
            heure_depart=datetime.time(18, 10),
            ville_depart='MOSCOU',
            date_arrivee=datetime.date(2013, 5, 1),
            heure_arrivee=datetime.time(12, 00),
            ville_arrivee='PARIS',
            compagnie='AIR FRANCE',
            numero_vol='AF333',
            prix=400,
            participant=participant,
            type_infos=consts.VOL_ORGANISE
        )
        infos_vol_aller_organise.save()
        infos_vol_retour_organise = InfosVol(
            date_depart=datetime.date(2013, 5, 5),
            heure_depart=datetime.time(23, 50),
            ville_depart='PARIS',
            date_arrivee=datetime.date(2013, 5, 6),
            heure_arrivee=datetime.time(4, 00),
            ville_arrivee='MOSCOU',
            compagnie='AIR FRANCE',
            numero_vol='AF334',
            prix=401,
            participant=participant,
            type_infos=consts.VOL_ORGANISE
        )
        infos_vol_retour_organise.save()
        itineraire = participant.itineraire()
        self.assertEqual(itineraire[0], infos_vol_aller_organise)
        self.assertEqual(itineraire[1], infos_vol_aller_groupe)
        self.assertEqual(itineraire[2], infos_vol_retour_groupe)
        self.assertEqual(itineraire[3], infos_vol_retour_organise)
        participant = Participant.actifs.sql_extra_fields('frais_transport') \
            .get(id=participant.id)
        self.assertEqual(participant.frais_transport,
                         sum([vol.prix for vol in [infos_vol_aller_organise,
                                                   infos_vol_retour_organise,
                                                   infos_vol_aller_groupe,
                                                   infos_vol_retour_groupe]]))

    def test_page_etats_listes(self):
        response = self.client.get(reverse('etats_listes'))
        self.assertEqual(response.status_code, 200)

    def test_nombre_participants_point_de_suivi(self):
        def check_nombre(attendu):
            points_de_suivi = PointDeSuivi.objects.avec_nombre_participants() \
                .filter(code__in=attendu.keys())
            for point in points_de_suivi:
                self.assertEqual(attendu[point.code],
                                 point.nombre_participants)

        check_nombre({
            POINT_DE_SUIVI_1: 1,
            POINT_DE_SUIVI_2: 0,
            POINT_DE_SUIVI_3: 0,
        })
        self.participant.suivi.add(PointDeSuivi.objects.get(
            code=POINT_DE_SUIVI_1))
        check_nombre({
            POINT_DE_SUIVI_1: 2,
            POINT_DE_SUIVI_2: 0,
            POINT_DE_SUIVI_3: 0,
        })
        self.participant.suivi.add(PointDeSuivi.objects.get(
            code=POINT_DE_SUIVI_2))
        check_nombre({
            POINT_DE_SUIVI_1: 2,
            POINT_DE_SUIVI_2: 1,
            POINT_DE_SUIVI_3: 0,
        })
        self.participant_etablissement_membre.suivi.add(
            PointDeSuivi.objects.get(code=POINT_DE_SUIVI_2))
        check_nombre({
            POINT_DE_SUIVI_1: 2,
            POINT_DE_SUIVI_2: 2,
            POINT_DE_SUIVI_3: 0,
        })
        self.participant.suivi.remove(
            PointDeSuivi.objects.get(code=POINT_DE_SUIVI_1))
        check_nombre({
            POINT_DE_SUIVI_1: 1,
            POINT_DE_SUIVI_2: 2,
            POINT_DE_SUIVI_3: 0,
        })
        self.participant.desactive = True
        self.participant.save()
        check_nombre({
            POINT_DE_SUIVI_1: 1,
            POINT_DE_SUIVI_2: 1,
            POINT_DE_SUIVI_3: 0,
        })


POINT_DE_SUIVI_1 = 'compl_paris'
POINT_DE_SUIVI_2 = 'trans_complet'
POINT_DE_SUIVI_3 = 'fact_transm'


class TransfertInscription(TestCase):
    fixtures = ['test_data.json']

    def setUp(self):
        create_fixtures(self)

    def test_transfert_inscription(self):
        invitation = Invitation()
        invitation.pour_mandate = True
        invitation.etablissement = \
            Etablissement.objects.get(pk=self.etablissement_id)
        invitation.save()
        i = Inscription()
        i.genre = 'M'
        i.nom = u'Moon'
        i.prenom = u'Keith'
        i.nationalite = u'UK'
        i.date_naissance = datetime.date(1945, 2, 2)
        i.poste = u'Recteur'
        i.courriel = u'rd@who.net'
        i.adresse = u'adresse...'
        i.ville = u'London'
        i.pays = u'UK'
        i.code_postal = u'F3D 4P5'
        i.telephone = u"+34 1 55 5555"
        i.telecopieur = u"+34 1 55 5555"
        i.date_arrivee_hotel = datetime.date(2013, 5, 6)
        i.date_depart_hotel = datetime.date(2013, 5, 6)
        i.paiement = 'CB'
        i.invitation = invitation
        i.identite_confirmee = True
        i.conditions_acceptees = True
        i.accompagnateur = True
        i.accompagnateur_genre = 'M'
        i.accompagnateur_nom = u'Townshend'
        i.accompagnateur_prenom = u'Peter'
        i.programmation_soiree_9_mai = True
        i.programmation_soiree_9_mai_invite = True
        i.programmation_soiree_10_mai = True
        i.programmation_soiree_10_mai_invite_invite = False
        i.programmation_gala = False
        i.programmation_gala_invite = False
        i.prise_en_charge_hebergement = False
        i.prise_en_charge_transport = False
        i.forfait_invite_transfert = True
        i.forfait_invite_dejeuners = True
        i.arrivee_date = datetime.date(2013, 5, 1)
        i.arrivee_heure = datetime.time(10, 00)
        i.arrivee_vol = u'CA111'
        i.depart_de = 'sao-paolo'
        i.depart_date = datetime.date(2013, 5, 6)
        i.depart_heure = datetime.time(21, 00)
        i.depart_vol = u'CD454'
        i.fermee = True
        i.date_fermeture = datetime.date(2012, 7, 23)
        i.save()
        assert settings.DESTINATAIRES_NOTIFICATIONS['service_institutions']
        nb_mails_before = len(mail.outbox)
        p = transfert_inscription.transfere(i, False, False, False)
        self.assertEqual(len(mail.outbox), nb_mails_before + 1)
        self.assertEqual(p.nom, i.nom)
        self.assertEqual(p.pays, i.pays)
        self.assertEqual(
            ParticipationActivite.objects.filter(
                participant=p, activite__code=consts.CODE_SOIREE_9_MAI,
                avec_invites=True
            ).count(),
            1
        )
        self.assertEqual(p.fonction.code, consts.FONCTION_REPR_UNIVERSITAIRE)
        self.assertEqual(
            ParticipationActivite.objects.filter(
                participant=p, activite__code=consts.CODE_SOIREE_10_MAI,
                avec_invites=False
            ).count(),
            1
        )
        self.assertEqual(
            ParticipationActivite.objects.filter(
                participant=p, activite__code=consts.CODE_GALA
            ).count(),
            0
        )
        infos_arrivee = p.get_infos_arrivee()
        self.assertEqual(infos_arrivee.numero_vol, i.arrivee_vol)
        self.assertEqual(infos_arrivee.date_arrivee, i.arrivee_date)
        self.assertEqual(infos_arrivee.heure_arrivee, i.arrivee_heure)
        infos_depart = p.get_infos_depart()
        self.assertEqual(infos_depart.numero_vol, i.depart_vol)
        self.assertEqual(infos_depart.date_depart, i.depart_date)
        self.assertEqual(infos_depart.heure_depart, i.depart_heure)
        self.assertEqual(p.fonction.code, consts.FONCTION_REPR_UNIVERSITAIRE)
        self.assertEqual(p.etablissement, i.get_etablissement())
        self.assertTrue(p.a_forfait(consts.CODE_DEJEUNERS))
        self.assertTrue(p.a_forfait(consts.CODE_TRANSFERT_AEROPORT))
        self.assertEquals(len(Invite.objects.filter(participant=p)), 1)
        self.assertFalse(p.transport_organise_par_auf)
        self.assertFalse(p.reservation_hotel_par_auf)
        forfait_chambre_double = Forfait.objects.get(
            code=consts.CODE_SUPPLEMENT_CHAMBRE_DOUBLE)
        assert forfait_chambre_double not in p.forfaits.all()
        p.delete()
        i.prise_en_charge_hebergement = True
        i.prise_en_charge_transport = True
        p = transfert_inscription.transfere(i, True, True, True)
        self.assertTrue(p.transport_organise_par_auf)
        self.assertTrue(p.prise_en_charge_transport)
        self.assertTrue(p.prise_en_charge_sejour)
        self.assertTrue(p.reservation_hotel_par_auf)
        assert forfait_chambre_double in p.forfaits.all()


class TableauDeBordTestCase(TestCase):
    fixtures = ['test_data.json']

    def setUp(self):
        create_fixtures(self)
        self.client.login(username='john', password='johnpassword')
        self.participants = [
            creer_participant(nom=u'Participant' + str(n),
                              prenom=u'prenom' + str(n))
            for n in range(10)
            ]

    def tearDown(self):
        self.client.logout()

    def get_tableau_de_bord(self):
        return self.client.get(reverse('tableau_de_bord'))

    def test_points_de_suivis(self):
        def check_link(resp, point_de_suivi, nombre):
            self.assertContains(resp,
                                u'href="%s?suivi=%s">%s'
                                % (reverse('participants'), point_de_suivi.id,
                                   nombre))

        point_de_suivi_1 = PointDeSuivi.objects.get(code=POINT_DE_SUIVI_1)
        point_de_suivi_2 = PointDeSuivi.objects.get(code=POINT_DE_SUIVI_2)
        response = self.get_tableau_de_bord()
        check_link(response, point_de_suivi_1, 0)
        self.participants[0].suivi.add(point_de_suivi_1)
        response = self.get_tableau_de_bord()
        check_link(response, point_de_suivi_1, 1)
        self.participants[0].suivi.add(point_de_suivi_2)
        response = self.get_tableau_de_bord()
        check_link(response, point_de_suivi_1, 1)
        check_link(response, point_de_suivi_2, 1)
        self.participants[0].suivi.remove(point_de_suivi_1)
        self.participants[0].suivi.remove(point_de_suivi_2)
        response = self.get_tableau_de_bord()
        check_link(response, point_de_suivi_1, 0)
        check_link(response, point_de_suivi_2, 0)


class PermissionsGestionTestCase(TestCase):
    fixtures = ['test_data.json']

    def setUp(self):
        create_fixtures(self)
        self.participant = creer_participant()
        self.user_sans_role = User.objects.create_user(username='sansrole',
                                                       password='abc')
        self.user_lecteur = User.objects.create_user(username='lecteur',
                                                     password='abc')
        self.user_lecteur.roles.add(AGRole(type_role=consts.ROLE_LECTEUR))
        self.user_sai = User.objects.create_user(username='sai',
                                                 password='abc')
        self.user_sai.roles.add(AGRole(type_role=consts.ROLE_SAI))
        self.user_sejour = User.objects.create_user(username='sejour',
                                                    password='abc')
        self.user_sejour.roles.add(AGRole(type_role=consts.ROLE_SEJOUR))
        self.user_comptable = User.objects.create_user(username='comptable',
                                                       password='abc')
        self.user_comptable.roles.add(AGRole(type_role=consts.ROLE_COMPTABLE))
        self.user_admin = User.objects.create_user(username='admin',
                                                   password='abc')
        self.user_admin.roles.add(AGRole(type_role=consts.ROLE_ADMIN))

    def tearDown(self):
        self.client.logout()

    def login(self, user):
        self.client.login(username=user.username, password='abc')

    def test_recherche(self):
        response = self.client.get(reverse('participants'))
        self.assertEqual(response.status_code, 302)
        self.login(self.user_sans_role)
        response = self.client.get(reverse('participants'))
        self.assertEqual(response.status_code, 403)
        self.client.logout()
        self.login(self.user_lecteur)
        response = self.client.get(reverse('participants'))
        self.assertEqual(response.status_code, 200)

    def test_permissions(self):
        modif_link_text = "Modifier</a>"
        response = self.client.get(reverse('fiche_participant',
                                           args=[self.participant.id]))
        self.assertEqual(response.status_code, 302)
        self.login(self.user_lecteur)
        response = self.client.get(reverse('fiche_participant',
                                           args=[self.participant.id]))
        self.assertFalse(modif_link_text in response.content)
        self.client.logout()
        self.login(self.user_sai)
        response = self.client.get(reverse('fiche_participant',
                                           args=[self.participant.id]))
        self.assertEquals(response.content.count(modif_link_text), 6)
        self.assertContains(response, reverse('renseignements_personnels',
                                              args=[self.participant.id]))
        self.assertContains(response, reverse('invites',
                                              args=[self.participant.id]))
        self.client.logout()
        self.login(self.user_sejour)
        response = self.client.get(reverse('fiche_participant',
                                           args=[self.participant.id]))
        self.assertEquals(response.content.count(modif_link_text), 6)
        self.assertContains(response, reverse('sejour',
                                              args=[self.participant.id]))
        self.assertContains(response, reverse('transport',
                                              args=[self.participant.id]))
        self.client.logout()
        self.login(self.user_comptable)
        response = self.client.get(reverse('fiche_participant',
                                           args=[self.participant.id]))
        self.assertEquals(response.content.count(modif_link_text), 5)
        self.assertContains(response, reverse('facturation',
                                              args=[self.participant.id]))
        self.client.logout()
        self.login(self.user_admin)
        response = self.client.get(reverse('fiche_participant',
                                           args=[self.participant.id]))
        self.assertEquals(response.content.count(modif_link_text), 9)

    def try_url(self, url, accepte, refuse):
        for user in accepte:
            self.login(user)
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
            self.client.logout()
        for user in refuse:
            self.login(user)
            response = self.client.get(url)
            self.assertEqual(response.status_code, 403)
            self.client.logout()

    def test_renseignements_personnels(self):
        self.try_url(reverse('renseignements_personnels',
                             args=[self.participant.id]),
                     [self.user_admin, self.user_sai],
                     [self.user_comptable, self.user_lecteur,
                      self.user_sans_role,
                      self.user_sejour])

    def test_facturation(self):
        self.try_url(reverse('facturation',
                             args=[self.participant.id]),
                     [self.user_admin, self.user_comptable],
                     [self.user_sai, self.user_lecteur, self.user_sans_role,
                      self.user_sejour])

    def test_transport(self):
        self.try_url(reverse('transport',
                             args=[self.participant.id]),
                     [self.user_admin, self.user_sejour],
                     [self.user_sai, self.user_lecteur, self.user_sans_role,
                      self.user_comptable])

    def test_sejour(self):
        self.try_url(reverse('sejour',
                             args=[self.participant.id]),
                     [self.user_admin, self.user_sejour],
                     [self.user_sai, self.user_lecteur, self.user_sans_role,
                      self.user_comptable])

    def test_notes_de_frais(self):
        self.try_url(reverse('notes_de_frais',
                             args=[self.participant.id]),
                     [self.user_admin, self.user_sejour, self.user_sai,
                      self.user_comptable],
                     [self.user_lecteur, self.user_sans_role])

    def test_invites(self):
        self.try_url(reverse('invites',
                             args=[self.participant.id]),
                     [self.user_admin, self.user_sai],
                     [self.user_sejour, self.user_lecteur, self.user_sans_role,
                      self.user_comptable])

    def test_suivi(self):
        self.try_url(reverse('suivi',
                             args=[self.participant.id]),
                     [self.user_admin, self.user_sai, self.user_sejour,
                      self.user_comptable],
                     [self.user_lecteur, self.user_sans_role])

    def test_fichiers(self):
        self.try_url(reverse('fichiers',
                             args=[self.participant.id]),
                     [self.user_admin, self.user_sai, self.user_sejour,
                      self.user_comptable],
                     [self.user_lecteur, self.user_sans_role])

    # noinspection PyPep8Naming
    def test_permission_region(self):
        region_MO = Region()
        region_MO.code = u'MO'
        region_MO.nom = u'Moyen-Orient'
        region_MO.save()
        region_EO = Region()
        region_EO.code = u'EO'
        region_EO.nom = u"Europe de l'Ouest"
        region_EO.save()
        pays_eg = Pays.objects.create(
            nom=u"Égypte", code=u"EG", sud=True)

        etablissement_MO = Etablissement(
            nom=u'etab_mo', pays=pays_eg, region=region_MO, statut=u'A',
            qualite=u'ESR', membre=True
        )
        etablissement_MO.save()

        participant_MO = Participant()
        participant_MO.nom = u'Khafagui'
        participant_MO.prenom = u'Nermo'
        participant_MO.etablissement = etablissement_MO
        participant_MO.fonction = get_fonction_repr_universitaire()
        participant_MO.save()

        type_autre = TypeInstitutionFactory()
        fonction_autre = FonctionFactory(type_institution=type_autre)
        institution_MO = InstitutionFactory(type_institution=type_autre,
                                            region=region_MO)

        participant_MO2 = Participant()
        participant_MO2.nom = u'Hussein'
        participant_MO2.prenom = u'Taha'
        participant_MO2.fonction = fonction_autre
        participant_MO2.institution = institution_MO
        participant_MO2.save()

        participant_inst_seulement = Participant()
        participant_inst_seulement.nom = u'Shokry'
        participant_inst_seulement.prenom = u'Yasser'
        participant_inst_seulement.fonction = get_fonction_instance_seulement()
        participant_inst_seulement.save()

        participant_pers_auf_MO = Participant.objects.create(
            nom=u"El-Badry", prenom=u"Selim",
            fonction=get_fonction_personnel_auf(),
            implantation=ImplantationFactory(region=region_MO)
        )

        user_mo = User.objects.create_user(username='mo', password='abc')
        user_mo.roles.add(AGRole(type_role=consts.ROLE_SAI, region=region_MO))
        user_eo = User.objects.create_user(username='eo', password='abc')
        user_eo.roles.add(AGRole(type_role=consts.ROLE_SAI, region=region_EO))

        self.try_url(reverse('renseignements_personnels',
                             args=[self.participant.id]), [],
                     [user_mo, user_eo])
        self.try_url(reverse('renseignements_personnels',
                             args=[participant_MO.id]), [user_mo],
                     [user_eo])
        self.try_url(reverse('renseignements_personnels',
                             args=[participant_MO2.id]), [user_mo],
                     [user_eo])
        self.try_url(reverse('renseignements_personnels',
                             args=[participant_inst_seulement.id]), [],
                     [user_eo, user_mo])
        self.try_url(reverse('renseignements_personnels',
                             args=[participant_pers_auf_MO.id]), [user_mo],
                     [user_eo])

        user_mo_lecteur = User.objects.create_user(username='mol',
                                                   password='abc')
        user_mo_lecteur.roles.add(
            AGRole(type_role=consts.ROLE_LECTEUR, region=region_MO))
        user_eo_lecteur = User.objects.create_user(username='eol',
                                                   password='abc')
        user_eo_lecteur.roles.add(
            AGRole(type_role=consts.ROLE_LECTEUR, region=region_EO))
        self.try_url(reverse('notes_de_frais',
                             args=[self.participant.id]), [],
                     [user_mo_lecteur, user_eo_lecteur])
        self.try_url(reverse('notes_de_frais',
                             args=[participant_inst_seulement.id]), [],
                     [user_mo_lecteur, user_eo_lecteur])
        self.try_url(reverse('notes_de_frais',
                             args=[participant_MO.id]), [user_mo_lecteur],
                     [user_eo_lecteur])
        self.try_url(reverse('notes_de_frais',
                             args=[participant_MO2.id]), [user_mo_lecteur],
                     [user_eo_lecteur])

    def test_tableau_de_bord(self):
        self.try_url(reverse('tableau_de_bord'),
                     [self.user_admin, self.user_sai, self.user_sejour,
                      self.user_comptable, self.user_lecteur],
                     [self.user_sans_role])


class TestsVolsGroupes(TestCase):
    fixtures = ['test_data.json']

    def setUp(self):
        create_fixtures(self)
        self.client.login(username='john', password='johnpassword')

    def tearDown(self):
        self.client.logout()

    def test_ajout(self):
        response = self.client.get(reverse('ajouter_vol_groupe'))
        self.assertEqual(response.status_code, 200)
        data = {
            u'top-nom': u"test vol",
            u'top-nombre_de_sieges': u"123"
        }
        data.update(VOL_TEST_DATA)
        response = self.client.post(reverse('ajouter_vol_groupe'), data=data)
        self.assertRedirects(response, reverse('liste_vols_groupes'))
        self.assertEqual(VolGroupe.objects.count(), 1)
        self.assertEqual(InfosVol.objects.filter(
            type_infos=consts.VOL_GROUPE).count(), 1)
        response = self.client.get(reverse('liste_vols_groupes'))
        self.assertContains(response, u"test vol")
        self.assertContains(response, u"Aucun participant")
        vol_test = VolGroupe.objects.all()[0]
        response = self.client.get(reverse('modifier_vol_groupe',
                                           args=(vol_test.id,)))
        self.assertContains(response, u"test vol")
        participant = creer_participant()
        participant.vol_groupe = vol_test
        participant.transport_organise_par_auf = True
        participant.prise_en_charge_transport = True
        participant.save()
        response = self.client.get(reverse('liste_vols_groupes'))
        self.assertContains(response, participant.get_nom_prenom())
        self.assertContains(response, participant.get_region())
        participant = Participant.actifs.sql_extra_fields(
            'frais_transport').get(id=participant.id)
        self.assertEqual(participant.frais_transport,
                         vol_test.get_prix_total())
        participant.desactive = True
        participant.save()
        response = self.client.get(reverse('liste_vols_groupes'))
        self.assertNotContains(response, participant.get_nom_prenom())

    def test_prix_facultatif(self):
        data = {
            u'top-nom': u"test vol",
            u'top-nombre_de_sieges': u"123"
        }
        data.update(VOL_TEST_DATA)
        del data[u'vols-0-prix']
        response = self.client.post(reverse('ajouter_vol_groupe'), data=data)
        self.assertRedirects(response, reverse('liste_vols_groupes'))


def empty_depart_arrivee():
    empty_depart_arrivee_dict = EMPTY_DEPART
    empty_depart_arrivee_dict.update(EMPTY_ARRIVEE)
    return InfosDepartArrivee(**empty_depart_arrivee_dict)


class InfosDepartArriveeTestCase(unittest.TestCase):
    def info_vol(self):
        return InfosVol(
            ville_depart="Paris",
            date_depart=datetime.date(2017, 5, 1),
            heure_depart=datetime.time(12, 00),
            ville_arrivee=consts.AEROPORTS_AG[0],
            date_arrivee=datetime.date(2017, 5, 2),
            heure_arrivee=datetime.time(12, 00),
            numero_vol="1234",
            compagnie="Air France", )

    def test_empty_depart_arrivee(self):
        self.assertEqual(infos_depart_arrivee_from_infos_vols(None, None),
                         empty_depart_arrivee())

    def test_depart(self):
        iv = self.info_vol()
        ida = infos_depart_arrivee_from_infos_vols(iv, None)
        self.assertEqual((iv.ville_depart, iv.date_depart, iv.heure_depart,
                          iv.numero_vol, iv.compagnie),
                         (ida.depart_de, ida.depart_date,
                          ida.depart_heure, ida.depart_vol,
                          ida.depart_compagnie))

    def test_arrivee(self):
        iv = self.info_vol()
        ida = infos_depart_arrivee_from_infos_vols(None, iv)
        self.assertEqual((iv.ville_arrivee, iv.date_arrivee, iv.heure_arrivee,
                          iv.numero_vol, iv.compagnie),
                         (ida.arrivee_a, ida.arrivee_date,
                          ida.arrivee_heure, ida.arrivee_vol,
                          ida.arrivee_compagnie))


class InfosDepartArriveeParticipantTestCase(TestCase):
    def test_participant_sans_pec_sans_infos_vol(self):
        p = Participant(prise_en_charge_transport=False)
        self.assertEqual(p.get_infos_depart_arrivee(),
                         empty_depart_arrivee())

    def test_participant_sans_pec_avec_infos_vol(self):
        p = test_utils.ParticipantFactory(prise_en_charge_transport=False)
        p.set_infos_arrivee(datetime.date(2017, 5, 1),
                            datetime.time(12, 0),
                            "1234",
                            "Air Canada",
                            consts.AEROPORTS_AG[0])
        p.set_infos_depart(datetime.date(2017, 5, 5),
                           datetime.time(12, 12),
                           "4321",
                           "Air France",
                           consts.AEROPORTS_AG[1])
        self.assertEqual(p.get_infos_depart_arrivee(),
                         infos_depart_arrivee_from_infos_vols(
                             p.get_infos_depart(), p.get_infos_arrivee()))

    def test_participant_avec_pec_sans_vol(self):
        p = test_utils.ParticipantFactory(prise_en_charge_transport=True)
        self.assertEqual(p.get_infos_depart_arrivee(),
                         empty_depart_arrivee())

    def create_infos_vols(self, p, escale_aller='BERLIN',
                          ville_depart_retour=consts.VILLE_AG,
                          escale_retour='PARIS',
                          ville_arrivee_ag=consts.VILLE_AG):
        InfosVol.objects.create(   # vol aller 1
            date_depart=datetime.date(2013, 5, 1),
            heure_depart=datetime.time(15, 10),
            ville_depart='PARIS',
            date_arrivee=datetime.date(2013, 5, 2),
            heure_arrivee=datetime.time(17, 10),
            ville_arrivee=escale_aller,
            compagnie='AIR FRANCE',
            numero_vol='AF615',
            prix=500,
            participant=p,
            type_infos=consts.VOL_ORGANISE,
        )
        infos_vol_aller_2 = InfosVol.objects.create(
            date_depart=datetime.date(2013, 5, 2),
            heure_depart=datetime.time(18, 10),
            ville_depart=escale_aller,
            date_arrivee=datetime.date(2013, 5, 3),
            heure_arrivee=datetime.time(5, 10),
            ville_arrivee=ville_arrivee_ag,
            compagnie='AIR FRANCE',
            numero_vol='AF615',
            prix=500,
            participant=p,
            type_infos=consts.VOL_ORGANISE,
        )
        infos_vol_retour = InfosVol.objects.create(
            date_depart=datetime.date(2013, 5, 4),
            heure_depart=datetime.time(15, 10),
            ville_depart=ville_depart_retour,
            date_arrivee=datetime.date(2013, 5, 4),
            heure_arrivee=datetime.time(17, 10),
            ville_arrivee=escale_retour,
            compagnie='AIR FRANCE',
            numero_vol='AF616',
            prix=600,
            participant=p,
            type_infos=consts.VOL_ORGANISE,
        )
        InfosVol.objects.create(  # vol retour 2
            date_depart=datetime.date(2013, 5, 4),
            heure_depart=datetime.time(18, 10),
            ville_depart=escale_retour,
            date_arrivee=datetime.date(2013, 5, 5),
            heure_arrivee=datetime.time(12, 10),
            ville_arrivee='MONTREAL',
            compagnie='AIR FRANCE',
            numero_vol='AF618',
            prix=600,
            participant=p,
            type_infos=consts.VOL_ORGANISE,
        )
        return infos_vol_aller_2, infos_vol_retour

    def test_participant_avec_pec_avec_vols(self):
        """Dans le cas d'un vol groupé ou organisé par l'auf,
        on vérifie que les infos de départ et d'arrivée sont bien celles
        du dernier segment du vol aller, et du premier segment du vol retour."""

        p = test_utils.ParticipantFactory(transport_organise_par_auf=True)
        # type: Participant
        infos_arrivee, infos_depart = self.create_infos_vols(p)
        self.assertEqual(p.get_infos_depart_arrivee(),
                         infos_depart_arrivee_from_infos_vols(infos_depart,
                                                              infos_arrivee))

    def test_priorite_ville_ag(self):
        """Dans le cas d'un vol groupé ou organisé par l'auf,
        on vérifie que les infos de départ et d'arrivée sont bien celles
        du dernier segment du vol aller, et du premier segment du vol retour,
        dans le cas où le participant fait une escale dans une autre ville 
        d'arrivée (ex: AG à Marrakech, arrivée possible à Casablanca ou
        Marrakech, le participant arrive à Marrakech en faisant une escale
        à Casablanca."""

        p = test_utils.ParticipantFactory(transport_organise_par_auf=True)
        # type: Participant
        infos_arrivee, infos_depart = self.create_infos_vols(
            p, consts.AEROPORTS_AG[1])
        self.assertEqual(p.get_infos_depart_arrivee(),
                         infos_depart_arrivee_from_infos_vols(infos_depart,
                                                              infos_arrivee))

    def test_priorite_ville_ag_ville_retour_differente(self):
        """Dans le cas d'un vol groupé ou organisé par l'auf,
        on vérifie que les infos de départ et d'arrivée sont bien celles
        du dernier segment du vol aller, et du premier segment du vol retour,
        dans le cas où le participant fait une escale dans une autre ville 
        d'arrivée (ex: AG à Marrakech, arrivée possible à Casablanca ou
        Marrakech, le participant arrive à Marrakech en faisant une escale
        à Casablanca."""

        p = test_utils.ParticipantFactory(transport_organise_par_auf=True)
        # type: Participant
        infos_arrivee, infos_depart = self.create_infos_vols(
            p, consts.AEROPORTS_AG[1], consts.AEROPORTS_AG[1])
        self.assertEqual(p.get_infos_depart_arrivee(),
                         infos_depart_arrivee_from_infos_vols(infos_depart,
                                                              infos_arrivee))

    def test_arrivee_ville_different_retour_ville_ag_escale_autre_ville(self):
        """Dans le cas d'un vol groupé ou organisé par l'auf,
        on vérifie que les infos de départ et d'arrivée sont bien celles
        du dernier segment du vol aller, et du premier segment du vol retour,
        dans le cas où le participant fait une escale dans une autre ville 
        au départ (ex: AG à Marrakech, arrivée à Casablanca , le participant 
        repart de Marrakech en faisant une escale à Casablanca."""

        p = test_utils.ParticipantFactory(transport_organise_par_auf=True)
        # type: Participant
        infos_arrivee, infos_depart = self.create_infos_vols(
            p, escale_aller='ATHENES', ville_arrivee_ag=consts.AEROPORTS_AG[1],
            ville_depart_retour=consts.VILLE_AG,
            escale_retour=consts.AEROPORTS_AG[1])
        self.assertEqual(p.get_infos_depart_arrivee(),
                         infos_depart_arrivee_from_infos_vols(infos_depart,
                                                              infos_arrivee))
