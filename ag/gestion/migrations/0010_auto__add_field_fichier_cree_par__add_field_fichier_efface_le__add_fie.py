# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Fichier.cree_par'
        db.add_column('gestion_fichier', 'cree_par',
                      self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', null=True, on_delete=models.PROTECT, to=orm['auth.User']),
                      keep_default=False)

        # Adding field 'Fichier.efface_le'
        db.add_column('gestion_fichier', 'efface_le',
                      self.gf('django.db.models.fields.DateTimeField')(null=True),
                      keep_default=False)

        # Adding field 'Fichier.efface_par'
        db.add_column('gestion_fichier', 'efface_par',
                      self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', null=True, on_delete=models.PROTECT, to=orm['auth.User']),
                      keep_default=False)

    def backwards(self, orm):
        # Deleting field 'Fichier.cree_par'
        db.delete_column('gestion_fichier', 'cree_par_id')

        # Deleting field 'Fichier.efface_le'
        db.delete_column('gestion_fichier', 'efface_le')

        # Deleting field 'Fichier.efface_par'
        db.delete_column('gestion_fichier', 'efface_par_id')

    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '75'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'gestion.activite': {
            'Meta': {'object_name': 'Activite'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '16', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'libelle': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'prix': ('django.db.models.fields.FloatField', [], {}),
            'prix_invite': ('django.db.models.fields.FloatField', [], {})
        },
        'gestion.agrole': {
            'Meta': {'object_name': 'AGRole'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'region': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['references.Region']", 'null': 'True', 'blank': 'True'}),
            'type_role': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'roles'", 'to': "orm['auth.User']"})
        },
        'gestion.chambre': {
            'Meta': {'unique_together': "(('hotel', 'type_chambre'),)", 'object_name': 'Chambre'},
            'hotel': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['gestion.Hotel']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nb_total': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'places': ('django.db.models.fields.IntegerField', [], {}),
            'prix': ('django.db.models.fields.FloatField', [], {}),
            'type_chambre': ('django.db.models.fields.CharField', [], {'max_length': '1'})
        },
        'gestion.fichier': {
            'Meta': {'object_name': 'Fichier'},
            'cree_le': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'cree_par': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'null': 'True', 'on_delete': 'models.PROTECT', 'to': "orm['auth.User']"}),
            'efface_le': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'efface_par': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'null': 'True', 'on_delete': 'models.PROTECT', 'to': "orm['auth.User']"}),
            'fichier': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'participant': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['gestion.Participant']"})
        },
        'gestion.frais': {
            'Meta': {'object_name': 'Frais'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'montant': ('django.db.models.fields.FloatField', [], {}),
            'participant': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['gestion.Participant']"}),
            'quantite': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'type_frais': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['gestion.TypeFrais']"})
        },
        'gestion.hotel': {
            'Meta': {'object_name': 'Hotel'},
            'adresse': ('django.db.models.fields.TextField', [], {}),
            'code': ('django.db.models.fields.CharField', [], {'max_length': '16', 'blank': 'True'}),
            'courriel': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'libelle': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'telephone': ('django.db.models.fields.CharField', [], {'max_length': '32', 'blank': 'True'})
        },
        'gestion.infosvol': {
            'Meta': {'ordering': "['date_depart', 'heure_depart']", 'object_name': 'InfosVol'},
            'compagnie': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            'date_arrivee': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'date_depart': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'heure_arrivee': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'}),
            'heure_depart': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'numero_vol': ('django.db.models.fields.CharField', [], {'max_length': '16', 'blank': 'True'}),
            'participant': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['gestion.Participant']", 'null': 'True'}),
            'prix': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'type_infos': ('django.db.models.fields.IntegerField', [], {'default': '2'}),
            'ville_arrivee': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'ville_depart': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'vol_groupe': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['gestion.VolGroupe']", 'null': 'True'})
        },
        'gestion.invitation': {
            'Meta': {'object_name': 'Invitation', 'db_table': "u'invitations'", 'managed': 'False'},
            'enveloppe_id': ('django.db.models.fields.IntegerField', [], {}),
            'etablissement_id': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'etablissement_nom': ('django.db.models.fields.CharField', [], {'max_length': '765'}),
            'etablissement_region_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'jeton': ('django.db.models.fields.CharField', [], {'max_length': '96'}),
            'modele_id': ('django.db.models.fields.IntegerField', [], {}),
            'nord_sud': ('django.db.models.fields.CharField', [], {'max_length': '765', 'blank': 'True'}),
            'statut': ('django.db.models.fields.CharField', [], {'max_length': '3', 'blank': 'True'})
        },
        'gestion.invite': {
            'Meta': {'object_name': 'Invite'},
            'genre': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nom': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'participant': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['gestion.Participant']"}),
            'prenom': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'gestion.participant': {
            'Meta': {'object_name': 'Participant'},
            'accompte': ('django.db.models.fields.FloatField', [], {'default': '0', 'blank': 'True'}),
            'activites': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['gestion.Activite']", 'through': "orm['gestion.ParticipationActivite']", 'symmetrical': 'False'}),
            'adresse': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'code_postal': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'courriel': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'date_arrivee_hotel': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'date_depart_hotel': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'date_facturation': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'date_naissance': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'desactive': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'etablissement': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['references.Etablissement']", 'null': 'True'}),
            'facturation_supplement_chambre_double': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'facturation_validee': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'genre': ('django.db.models.fields.CharField', [], {'max_length': '1', 'blank': 'True'}),
            'hotel': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['gestion.Hotel']", 'null': 'True', 'on_delete': 'models.PROTECT'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'imputation': ('django.db.models.fields.CharField', [], {'max_length': '32', 'blank': 'True'}),
            'inscription': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['inscription.Inscription']", 'null': 'True'}),
            'instance_auf': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'modalite_retrait_billet': ('django.db.models.fields.CharField', [], {'max_length': '1', 'blank': 'True'}),
            'modalite_versement_frais_sejour': ('django.db.models.fields.CharField', [], {'max_length': '1', 'blank': 'True'}),
            'nationalite': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'nom': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'nom_autre_institution': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True'}),
            'notes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'notes_facturation': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'notes_hebergement': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'notes_statut': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'notes_transport': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'numero_dossier_transport': ('django.db.models.fields.CharField', [], {'max_length': '32', 'blank': 'True'}),
            'numero_facture': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'paiement': ('django.db.models.fields.CharField', [], {'max_length': '2', 'blank': 'True'}),
            'pays': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'poste': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'prenom': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'prise_en_charge_activites': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'prise_en_charge_inscription': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'prise_en_charge_sejour': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'prise_en_charge_transport': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'region': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['references.Region']", 'null': 'True'}),
            'remarques_transport': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'reservation_hotel_par_auf': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'statut': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['gestion.StatutParticipant']", 'on_delete': 'models.PROTECT'}),
            'statut_dossier_transport': ('django.db.models.fields.CharField', [], {'max_length': '1', 'blank': 'True'}),
            'suivi': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['gestion.PointDeSuivi']", 'symmetrical': 'False'}),
            'telecopieur': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'telephone': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'transport_organise_par_auf': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'type_autre_institution': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['gestion.TypeInstitutionSupplementaire']", 'null': 'True', 'on_delete': 'models.PROTECT'}),
            'type_institution': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'utiliser_adresse_gde': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'ville': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'vol_groupe': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['gestion.VolGroupe']", 'null': 'True', 'on_delete': 'models.PROTECT'})
        },
        'gestion.participationactivite': {
            'Meta': {'unique_together': "(('activite', 'participant'),)", 'object_name': 'ParticipationActivite'},
            'activite': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['gestion.Activite']"}),
            'avec_invites': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'participant': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['gestion.Participant']"})
        },
        'gestion.pointdesuivi': {
            'Meta': {'ordering': "['ordre']", 'object_name': 'PointDeSuivi'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '16', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'libelle': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'ordre': ('django.db.models.fields.IntegerField', [], {})
        },
        'gestion.reservationchambre': {
            'Meta': {'unique_together': "(('participant', 'type_chambre'),)", 'object_name': 'ReservationChambre'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nombre': ('django.db.models.fields.IntegerField', [], {}),
            'participant': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['gestion.Participant']"}),
            'type_chambre': ('django.db.models.fields.CharField', [], {'max_length': '1'})
        },
        'gestion.statutparticipant': {
            'Meta': {'ordering': "['ordre']", 'object_name': 'StatutParticipant'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '16', 'blank': 'True'}),
            'droit_de_vote': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'libelle': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'ordre': ('django.db.models.fields.IntegerField', [], {})
        },
        'gestion.typefrais': {
            'Meta': {'ordering': "['libelle']", 'object_name': 'TypeFrais'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '16', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'libelle': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        },
        'gestion.typeinstitutionsupplementaire': {
            'Meta': {'ordering': "['ordre']", 'object_name': 'TypeInstitutionSupplementaire'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '16', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'libelle': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'ordre': ('django.db.models.fields.IntegerField', [], {})
        },
        'gestion.volgroupe': {
            'Meta': {'ordering': "['nom']", 'object_name': 'VolGroupe'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nom': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'nombre_de_sieges': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        'inscription.inscription': {
            'Meta': {'object_name': 'Inscription'},
            'accompagnateur': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'accompagnateur_genre': ('django.db.models.fields.CharField', [], {'max_length': '1', 'blank': 'True'}),
            'accompagnateur_nom': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'accompagnateur_prenom': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'adresse': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'arrivee_compagnie': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'arrivee_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'arrivee_heure': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'}),
            'arrivee_vol': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'code_postal': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'conditions_acceptees': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'courriel': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'date_arrivee_hotel': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'date_depart_hotel': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'date_fermeture': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'date_naissance': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'depart_compagnie': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'depart_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'depart_de': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'}),
            'depart_heure': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'}),
            'depart_vol': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'fermee': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'genre': ('django.db.models.fields.CharField', [], {'max_length': '1', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'identite_confirmee': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'invitation': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['inscription.Invitation']", 'unique': 'True'}),
            'nationalite': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'nom': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'paiement': ('django.db.models.fields.CharField', [], {'max_length': '2', 'blank': 'True'}),
            'pays': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'poste': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'prenom': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'prise_en_charge_hebergement': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'prise_en_charge_transport': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'programmation_gala': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'programmation_gala_invite': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'programmation_soiree_interconsulaire': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'programmation_soiree_interconsulaire_invite': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'programmation_soiree_unesp': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'programmation_soiree_unesp_invite': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'telecopieur': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'telephone': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'ville': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'})
        },
        'inscription.invitation': {
            'Meta': {'object_name': 'Invitation'},
            'courriel': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True'}),
            'etablissement': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['references.Etablissement']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'jeton': ('django.db.models.fields.CharField', [], {'default': "'pbkJvYo0PNfC9ROlVU1Ho8dULBR3Ji9W'", 'max_length': '32'}),
            'pour_mandate': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'references.bureau': {
            'Meta': {'ordering': "['nom']", 'object_name': 'Bureau', 'db_table': "u'ref_bureau'", 'managed': 'False'},
            'actif': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'implantation': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['references.Implantation']", 'db_column': "'implantation'"}),
            'nom': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'nom_court': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'nom_long': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'region': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['references.Region']", 'db_column': "'region'"})
        },
        'references.etablissement': {
            'Meta': {'ordering': "['pays__nom', 'nom']", 'object_name': 'Etablissement', 'db_table': "u'ref_etablissement'", 'managed': 'False'},
            'actif': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'adresse': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'cedex': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'code_postal': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'commentaire': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'date_modification': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'fax': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'historique': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'implantation': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'db_column': "'implantation'", 'to': "orm['references.Implantation']"}),
            'membre': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'membre_adhesion_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'nom': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'nombre_chercheurs': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'nombre_enseignants': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'nombre_etudiants': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'nombre_membres': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'pays': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to_field': "'code'", 'db_column': "'pays'", 'to': "orm['references.Pays']"}),
            'province': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'qualite': ('django.db.models.fields.CharField', [], {'max_length': '3', 'null': 'True', 'blank': 'True'}),
            'region': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'db_column': "'region'", 'to': "orm['references.Region']"}),
            'responsable_courriel': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'responsable_fonction': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'responsable_genre': ('django.db.models.fields.CharField', [], {'max_length': '1', 'blank': 'True'}),
            'responsable_nom': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'responsable_prenom': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'sigle': ('django.db.models.fields.CharField', [], {'max_length': '16', 'blank': 'True'}),
            'statut': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True', 'blank': 'True'}),
            'telephone': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '255', 'blank': 'True'}),
            'ville': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'})
        },
        'references.implantation': {
            'Meta': {'ordering': "['nom']", 'object_name': 'Implantation', 'db_table': "u'ref_implantation'", 'managed': 'False'},
            'actif': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'adresse_physique_bureau': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'adresse_physique_code_postal': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'adresse_physique_code_postal_avant_ville': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'adresse_physique_no': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'adresse_physique_pays': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'impl_adresse_physique'", 'to_field': "'code'", 'db_column': "'adresse_physique_pays'", 'to': "orm['references.Pays']"}),
            'adresse_physique_precision': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'adresse_physique_precision_avant': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'adresse_physique_region': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'adresse_physique_rue': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'adresse_physique_ville': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'adresse_postale_boite_postale': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'adresse_postale_bureau': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'adresse_postale_code_postal': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'adresse_postale_code_postal_avant_ville': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'adresse_postale_no': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'adresse_postale_pays': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'impl_adresse_postale'", 'to_field': "'code'", 'db_column': "'adresse_postale_pays'", 'to': "orm['references.Pays']"}),
            'adresse_postale_precision': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'adresse_postale_precision_avant': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'adresse_postale_region': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'adresse_postale_rue': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'adresse_postale_ville': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'bureau_rattachement': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['references.Implantation']", 'db_column': "'bureau_rattachement'"}),
            'code_meteo': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'commentaire': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'courriel': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'courriel_interne': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'date_extension': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'date_fermeture': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'date_inauguration': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'date_ouverture': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'fax': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'fax_interne': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'fuseau_horaire': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'hebergement_convention': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'hebergement_convention_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'hebergement_etablissement': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modif_date': ('django.db.models.fields.DateField', [], {}),
            'nom': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'nom_court': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'nom_long': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'region': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['references.Region']", 'db_column': "'region'"}),
            'remarque': ('django.db.models.fields.TextField', [], {}),
            'responsable_implantation': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'statut': ('django.db.models.fields.IntegerField', [], {}),
            'telephone': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'telephone_interne': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '255', 'blank': 'True'}),
            'zone_administrative': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['references.ZoneAdministrative']"})
        },
        'references.pays': {
            'Meta': {'ordering': "['nom']", 'object_name': 'Pays', 'db_table': "u'ref_pays'", 'managed': 'False'},
            'actif': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '2'}),
            'code_bureau': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['references.Bureau']", 'to_field': "'code'", 'null': 'True', 'db_column': "'code_bureau'", 'blank': 'True'}),
            'code_iso3': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '3'}),
            'developpement': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'monnaie': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'nom': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'nord_sud': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'region': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['references.Region']", 'db_column': "'region'"})
        },
        'references.region': {
            'Meta': {'ordering': "['nom']", 'object_name': 'Region', 'db_table': "u'ref_region'", 'managed': 'False'},
            'actif': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'implantation_bureau': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'gere_region'", 'null': 'True', 'db_column': "'implantation_bureau'", 'to': "orm['references.Implantation']"}),
            'nom': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'})
        },
        'references.zoneadministrative': {
            'Meta': {'ordering': "['nom']", 'object_name': 'ZoneAdministrative', 'db_table': "'ref_zoneadministrative'", 'managed': 'False'},
            'actif': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'code': ('django.db.models.fields.CharField', [], {'max_length': '4', 'primary_key': 'True'}),
            'nom': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['gestion']