from django.db import migrations, models
import django.db.models.deletion
import csv


def load_data(apps, schema_editor):
    PersonalitiesNames = apps.get_model('studentModel', 'PersonalitiesNames')
    personalitiesNames = ['architect', 'logician', 'commander', 'debater', 'advocate', 'mediator', 'protagonist',
                          'campaigner', 'logistician', 'defender', 'executive', 'consul', 'virtuoso', 'adventurer',
                          'entrepreneur', 'entertainer']

    i = 0
    for p in personalitiesNames:
        try:
            personalityName = PersonalitiesNames.objects.create(personalityName=p)
            print(f"personalityName {p} loaded!")

        except:
            print("personalityName wasn't loaded")


class Migration(migrations.Migration):
    dependencies = [
        ('studentModel', '0002_initial'),
    ]

    operations = [
        migrations.RunPython(load_data),
    ]
