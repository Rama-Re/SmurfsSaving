
from django.db import migrations, models
import django.db.models.deletion
import csv
from ..views import subConceptsInCode

def load_data(apps, schema_editor):
    GeneralConcept = apps.get_model('domainModel', 'GeneralConcept')
    SubConcept = apps.get_model('domainModel', 'SubConcept')
    TheoreticalData = apps.get_model('domainModel', 'TheoreticalData')
    Keyword = apps.get_model('domainModel', 'Keyword')
    Operator = apps.get_model('domainModel', 'Operator')
    Project = apps.get_model('domainModel', 'Project')
    with open('harmash_data.csv', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader)  # skip header row
        i = 0
        for row in reader:
            i += 1
            # Create or get the GeneralConcept object
            generalconcept, created = GeneralConcept.objects.get_or_create(name=row[0])
            # Create the SubConcept object with foreign key to GeneralConcept
            subconcept, created = SubConcept.objects.get_or_create(name=row[1], generalConcept=generalconcept)
            # Create the TheoreticalData object with foreign key to SubConcept
            theoreticaldata = TheoreticalData.objects.create(title=subconcept, subheading=row[2],
                                                             explanation=row[3], code=row[4], output=row[5],
                                                             codeExplanation=row[6])
            print(f"data {i} loaded!")

    with open('keywords.csv', encoding='utf-8') as f:
        reader = csv.reader(f)
        i = 0
        for row in reader:
            i += 1
            subconcept = SubConcept.objects.get(name=row[1])
            keyword, created = Keyword.objects.get_or_create(name=row[2])
            keyword.subConcepts.add(subconcept)
            print(f"keyword {i} loaded!")

    with open('operators.csv', encoding='utf-8') as f:
        reader = csv.reader(f)
        i = 0
        for row in reader:
            i += 1
            subconcept = SubConcept.objects.get(name=row[1])
            operator, created = Operator.objects.get_or_create(name=row[2])
            operator.subConcepts.add(subconcept)
            print(f"operator {i} loaded!")

    with open('ex_dataset.csv', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader)  # skip header row
        i = 0
        for row in reader:
            i += 1
            subconcepts = subConceptsInCode(row[3])
            project, created = Project.objects.get_or_create(question=row[1], correctAnswerSample=row[3], img_src=row[2],
                                                             output=row[4], explanation=row[5], hint=row[6],
                                                             difficulty=row[7])
            for subconcept in subconcepts:
                project.subConcepts.add(subconcept.name)

            print(f"ex {i} loaded!")

class Migration(migrations.Migration):

    dependencies = [
        ('domainModel', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(load_data),
    ]
