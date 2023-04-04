from django.db import migrations, models
import django.db.models.deletion
import csv
from domainModel.views import conceptsInCode


def load_data(apps, schema_editor):

    Project = apps.get_model('domainModel', 'Project')

    with open('ex_dataset.csv', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader)  # skip header row
        i = 0
        for row in reader:
            i += 1
            concepts = conceptsInCode(row[3])
            project, created = Project.objects.get_or_create(question=row[1], correctAnswerSample=row[3],
                                                             img_src=row[2],
                                                             output=row[4], explanation=row[5], hint=row[6],
                                                             difficulty=row[7])
            for concept in concepts:
                project.generalConcepts.add(concept.name)

            print(f"ex {i} loaded!")





class Migration(migrations.Migration):
    dependencies = [
        ('domainModel', 'add_operators'),
    ]

    operations = [
        migrations.RunPython(load_data),
    ]
