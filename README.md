Pour démarrer le serveur, tapper
```
python manage.py runserver
```
Vous pouvez utiliser les identifiants 'admin' et 'admin' comme identifiants d’utilisateur et mot de passe lors de l’authentification. 
Normalement la base est enregistrée dans le fichier fsb_database.db, on a utilisé SQLite mais je crois que l'utilisation d'un SGBD comme Postgres sera meilleure.
Pour les agents IA, ils sont actifs maintenant. Ils peuvent vous répondre mais il n'affecte aucune action
Il faut que vous insériez vos clés d'api dans le fichier `fsb_system/settings.py`. Vous les trouvez en bas du fichier. 
