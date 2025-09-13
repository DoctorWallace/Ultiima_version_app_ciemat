from django.db import migrations


def normalize_groups(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    variants = {
        'Técnicos S-LAB': 'Técnicos S-LAB',
        'T\uFFFDcnicos S-LAB': 'Técnicos S-LAB',
        'TÃ©cnicos S-LAB': 'Técnicos S-LAB',
        'Tecnicos S-LAB': 'Técnicos S-LAB',

        'Técnicos responsables S-MEC': 'Técnicos responsables S-MEC',
        'T\uFFFDcnicos responsables S-MEC': 'Técnicos responsables S-MEC',
        'TÃ©cnicos responsables S-MEC': 'Técnicos responsables S-MEC',
        'Tecnicos responsables S-MEC': 'Técnicos responsables S-MEC',

        'Técnicos S-MEC': 'Técnicos S-MEC',
        'T\uFFFDcnicos S-MEC': 'Técnicos S-MEC',
        'TÃ©cnicos S-MEC': 'Técnicos S-MEC',
        'Tecnicos S-MEC': 'Técnicos S-MEC',
    }
    # Build reverse lookup to avoid KeyError
    target_names = set(variants.values())
    for g in Group.objects.all():
        new_name = variants.get(g.name)
        if new_name and g.name != new_name:
            if not Group.objects.filter(name=new_name).exists():
                g.name = new_name
                g.save(update_fields=['name'])


class Migration(migrations.Migration):
    dependencies = [
        ('sigmalab', '0003_solicitud_autonomo_diarioentrada'),
        ('auth', '__latest__'),
    ]

    operations = [
        migrations.RunPython(normalize_groups, migrations.RunPython.noop),
    ]

