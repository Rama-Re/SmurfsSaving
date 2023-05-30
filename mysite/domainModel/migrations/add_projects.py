from django.db import migrations, models
import django.db.models.deletion
import csv
import ast
from math import ceil


def load_data(apps, schema_editor):

    Project = apps.get_model('domainModel', 'Project')
    ProjectDifficulty = apps.get_model('domainModel', 'ProjectDifficulty')
    ProjectTime = apps.get_model('domainModel', 'ProjectTime')
    ProjectHint = apps.get_model('domainModel', 'ProjectHint')

    with open('ex_dataset.csv', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader)  # skip header row
        i = 0
        for row in reader:
            i += 1
            concepts = ast.literal_eval(row[8])
            mapped_required_time = row[10]
            emptying = row[11]
            concept_emptying2 = ast.literal_eval(row[12])
            project, created = Project.objects.get_or_create(question=row[2], correctAnswerSample=row[4],
                                                             img_src=row[3],
                                                             output=row[5], explanation=row[6], hint=row[7])
            projectDifficulty = ProjectDifficulty.objects.create(project=project, difficulty=row[9])
            projectTime = ProjectTime.objects.create(project=project, time=mapped_required_time)
            projectHint = ProjectHint.objects.create(project=project, required_concept_hint=str({key: round(value, 4) for key, value in zip(concepts, concept_emptying2)}))

            for concept in concepts:
                project.generalConcepts.add(concept)

            print(f"ex {i} loaded!")


class Migration(migrations.Migration):
    dependencies = [
        ('domainModel', 'add_operators'),
    ]

    operations = [
        migrations.RunPython(load_data),
    ]
