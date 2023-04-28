/*
Nettoyage d'une base de données collecte-pro pour utilisation par une instance de démo
Ce script est créé pour la version 2.2.4 de collecte-pro
*/

/*************************************
NETTOYAGE DE DJANGO
**************************************/
DELETE FROM "ecollecte-demo".public.django_admin_log;
DELETE FROM "ecollecte-demo".public.django_session;


/*************************************
NETTOYAGE DE CELERY
**************************************/
DELETE FROM "ecollecte-demo".public.django_celery_beat_clockedschedule;
DELETE FROM "ecollecte-demo".public.django_celery_beat_crontabschedule;
DELETE FROM "ecollecte-demo".public.django_celery_beat_intervalschedule;
DELETE FROM "ecollecte-demo".public.django_celery_beat_solarschedule;
DELETE FROM "ecollecte-demo".public.django_celery_beat_periodictasks;
DELETE FROM "ecollecte-demo".public.django_celery_beat_periodictask;



/*************************************
NETTOYAGE DE LA FAQ
**************************************/
DELETE FROM "ecollecte-demo".public.faq_faqitem;

-- Gestion des Questions
INSERT INTO "ecollecte-demo".public.faq_faqitem VALUES (1, 1, 'Comment accéder aux modes d''emploi ?', 'question1_default', 'Il existe deux tutoriels pour les utilisateurs de collecte-pro :

- Mode d''emploi pour les demandeurs à télécharger ici

- Mode d''emploi pour les répondants à télécharger ici', null, false);
INSERT INTO "ecollecte-demo".public.faq_faqitem VALUES (2, 2, 'Je ne connais pas mon mot de passe pour me connecter, comment faire ?', 'question2_default', 'Si votre administration vous a créé un compte utilisateur ou bien si vous avez reçu un courriel vous invitant à vous connecter, cliquez sur "se connecter" puis "mot de passe oublié". Vous renseignerez alors votre adresse électronique et recevrez un lien pour initialiser votre mot de passe (pensez à vérifier votre dossier de courriels indésirables).

Si vous avez oublié votre mot de passe, la procédure est la même.

Votre mot de passe doit être composé de 15 caractères minimum et comprendre au moins une majuscule, une minuscule, un chiffre et un caractère spécial.', null, false);
INSERT INTO "ecollecte-demo".public.faq_faqitem VALUES (3, 3, 'En tant que répondant, je n''ai pas de réponse à une question. Que faut-il faire ?', 'question3_default', 'Il se peut que vous n''ayez pas d''éléments de réponse ni de pièces justificatives à apporter à une question. Dans ce cas, nous vous recommandons :

    De créer un document, par exemple un fichier Word, où vous expliquerez brièvement que vous n''avez pas d''élément de réponse.
    Ensuite, vous pourrez déposer ce fichier Word ou une version PDF sous la question concernée.


Cette information est importante pour les équipes d''instruction. Elle évitera les malentendus et le risque que la même question vous soit reposée dans un prochain questionnaire.', null, false);
INSERT INTO "ecollecte-demo".public.faq_faqitem VALUES (4, 4, 'En tant que répondant, est-il possible de déposer plusieurs documents à la fois ?', 'question4_default', 'Oui. Collecte-pro permet de déposer plusieurs fichiers à la fois : textes (word ou openoffice), tableaux (xls, xlsx, calc ...), des documents de type pdf, des bases de données et des fichiers compressés ou zippés.', null, false);
INSERT INTO "ecollecte-demo".public.faq_faqitem VALUES (5, 5, 'En tant que répondant, est-il possible de déposer des dossiers ?', 'question5_default', 'Non. Il n''est pas possible de déposer un ou plusieurs dossiers.

En revanche, vous pouvez déposer un fichier compressé ou zippé.

Pour compresser ou zipper un dossier, nous vous conseillons d''utiliser la solution 7-Zip : logiciel gratuit et libre d''archivage à très haut taux de compression', null, false);
INSERT INTO "ecollecte-demo".public.faq_faqitem VALUES (6, 6, 'En tant que répondant, est-il possible de remplacer un document déposé par erreur ?', 'question6_default', 'Oui. Il est possible de remplacer un document déposé sur collecte-pro. En cas d’erreur, vous pouvez mettre le document à la corbeille. En revanche, celui-ci n’est pas définitivement supprimé. La corbeille reste consultable par l’équipe d’instruction.', null, false);
INSERT INTO "ecollecte-demo".public.faq_faqitem VALUES (7, 7, 'En tant que répondant, est-il possible de déposer un fichier très volumineux ?', 'question7_default', 'Oui, mais dans la limite d''une taille maximale de 256 Mo.

Si votre fichier est d''un volume supérieur vous pouvez :

    le compresser ou le zipper
    le diviser en plusieurs fichiers
    contacter l''équipe d''instruction pour trouver un autre canal de partage de document pour ce cas précis.

Pour compresser ou zipper votre fichier, nous vous conseillons d''utiliser 7-Zip : logiciel gratuit et libre d''archivage à très haut taux de compression', null, false);
INSERT INTO "ecollecte-demo".public.faq_faqitem VALUES (8, 8, 'En tant que demandeur, est-il possible de modifier la numérotation de mes questions ?', 'question8_default', 'Il n''est pas possible de modifier la numérotation de vos questions. Elle est générée automatiquement par collecte-pro lorsque vous créez votre questionnaire.', null, false);
INSERT INTO "ecollecte-demo".public.faq_faqitem VALUES (9, 9, 'En tant que demandeur, je souhaiterais créer des sous-parties ou sous-thèmes à mon questionnaire. Cela est-il possible ?', 'question9_default', 'Il n''est pas possible de créer des sous-thèmes ou des sous-parties dans un questionnaire.

Sur collecte-pro, il existe trois niveaux de granularité :

    Nom du questionnaire
    Thèmes (ou parties) du questionnaire
    Questions de chaque thème.


Les équipes prévoyant la granularité suivante ne peuvent pas le faire sur collecte-pro :

    Nom du questionnaire
    Thèmes (ou parties) du questionnaire
    Sous-thèmes (ou sous-parties) de chaque thème
    Les questions de chaque thème.


Certaines équipes d''instruction ayant prévu initialement un questionnaire comportant des sous-thèmes ont priviligié la création de plusieurs questionnaires. Ainsi le nom de leur questionnaire n°1 correspond au nom de leur thème 1 inital.', null, false);
INSERT INTO "ecollecte-demo".public.faq_faqitem VALUES (10, 10, 'En tant que demandeur, je dois adresser des questionnaires différents à plusieurs organismes. Comment faire ?', 'question10_default', 'collecte-pro vous permet de créer autant d''espaces de dépôt que vous le souhaitez.

Chaque espace de dépôt correspondra à un organisme interrogé différent.

Chaque espace de dépôt est étanche et sécurisé. Concrètement, l''organisme X ne pourra voir que les questions et les réponses de l''espace de dépôt X tandis que l''organisme Y ne pourra voir que les questions et les réponses de l''espace de dépôt Y.

Exemple :

Pour la procédure « FBI », vous pouvez créer un espace de dépôt pour le « FBI » et un second pour le « Secrétaire d''Etat à la défense ». L''équipe d''instruction pourra voir ces deux espaces. En revanche, le FBI et le secrétaire d''Etat à la défense ne verront que leur propre espace de dépôt.', null, false);
INSERT INTO "ecollecte-demo".public.faq_faqitem VALUES (11, 11, 'En tant que demandeur, je souhaite adresser le même questionnaire à plusieurs organismes interrogés différents. Comment faire ?', 'question11_default', 'Pour vous éviter de ressaisir plusieurs fois le même questionnaire, vous pouvez dupliquer un espace de dépôt en sélectionnant le ou les questionnaires que vous souhaitez adresser à un nouvel organisme. Consultez le mode d''emploi.', null, false);
INSERT INTO "ecollecte-demo".public.faq_faqitem VALUES (12, 12, 'En tant que demandeur, je souhaite exporter les réponses déposées', 'question12_default', 'Il est possible d''exporter les réponses déposées très simplement à partir de l''espace concerné en cliquant sur Exporter (Zip)

L’exportation d’un volume important de documents peut prendre du temps. Un message de téléchargement durant l''exécution de l''export s''affiche. Lorsque le processus sera terminé, votre navigateur vous avertira de la fin du téléchargement ou bien vous affichera un message vous demandant de préciser le répertoire où les fichiers doivent être stockés.', null, false);
INSERT INTO "ecollecte-demo".public.faq_faqitem VALUES (13, 13, 'En tant que répondant et demandeur, je souhaite proposer une amélioration de la solution collecte-pro', 'question13_default', 'Vous avez une idée pour améliorer collecte-pro, vous pensez qu''une option manque ou bien vous souhaitez nous donner votre avis : contactez-nous directement ou sur GitHub.

Un de nos buts est de toujours augmenter l''efficacité de cette solution pour nos utilisateurs. Toutes les propositions d''amélioration sont les bienvenues. Elles sont étudiées au regard de leur impact direct pour les utilisateurs demandeurs, comme répondants : gain de temps, réduction des délais d''instruction, facilité de compréhension...', null, false);



/*************************************
NETTOYAGE DES PARAMETRES
**************************************/
DELETE FROM "ecollecte-demo".public.parametres_parametre;

-- Gestion des Paramètres
INSERT INTO "ecollecte-demo".public.parametres_parametre VALUES (1, 0, null, 'SUPPORT_EMAIL', 'support@example.org', 'support@example.org', 'support@example.org', false);


/*************************************
NETTOYAGE DES CGU
**************************************/
DELETE FROM "ecollecte-demo".public.tos_cguitem;

-- Gestion des CGU
INSERT INTO "ecollecte-demo".public.tos_cguitem VALUES (1, 1, null, 'Condition générales d''utilisation', 'cgu_1', 'Ce site est un site de démonstration.', false);


/*************************************
NETTOYAGE DES ESPACES DE DEPOT
**************************************/
DELETE FROM "ecollecte-demo".public.control_responsefile;
DELETE FROM "ecollecte-demo".public.control_questionfile;
DELETE FROM "ecollecte-demo".public.control_question;
DELETE FROM "ecollecte-demo".public.control_theme;
DELETE FROM "ecollecte-demo".public.control_questionnairefile;
DELETE FROM "ecollecte-demo".public.control_questionnaire;
DELETE FROM "ecollecte-demo".public.control_control;


/*************************************
NETTOYAGE DES UTILISATEURS
**************************************/
DELETE FROM "ecollecte-demo".public.user_profiles_access;
DELETE FROM "ecollecte-demo".public.user_profiles_userprofile;
DELETE FROM "ecollecte-demo".public.user_profiles_useripaddress;

DELETE FROM "ecollecte-demo".public.auth_group_permissions;
DELETE FROM "ecollecte-demo".public.auth_permission;
DELETE FROM "ecollecte-demo".public.auth_user_groups;
DELETE FROM "ecollecte-demo".public.auth_group;
DELETE FROM "ecollecte-demo".public.auth_user;

-- Gestion des groupes
INSERT INTO "ecollecte-demo".public.auth_group VALUES (1, 'admin_metier');

-- Gestion des permissions
INSERT INTO "ecollecte-demo".public.auth_permission VALUES (1, 'Can add follow', 1, 'add_follow');
INSERT INTO "ecollecte-demo".public.auth_permission VALUES (2, 'Can change follow', 1, 'change_follow');
INSERT INTO "ecollecte-demo".public.auth_permission VALUES (3, 'Can delete follow', 1, 'delete_follow');
INSERT INTO "ecollecte-demo".public.auth_permission VALUES (4, 'Can view follow', 1, 'view_follow');
INSERT INTO "ecollecte-demo".public.auth_permission VALUES (5, 'Can add action', 2, 'add_action');
INSERT INTO "ecollecte-demo".public.auth_permission VALUES (6, 'Can change action', 2, 'change_action');
INSERT INTO "ecollecte-demo".public.auth_permission VALUES (7, 'Can delete action', 2, 'delete_action');
INSERT INTO "ecollecte-demo".public.auth_permission VALUES (8, 'Can view action', 2, 'view_action');
INSERT INTO "ecollecte-demo".public.auth_permission VALUES (9, 'Can add log entry', 3, 'add_logentry');
INSERT INTO "ecollecte-demo".public.auth_permission VALUES (10, 'Can change log entry', 3, 'change_logentry');
INSERT INTO "ecollecte-demo".public.auth_permission VALUES (11, 'Can delete log entry', 3, 'delete_logentry');
INSERT INTO "ecollecte-demo".public.auth_permission VALUES (12, 'Can view log entry', 3, 'view_logentry');
INSERT INTO "ecollecte-demo".public.auth_permission VALUES (13, 'Can add Alerte', 4, 'add_alert');
INSERT INTO "ecollecte-demo".public.auth_permission VALUES (14, 'Can change Alerte', 4, 'change_alert');
INSERT INTO "ecollecte-demo".public.auth_permission VALUES (15, 'Can delete Alerte', 4, 'delete_alert');
INSERT INTO "ecollecte-demo".public.auth_permission VALUES (16, 'Can view Alerte', 4, 'view_alert');
INSERT INTO "ecollecte-demo".public.auth_permission VALUES (17, 'Can add permission', 5, 'add_permission');
INSERT INTO "ecollecte-demo".public.auth_permission VALUES (18, 'Can change permission', 5, 'change_permission');
INSERT INTO "ecollecte-demo".public.auth_permission VALUES (19, 'Can delete permission', 5, 'delete_permission');
INSERT INTO "ecollecte-demo".public.auth_permission VALUES (20, 'Can view permission', 5, 'view_permission');
INSERT INTO "ecollecte-demo".public.auth_permission VALUES (21, 'Can add group', 6, 'add_group');
INSERT INTO "ecollecte-demo".public.auth_permission VALUES (22, 'Can change group', 6, 'change_group');
INSERT INTO "ecollecte-demo".public.auth_permission VALUES (23, 'Can delete group', 6, 'delete_group');
INSERT INTO "ecollecte-demo".public.auth_permission VALUES (24, 'Can view group', 6, 'view_group');
INSERT INTO "ecollecte-demo".public.auth_permission VALUES (25, 'Can add user', 7, 'add_user');
INSERT INTO "ecollecte-demo".public.auth_permission VALUES (26, 'Can change user', 7, 'change_user');
INSERT INTO "ecollecte-demo".public.auth_permission VALUES (27, 'Can delete user', 7, 'delete_user');
INSERT INTO "ecollecte-demo".public.auth_permission VALUES (28, 'Can view user', 7, 'view_user');
INSERT INTO "ecollecte-demo".public.auth_permission VALUES (29, 'Can add content type', 8, 'add_contenttype');
INSERT INTO "ecollecte-demo".public.auth_permission VALUES (30, 'Can change content type', 8, 'change_contenttype');
INSERT INTO "ecollecte-demo".public.auth_permission VALUES (31, 'Can delete content type', 8, 'delete_contenttype');
INSERT INTO "ecollecte-demo".public.auth_permission VALUES (32, 'Can view content type', 8, 'view_contenttype');
INSERT INTO "ecollecte-demo".public.auth_permission VALUES (33, 'Can add ProcÃ©dure', 9, 'add_control');
INSERT INTO "ecollecte-demo".public.auth_permission VALUES (34, 'Can change ProcÃ©dure', 9, 'change_control');
INSERT INTO "ecollecte-demo".public.auth_permission VALUES (35, 'Can delete ProcÃ©dure', 9, 'delete_control');
INSERT INTO "ecollecte-demo".public.auth_permission VALUES (36, 'Can view ProcÃ©dure', 9, 'view_control');
INSERT INTO "ecollecte-demo".public.auth_permission VALUES (37, 'Can add Questionnaire', 10, 'add_questionnaire');
INSERT INTO "ecollecte-demo".public.auth_permission VALUES (38, 'Can change Questionnaire', 10, 'change_questionnaire');
INSERT INTO "ecollecte-demo".public.auth_permission VALUES (39, 'Can delete Questionnaire', 10, 'delete_questionnaire');
INSERT INTO "ecollecte-demo".public.auth_permission VALUES (40, 'Can view Questionnaire', 10, 'view_questionnaire');
INSERT INTO "ecollecte-demo".public.auth_permission VALUES (41, 'Can add ThÃ¨me', 11, 'add_theme');
INSERT INTO "ecollecte-demo".public.auth_permission VALUES (42, 'Can change ThÃ¨me', 11, 'change_theme');
INSERT INTO "ecollecte-demo".public.auth_permission VALUES (43, 'Can delete ThÃ¨me', 11, 'delete_theme');
INSERT INTO "ecollecte-demo".public.auth_permission VALUES (44, 'Can view ThÃ¨me', 11, 'view_theme');
INSERT INTO "ecollecte-demo".public.auth_permission VALUES (45, 'Can add Question', 12, 'add_question');
INSERT INTO "ecollecte-demo".public.auth_permission VALUES (46, 'Can change Question', 12, 'change_question');
INSERT INTO "ecollecte-demo".public.auth_permission VALUES (47, 'Can delete Question', 12, 'delete_question');
INSERT INTO "ecollecte-demo".public.auth_permission VALUES (48, 'Can view Question', 12, 'view_question');
INSERT INTO "ecollecte-demo".public.auth_permission VALUES (53, 'Can add RÃ©ponse: Fichier DÃ©posÃ©', 14, 'add_responsefile');
INSERT INTO "ecollecte-demo".public.auth_permission VALUES (54, 'Can change RÃ©ponse: Fichier DÃ©posÃ©', 14, 'change_responsefile');
INSERT INTO "ecollecte-demo".public.auth_permission VALUES (55, 'Can delete RÃ©ponse: Fichier DÃ©posÃ©', 14, 'delete_responsefile');
INSERT INTO "ecollecte-demo".public.auth_permission VALUES (56, 'Can view RÃ©ponse: Fichier DÃ©posÃ©', 14, 'view_responsefile');
INSERT INTO "ecollecte-demo".public.auth_permission VALUES (57, 'Can add solar event', 15, 'add_solarschedule');
INSERT INTO "ecollecte-demo".public.auth_permission VALUES (58, 'Can change solar event', 15, 'change_solarschedule');
INSERT INTO "ecollecte-demo".public.auth_permission VALUES (59, 'Can delete solar event', 15, 'delete_solarschedule');
INSERT INTO "ecollecte-demo".public.auth_permission VALUES (60, 'Can view solar event', 15, 'view_solarschedule');
INSERT INTO "ecollecte-demo".public.auth_permission VALUES (61, 'Can add interval', 16, 'add_intervalschedule');
INSERT INTO "ecollecte-demo".public.auth_permission VALUES (62, 'Can change interval', 16, 'change_intervalschedule');
INSERT INTO "ecollecte-demo".public.auth_permission VALUES (63, 'Can delete interval', 16, 'delete_intervalschedule');
INSERT INTO "ecollecte-demo".public.auth_permission VALUES (64, 'Can view interval', 16, 'view_intervalschedule');
INSERT INTO "ecollecte-demo".public.auth_permission VALUES (65, 'Can add clocked', 17, 'add_clockedschedule');
INSERT INTO "ecollecte-demo".public.auth_permission VALUES (66, 'Can change clocked', 17, 'change_clockedschedule');
INSERT INTO "ecollecte-demo".public.auth_permission VALUES (67, 'Can delete clocked', 17, 'delete_clockedschedule');
INSERT INTO "ecollecte-demo".public.auth_permission VALUES (68, 'Can view clocked', 17, 'view_clockedschedule');
INSERT INTO "ecollecte-demo".public.auth_permission VALUES (69, 'Can add crontab', 18, 'add_crontabschedule');
INSERT INTO "ecollecte-demo".public.auth_permission VALUES (70, 'Can change crontab', 18, 'change_crontabschedule');
INSERT INTO "ecollecte-demo".public.auth_permission VALUES (71, 'Can delete crontab', 18, 'delete_crontabschedule');
INSERT INTO "ecollecte-demo".public.auth_permission VALUES (72, 'Can view crontab', 18, 'view_crontabschedule');
INSERT INTO "ecollecte-demo".public.auth_permission VALUES (73, 'Can add periodic tasks', 19, 'add_periodictasks');
INSERT INTO "ecollecte-demo".public.auth_permission VALUES (74, 'Can change periodic tasks', 19, 'change_periodictasks');
INSERT INTO "ecollecte-demo".public.auth_permission VALUES (75, 'Can delete periodic tasks', 19, 'delete_periodictasks');
INSERT INTO "ecollecte-demo".public.auth_permission VALUES (76, 'Can view periodic tasks', 19, 'view_periodictasks');
INSERT INTO "ecollecte-demo".public.auth_permission VALUES (77, 'Can add periodic task', 20, 'add_periodictask');
INSERT INTO "ecollecte-demo".public.auth_permission VALUES (78, 'Can change periodic task', 20, 'change_periodictask');
INSERT INTO "ecollecte-demo".public.auth_permission VALUES (79, 'Can delete periodic task', 20, 'delete_periodictask');
INSERT INTO "ecollecte-demo".public.auth_permission VALUES (80, 'Can view periodic task', 20, 'view_periodictask');
INSERT INTO "ecollecte-demo".public.auth_permission VALUES (81, 'Can add Item de F.A.Q', 21, 'add_faqitem');
INSERT INTO "ecollecte-demo".public.auth_permission VALUES (82, 'Can change Item de F.A.Q', 21, 'change_faqitem');
INSERT INTO "ecollecte-demo".public.auth_permission VALUES (83, 'Can delete Item de F.A.Q', 21, 'delete_faqitem');
INSERT INTO "ecollecte-demo".public.auth_permission VALUES (84, 'Can view Item de F.A.Q', 21, 'view_faqitem');
INSERT INTO "ecollecte-demo".public.auth_permission VALUES (85, 'Can add ParamÃ¨tre', 22, 'add_parametre');
INSERT INTO "ecollecte-demo".public.auth_permission VALUES (86, 'Can change ParamÃ¨tre', 22, 'change_parametre');
INSERT INTO "ecollecte-demo".public.auth_permission VALUES (87, 'Can delete ParamÃ¨tre', 22, 'delete_parametre');
INSERT INTO "ecollecte-demo".public.auth_permission VALUES (88, 'Can view ParamÃ¨tre', 22, 'view_parametre');
INSERT INTO "ecollecte-demo".public.auth_permission VALUES (89, 'Can add site', 23, 'add_site');
INSERT INTO "ecollecte-demo".public.auth_permission VALUES (90, 'Can change site', 23, 'change_site');
INSERT INTO "ecollecte-demo".public.auth_permission VALUES (91, 'Can delete site', 23, 'delete_site');
INSERT INTO "ecollecte-demo".public.auth_permission VALUES (92, 'Can view site', 23, 'view_site');
INSERT INTO "ecollecte-demo".public.auth_permission VALUES (93, 'Can add Item de C.G.U.', 24, 'add_cguitem');
INSERT INTO "ecollecte-demo".public.auth_permission VALUES (94, 'Can change Item de C.G.U.', 24, 'change_cguitem');
INSERT INTO "ecollecte-demo".public.auth_permission VALUES (95, 'Can delete Item de C.G.U.', 24, 'delete_cguitem');
INSERT INTO "ecollecte-demo".public.auth_permission VALUES (96, 'Can view Item de C.G.U.', 24, 'view_cguitem');
INSERT INTO "ecollecte-demo".public.auth_permission VALUES (97, 'Can add Adresse IP Utilisateur', 25, 'add_useripaddress');
INSERT INTO "ecollecte-demo".public.auth_permission VALUES (98, 'Can change Adresse IP Utilisateur', 25, 'change_useripaddress');
INSERT INTO "ecollecte-demo".public.auth_permission VALUES (99, 'Can delete Adresse IP Utilisateur', 25, 'delete_useripaddress');
INSERT INTO "ecollecte-demo".public.auth_permission VALUES (100, 'Can view Adresse IP Utilisateur', 25, 'view_useripaddress');
INSERT INTO "ecollecte-demo".public.auth_permission VALUES (101, 'Can add Profil Utilisateur', 26, 'add_userprofile');
INSERT INTO "ecollecte-demo".public.auth_permission VALUES (102, 'Can change Profil Utilisateur', 26, 'change_userprofile');
INSERT INTO "ecollecte-demo".public.auth_permission VALUES (103, 'Can delete Profil Utilisateur', 26, 'delete_userprofile');
INSERT INTO "ecollecte-demo".public.auth_permission VALUES (104, 'Can view Profil Utilisateur', 26, 'view_userprofile');
INSERT INTO "ecollecte-demo".public.auth_permission VALUES (105, 'Can add session', 27, 'add_session');
INSERT INTO "ecollecte-demo".public.auth_permission VALUES (106, 'Can change session', 27, 'change_session');
INSERT INTO "ecollecte-demo".public.auth_permission VALUES (107, 'Can delete session', 27, 'delete_session');
INSERT INTO "ecollecte-demo".public.auth_permission VALUES (108, 'Can view session', 27, 'view_session');
INSERT INTO "ecollecte-demo".public.auth_permission VALUES (109, 'Can add Question: Fichier Annexe', 13, 'add_questionfile');
INSERT INTO "ecollecte-demo".public.auth_permission VALUES (110, 'Can change Question: Fichier Annexe', 13, 'change_questionfile');
INSERT INTO "ecollecte-demo".public.auth_permission VALUES (111, 'Can delete Question: Fichier Annexe', 13, 'delete_questionfile');
INSERT INTO "ecollecte-demo".public.auth_permission VALUES (112, 'Can view Question: Fichier Annexe', 13, 'view_questionfile');
INSERT INTO "ecollecte-demo".public.auth_permission VALUES (113, 'Can add AccÃ¨s d''un utilisateur Ã  un contrÃ´le', 28, 'add_access');
INSERT INTO "ecollecte-demo".public.auth_permission VALUES (114, 'Can change AccÃ¨s d''un utilisateur Ã  un contrÃ´le', 28, 'change_access');
INSERT INTO "ecollecte-demo".public.auth_permission VALUES (115, 'Can delete AccÃ¨s d''un utilisateur Ã  un contrÃ´le', 28, 'delete_access');
INSERT INTO "ecollecte-demo".public.auth_permission VALUES (116, 'Can view AccÃ¨s d''un utilisateur Ã  un contrÃ´le', 28, 'view_access');
INSERT INTO "ecollecte-demo".public.auth_permission VALUES (117, 'Can add Questionnaire: Fichier Annexe', 29, 'add_questionnairefile');
INSERT INTO "ecollecte-demo".public.auth_permission VALUES (118, 'Can change Questionnaire: Fichier Annexe', 29, 'change_questionnairefile');
INSERT INTO "ecollecte-demo".public.auth_permission VALUES (119, 'Can delete Questionnaire: Fichier Annexe', 29, 'delete_questionnairefile');
INSERT INTO "ecollecte-demo".public.auth_permission VALUES (120, 'Can view Questionnaire: Fichier Annexe', 29, 'view_questionnairefile');

-- Gestion des permissions des groupes
INSERT INTO "ecollecte-demo".public.auth_group_permissions VALUES (1, 1, 8);
INSERT INTO "ecollecte-demo".public.auth_group_permissions VALUES (2, 1, 69);
INSERT INTO "ecollecte-demo".public.auth_group_permissions VALUES (3, 1, 70);
INSERT INTO "ecollecte-demo".public.auth_group_permissions VALUES (4, 1, 71);
INSERT INTO "ecollecte-demo".public.auth_group_permissions VALUES (5, 1, 72);
INSERT INTO "ecollecte-demo".public.auth_group_permissions VALUES (6, 1, 61);
INSERT INTO "ecollecte-demo".public.auth_group_permissions VALUES (7, 1, 62);
INSERT INTO "ecollecte-demo".public.auth_group_permissions VALUES (8, 1, 63);
INSERT INTO "ecollecte-demo".public.auth_group_permissions VALUES (9, 1, 64);
INSERT INTO "ecollecte-demo".public.auth_group_permissions VALUES (10, 1, 77);
INSERT INTO "ecollecte-demo".public.auth_group_permissions VALUES (11, 1, 78);
INSERT INTO "ecollecte-demo".public.auth_group_permissions VALUES (12, 1, 79);
INSERT INTO "ecollecte-demo".public.auth_group_permissions VALUES (13, 1, 80);
INSERT INTO "ecollecte-demo".public.auth_group_permissions VALUES (14, 1, 73);
INSERT INTO "ecollecte-demo".public.auth_group_permissions VALUES (15, 1, 74);
INSERT INTO "ecollecte-demo".public.auth_group_permissions VALUES (16, 1, 75);
INSERT INTO "ecollecte-demo".public.auth_group_permissions VALUES (17, 1, 76);
INSERT INTO "ecollecte-demo".public.auth_group_permissions VALUES (18, 1, 57);
INSERT INTO "ecollecte-demo".public.auth_group_permissions VALUES (19, 1, 58);
INSERT INTO "ecollecte-demo".public.auth_group_permissions VALUES (20, 1, 59);
INSERT INTO "ecollecte-demo".public.auth_group_permissions VALUES (21, 1, 60);
INSERT INTO "ecollecte-demo".public.auth_group_permissions VALUES (22, 1, 65);
INSERT INTO "ecollecte-demo".public.auth_group_permissions VALUES (23, 1, 66);
INSERT INTO "ecollecte-demo".public.auth_group_permissions VALUES (24, 1, 67);
INSERT INTO "ecollecte-demo".public.auth_group_permissions VALUES (25, 1, 68);
INSERT INTO "ecollecte-demo".public.auth_group_permissions VALUES (26, 1, 93);
INSERT INTO "ecollecte-demo".public.auth_group_permissions VALUES (27, 1, 94);
INSERT INTO "ecollecte-demo".public.auth_group_permissions VALUES (28, 1, 95);
INSERT INTO "ecollecte-demo".public.auth_group_permissions VALUES (29, 1, 96);
INSERT INTO "ecollecte-demo".public.auth_group_permissions VALUES (30, 1, 34);
INSERT INTO "ecollecte-demo".public.auth_group_permissions VALUES (31, 1, 36);
INSERT INTO "ecollecte-demo".public.auth_group_permissions VALUES (32, 1, 81);
INSERT INTO "ecollecte-demo".public.auth_group_permissions VALUES (33, 1, 82);
INSERT INTO "ecollecte-demo".public.auth_group_permissions VALUES (34, 1, 83);
INSERT INTO "ecollecte-demo".public.auth_group_permissions VALUES (35, 1, 84);
INSERT INTO "ecollecte-demo".public.auth_group_permissions VALUES (36, 1, 4);
INSERT INTO "ecollecte-demo".public.auth_group_permissions VALUES (37, 1, 12);
INSERT INTO "ecollecte-demo".public.auth_group_permissions VALUES (38, 1, 85);
INSERT INTO "ecollecte-demo".public.auth_group_permissions VALUES (39, 1, 86);
INSERT INTO "ecollecte-demo".public.auth_group_permissions VALUES (40, 1, 87);
INSERT INTO "ecollecte-demo".public.auth_group_permissions VALUES (41, 1, 88);
INSERT INTO "ecollecte-demo".public.auth_group_permissions VALUES (42, 1, 46);
INSERT INTO "ecollecte-demo".public.auth_group_permissions VALUES (43, 1, 48);
INSERT INTO "ecollecte-demo".public.auth_group_permissions VALUES (48, 1, 38);
INSERT INTO "ecollecte-demo".public.auth_group_permissions VALUES (49, 1, 90);
INSERT INTO "ecollecte-demo".public.auth_group_permissions VALUES (50, 1, 42);
INSERT INTO "ecollecte-demo".public.auth_group_permissions VALUES (51, 1, 44);
INSERT INTO "ecollecte-demo".public.auth_group_permissions VALUES (52, 1, 26);
INSERT INTO "ecollecte-demo".public.auth_group_permissions VALUES (53, 1, 28);
INSERT INTO "ecollecte-demo".public.auth_group_permissions VALUES (54, 1, 100);
INSERT INTO "ecollecte-demo".public.auth_group_permissions VALUES (55, 1, 104);
INSERT INTO "ecollecte-demo".public.auth_group_permissions VALUES (56, 1, 16);
INSERT INTO "ecollecte-demo".public.auth_group_permissions VALUES (57, 1, 13);
INSERT INTO "ecollecte-demo".public.auth_group_permissions VALUES (58, 1, 14);
INSERT INTO "ecollecte-demo".public.auth_group_permissions VALUES (59, 1, 15);
INSERT INTO "ecollecte-demo".public.auth_group_permissions VALUES (60, 1, 113);
INSERT INTO "ecollecte-demo".public.auth_group_permissions VALUES (61, 1, 114);
INSERT INTO "ecollecte-demo".public.auth_group_permissions VALUES (62, 1, 115);
INSERT INTO "ecollecte-demo".public.auth_group_permissions VALUES (63, 1, 116);
INSERT INTO "ecollecte-demo".public.auth_group_permissions VALUES (68, 1, 117);
INSERT INTO "ecollecte-demo".public.auth_group_permissions VALUES (69, 1, 118);
INSERT INTO "ecollecte-demo".public.auth_group_permissions VALUES (70, 1, 119);
INSERT INTO "ecollecte-demo".public.auth_group_permissions VALUES (71, 1, 120);
INSERT INTO "ecollecte-demo".public.auth_group_permissions VALUES (72, 1, 109);
INSERT INTO "ecollecte-demo".public.auth_group_permissions VALUES (73, 1, 110);
INSERT INTO "ecollecte-demo".public.auth_group_permissions VALUES (74, 1, 111);
INSERT INTO "ecollecte-demo".public.auth_group_permissions VALUES (75, 1, 112);



-- Gestion des utilisateurs
-- Mot de passe : collecte-pro
INSERT INTO "ecollecte-demo".public.auth_user VALUES (1, 'pbkdf2_sha256$260000$lSW7qnNeNzOqlW2RTmoHbE$RX/Ve0O1UuvlhrGOsgX9RXVY7XQ4mz/o5PkU3rwotpQ=', null, true, 'super@admin.org', 'super', 'admin', 'super@admin.org', true, true, '2022-01-01');
INSERT INTO "ecollecte-demo".public.auth_user VALUES (2, 'pbkdf2_sha256$260000$lSW7qnNeNzOqlW2RTmoHbE$RX/Ve0O1UuvlhrGOsgX9RXVY7XQ4mz/o5PkU3rwotpQ=', null, false, 'admin@example.org', 'admin', 'admin', 'admin@example.org', true, true, '2022-01-01');
INSERT INTO "ecollecte-demo".public.auth_user VALUES (3, 'pbkdf2_sha256$260000$lSW7qnNeNzOqlW2RTmoHbE$RX/Ve0O1UuvlhrGOsgX9RXVY7XQ4mz/o5PkU3rwotpQ=', null, false, 'demandeur1@example.org', 'demandeur', 'un', 'demandeur1@example.org', false, true, '2022-01-01');
INSERT INTO "ecollecte-demo".public.auth_user VALUES (4, 'pbkdf2_sha256$260000$lSW7qnNeNzOqlW2RTmoHbE$RX/Ve0O1UuvlhrGOsgX9RXVY7XQ4mz/o5PkU3rwotpQ=', null, false, 'repondant1@example.org', 'repondant', 'un', 'repondant1@example.org', false, true, '2022-01-01');
INSERT INTO "ecollecte-demo".public.auth_user VALUES (5, 'pbkdf2_sha256$260000$lSW7qnNeNzOqlW2RTmoHbE$RX/Ve0O1UuvlhrGOsgX9RXVY7XQ4mz/o5PkU3rwotpQ=', null, false, 'demandeur2@example.org', 'demandeur', 'deux', 'demandeur2@example.org', false, true, '2022-01-01');
INSERT INTO "ecollecte-demo".public.auth_user VALUES (6, 'pbkdf2_sha256$260000$lSW7qnNeNzOqlW2RTmoHbE$RX/Ve0O1UuvlhrGOsgX9RXVY7XQ4mz/o5PkU3rwotpQ=', null, false, 'repondant2@example.org', 'repondant', 'deux', 'repondant2@example.org', false, true, '2022-01-01');
INSERT INTO "ecollecte-demo".public.auth_user VALUES (7, 'pbkdf2_sha256$260000$lSW7qnNeNzOqlW2RTmoHbE$RX/Ve0O1UuvlhrGOsgX9RXVY7XQ4mz/o5PkU3rwotpQ=', null, false, 'demandeur3@example.org', 'demandeur', 'trois', 'demandeur3@example.org', false, true, '2022-01-01');
INSERT INTO "ecollecte-demo".public.auth_user VALUES (8, 'pbkdf2_sha256$260000$lSW7qnNeNzOqlW2RTmoHbE$RX/Ve0O1UuvlhrGOsgX9RXVY7XQ4mz/o5PkU3rwotpQ=', null, false, 'repondant3@example.org', 'repondant', 'trois', 'repondant3@example.org', false, true, '2022-01-01');


-- Gestion des groupes des utilisateurs
INSERT INTO "ecollecte-demo".public.auth_user_groups VALUES (1, 2, 1);


-- Gestion des profils des utilisateurs
INSERT INTO "ecollecte-demo".public.user_profiles_userprofile VALUES (1, 'inspector', null, true, true);
INSERT INTO "ecollecte-demo".public.user_profiles_userprofile VALUES (2, 'inspector', null, true, true);
INSERT INTO "ecollecte-demo".public.user_profiles_userprofile VALUES (3, 'inspector', null, true, true);
INSERT INTO "ecollecte-demo".public.user_profiles_userprofile VALUES (4, 'audited', null, true, true);
INSERT INTO "ecollecte-demo".public.user_profiles_userprofile VALUES (5, 'inspector', null, true, true);
INSERT INTO "ecollecte-demo".public.user_profiles_userprofile VALUES (6, 'audited', null, true, true);
INSERT INTO "ecollecte-demo".public.user_profiles_userprofile VALUES (7, 'inspector', null, true, true);
INSERT INTO "ecollecte-demo".public.user_profiles_userprofile VALUES (8, 'audited', null, true, true);



/*************************************
NETTOYAGE DES ACTIONS EFFECTUEES
**************************************/
DELETE FROM "ecollecte-demo".public.actstream_follow;
DELETE FROM "ecollecte-demo".public.actstream_action;

