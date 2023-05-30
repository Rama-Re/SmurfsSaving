from django.db import migrations, models
import django.db.models.deletion
import csv
import re

def load_data(apps, schema_editor):
    GeneralConcept = apps.get_model('domainModel', 'GeneralConcept')
    Operator = apps.get_model('domainModel', 'Operator')

    with open('operators.csv', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader)  # skip header row
        i = 0
        for row in reader:
            i += 1
            generalConcept = GeneralConcept.objects.get(name=row[0])
            operator, created = Operator.objects.get_or_create(name=row[2])
            operator.generalConcepts.add(generalConcept)
            print(f"operator {i} loaded!")

    # concept = GeneralConcept.objects.get(name="العوامل")
    # concept_operators = concept.operators.all()
    #
    # print(re.compile(fr'(?:[{"|".join(re.escape(k.name) for k in concept_operators)}])'))

class Migration(migrations.Migration):
    dependencies = [
        ('domainModel', 'add_keywords'),
    ]

    operations = [
        migrations.RunPython(load_data),
    ]
