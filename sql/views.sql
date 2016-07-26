DROP VIEW IF EXISTS invitations;

CREATE ALGORITHM=UNDEFINED SQL SECURITY DEFINER VIEW `invitations` AS select `e`.`nom` AS `etablissement_nom`,`e`.`id` AS `etablissement_id`,`e`.`region` AS `etablissement_region_id`,`i`.`jeton` AS `jeton`,`env`.`id` AS `enveloppe_id`,`env`.`modele_id` AS `modele_id`,`p`.`nord_sud` AS `nord_sud`,`e`.`statut` AS `statut` from ((((`ag_test`.`mailing_enveloppe` `env` join `ag_test`.`inscription_invitationenveloppe` `ie` on((`env`.`id` = `ie`.`enveloppe_id`))) join `ag_test`.`inscription_invitation` `i` on((`i`.`id` = `ie`.`invitation_id`))) join `ag_test`.`ref_etablissement` `e` on((`e`.`id` = `i`.`etablissement_id`))) join `ag_test`.`ref_pays` `p` on((`p`.`code` = `e`.`pays`)))
