# Generated by Django 4.2.2 on 2023-08-02 17:43

import datetime
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('studentModel', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='GamificationFeature',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('feature_name', models.TextField(default='')),
                ('threshold', models.DecimalField(decimal_places=2, default=0, max_digits=3)),
            ],
        ),
        migrations.CreateModel(
            name='MbtiQuestions',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question_text', models.CharField(max_length=512)),
            ],
        ),
        migrations.CreateModel(
            name='ToReview',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.TextField(default='')),
                ('shared_date', models.DateTimeField(default=datetime.datetime(2023, 8, 2, 17, 43, 32, 662123))),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='studentModel.studentprofile')),
                ('shared_project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='studentModel.studentproject')),
            ],
        ),
        migrations.CreateModel(
            name='Reviewed',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('edited_code', models.TextField(default='')),
                ('reviewed_date', models.DateTimeField(default=datetime.datetime(2023, 8, 2, 17, 43, 32, 662123))),
                ('review', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gamificationModel.toreview')),
                ('reviewer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='studentModel.studentprofile')),
            ],
        ),
        migrations.CreateModel(
            name='MbtiAnswers',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('answer', models.CharField(max_length=512)),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gamificationModel.mbtiquestions')),
            ],
        ),
        migrations.CreateModel(
            name='FeaturePersonalityRelationship',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rr', models.DecimalField(decimal_places=2, default=0, max_digits=3)),
                ('gamificationFeature', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gamificationModel.gamificationfeature')),
                ('personality', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='studentModel.personality')),
            ],
        ),
        migrations.CreateModel(
            name='Challenge',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('challenge_type', models.CharField(choices=[('Th', 'Theoretical'), ('XP', 'XP'), ('P', 'Projects')], max_length=12)),
                ('challenge_target', models.CharField(default='', max_length=255)),
                ('challenge_state', models.BooleanField(default=False)),
                ('challenge_date', models.DateField(default=django.utils.timezone.now)),
                ('challenger', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='studentModel.studentprofile')),
            ],
        ),
    ]
