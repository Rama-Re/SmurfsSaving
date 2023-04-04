from django.db import migrations, models
import django.db.models.deletion
import csv
from domainModel.views import conceptsInCode


def load_data(apps, schema_editor):
    Keyword = apps.get_model('domainModel', 'Keyword')
    GeneralConcept = apps.get_model('domainModel', 'GeneralConcept')

    with open('keywords.csv', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader)  # skip header row
        i = 0
        for row in reader:
            i += 1
            # if i == 1:
            #     concept = row[0][1:]
            # else:
            concept = row[0]
            generalConcept = GeneralConcept.objects.get(name=concept)
            keyword, created = Keyword.objects.get_or_create(name=row[2])
            keyword.generalConcepts.add(generalConcept)
            # print(f"keyword {i} loaded!")


class Migration(migrations.Migration):
    dependencies = [
        ('domainModel', 'add_theoreticaldata'),
    ]

    operations = [
        migrations.RunPython(load_data),
    ]
