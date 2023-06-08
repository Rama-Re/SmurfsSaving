from django.db import migrations, models
import django.db.models.deletion
import csv

from gamificationModel.models import *

featurePersonalityRelationship_dic = {
    "Voice Interaction": {
        "threshold": 0.5,
        "rr": {
            "Extravert": 1,
            "Intuitive": 0.5,
            "Feeler": 0.2,
            "Perceiver": 0.2,
            "Introvert": 0.2,
            "Sensor": 0.2,
            "Thinker": 0.2,
            "Judger": 0.2,
        }
    },
    "Few Projects": {
        "threshold": 0.5,
        "rr": {
            "Extravert": 0.2,
            "Intuitive": 0,
            "Feeler": 0.2,
            "Perceiver": 0.2,
            "Introvert": 0.2,
            "Sensor": 1,
            "Thinker": 0.2,
            "Judger": 0.2,
        }
    },
    "Leaderboard": {
        "threshold": 0.5,
        "rr": {
            "Extravert": 0.2,
            "Intuitive": 0.2,
            "Feeler": 0,
            "Perceiver": 0.2,
            "Introvert": 0.2,
            "Sensor": 0.2,
            "Thinker": 1,
            "Judger": 0.2,
        }
    },
    "Timer": {
        "threshold": 0.5,
        "rr": {
            "Extravert": 0.2,
            "Intuitive": 0.2,
            "Feeler": 0.2,
            "Perceiver": 0,
            "Introvert": 0.2,
            "Sensor": 0.2,
            "Thinker": 0.2,
            "Judger": 1,
        }
    },
    "Peer Review": {
        "threshold": 0.5,
        "rr": {
            "Extravert": 0.2,
            "Intuitive": 0.2,
            "Feeler": 1,
            "Perceiver": 0.2,
            "Introvert": 0.2,
            "Sensor": 0.2,
            "Thinker": 0.5,
            "Judger": 0.2,
        }
    }
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
