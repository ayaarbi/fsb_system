import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fsb_system.settings')
django.setup()

from administration.models import Departement, Filiere, Enseignant, Etudiant

print("=== Nettoyage des departements en double ===")

# ── Fusionner sciences_vie → biologie ──
try:
    old = Departement.objects.get(nom='sciences_vie')
    new, _ = Departement.objects.get_or_create(
        nom='biologie',
        defaults=dict(chef=old.chef, email=old.email, telephone=old.telephone)
    )
    # Migrer les filières
    Filiere.objects.filter(departement=old).update(departement=new)
    Enseignant.objects.filter(departement=old).update(departement=new)
    old.delete()
    print(f"[OK] sciences_vie fusionne dans biologie")
except Departement.DoesNotExist:
    print("[--] sciences_vie introuvable (deja corrige)")

# ── Fusionner sciences_terre → geologie ──
try:
    old = Departement.objects.get(nom='sciences_terre')
    new, _ = Departement.objects.get_or_create(
        nom='geologie',
        defaults=dict(chef=old.chef, email=old.email, telephone=old.telephone)
    )
    Filiere.objects.filter(departement=old).update(departement=new)
    Enseignant.objects.filter(departement=old).update(departement=new)
    old.delete()
    print(f"[OK] sciences_terre fusionne dans geologie")
except Departement.DoesNotExist:
    print("[--] sciences_terre introuvable (deja corrige)")

# ── Vérification finale ──
print("\nDepartements restants :")
for d in Departement.objects.all():
    nb_f = d.filieres.count()
    nb_e = Enseignant.objects.filter(departement=d).count()
    print(f"  {d.get_nom_display()} — {nb_f} filieres, {nb_e} enseignants")

print("\n=== Terminé ===")