from django.db import migrations, models
import django.db.models.deletion
import csv

from gamificationModel.models import *

featurePersonalityRelationship_dic = {
    "Voice Interaction": {
        "threshold": 0.5,
        "rr": {
            "Extravert": 1,
            "Introvert": 0.5,
            "Intuitive": 0.3,
            "Feeler": 0.3,
            "Perceiver": 0.3,
            "Sensor": 0.3,
            "Thinker": 0.3,
            "Judger": 0.3,
        }
    },
    "Few Projects": {
        "threshold": 0.5,
        "rr": {
            "Extravert": 0.05,
            "Intuitive": 0,
            "Feeler": 0.05,
            "Perceiver": 0.5,
            "Introvert": 0.5,
            "Sensor": 1,
            "Thinker": 0.05,
            "Judger": 0.3,
        }
    },
    "Leaderboard": {
        "threshold": 0.5,
        "rr": {
            "Extravert": 0.96,
            "Intuitive": 0.62,
            "Feeler": 0.61,
            "Perceiver": 0.43,
            "Introvert": 0.57,
            "Sensor": 0.53,
            "Thinker": 0.63,
            "Judger": 0.64,
        }
    },
    "Timer": {
        "threshold": 0.5,
        "rr": {
            "Extravert": 0.05,
            "Intuitive": 0.05,
            "Feeler": 0,
            "Perceiver": 0,
            "Introvert": 0.05,
            "Sensor": 0.3,
            "Thinker": 0.3,
            "Judger": 1,
        }
    },
    "Peer Review": {
        "threshold": 0.5,
        "rr": {
            "Extravert": 0.8,
            "Intuitive": 0.5,
            "Feeler": 1,
            "Perceiver": 0.4,
            "Introvert": 0.3,
            "Sensor": 0.05,
            "Thinker": 0.5,
            "Judger": 0.05,
        }
    },
    "Daily Challenges": {
        "threshold": 0.5,
        "rr": {
            "Extravert": 0.5,
            "Intuitive": 0.05,
            "Feeler": 0.3,
            "Perceiver": 0.3,
            "Introvert": 1,
            "Sensor": 0.95,
            "Thinker": 0.6,
            "Judger": 0.5,
        }
    },
}


def load_data(apps, schema_editor):
    GamificationFeature = apps.get_model('gamificationModel', 'GamificationFeature')
    FeaturePersonalityRelationship = apps.get_model('gamificationModel', 'FeaturePersonalityRelationship')

    for feature, values in featurePersonalityRelationship_dic.items():
        gamificationFeature = GamificationFeature.objects.create(feature_name=feature, threshold=values['threshold'])
        for p, rr in values['rr'].items():
            personality = Personality.objects.get(name=p)
            print('*******', personality.name, '*********')
            feature_personality_relationship = FeaturePersonalityRelationship.objects.create(
                personality_id=personality.name,
                rr=rr,
                gamificationFeature=gamificationFeature)


class Migration(migrations.Migration):
    dependencies = [
        ('studentModel', 'add_personality'),
        ('gamificationModel', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(load_data),
    ]
