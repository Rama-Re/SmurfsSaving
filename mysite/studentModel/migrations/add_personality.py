from django.db import migrations, models
import django.db.models.deletion
import csv


def load_data(apps, schema_editor):
    Personality = apps.get_model('studentModel', 'Personality')
    personalitiesNames = ['Extravert', 'Intuitive', 'Feeler', 'Perceiver', 'Introvert', 'Sensor', 'Thinker',
                          'Judger']

    i = 0
    for p in personalitiesNames:
        try:
            Personality.objects.get_or_create(name=p)
            print(f"personalityName {p} loaded!")

        except:
            print("personalityName wasn't loaded")


class Migration(migrations.Migration):
    dependencies = [
        ('studentModel', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(load_data),
    ]
