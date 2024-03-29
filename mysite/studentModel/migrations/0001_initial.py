# Generated by Django 4.2.2 on 2023-08-02 17:43

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('domainModel', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Personality',
            fields=[
                ('name', models.CharField(max_length=255, primary_key=True, serialize=False, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='StudentProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('xp', models.IntegerField(default=0)),
                ('learning_path', models.CharField(choices=[('up', 'university_path'), ('fp', 'free_path')], default='university_path', max_length=15)),
                ('studentKnowledge', models.ManyToManyField(to='domainModel.subconcept')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='TimePerformance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('performance', models.DecimalField(decimal_places=3, max_digits=6)),
                ('date', models.DateTimeField(default=datetime.datetime(2023, 8, 2, 17, 43, 32, 646502))),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='studentModel.studentprofile')),
            ],
        ),
        migrations.CreateModel(
            name='TheoreticalSkill',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('skill', models.IntegerField(default=0)),
                ('self_rate', models.IntegerField(default=0)),
                ('availability', models.BooleanField(default=False)),
                ('edit_date', models.DateTimeField(null=True)),
                ('generalConcept', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='domainModel.generalconcept')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='studentModel.studentprofile')),
            ],
        ),
        migrations.CreateModel(
            name='StudentProject',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('solve_date', models.DateTimeField(null=True)),
                ('solutionCode', models.TextField(null=True)),
                ('used_concept_difficulty', models.IntegerField(null=True)),
                ('hint_levels', models.CharField(default='', max_length=255)),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='domainModel.project')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='studentModel.studentprofile')),
            ],
        ),
        migrations.CreateModel(
            name='StudentPersonality',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pp', models.DecimalField(decimal_places=2, default=0, max_digits=3)),
                ('edit_date', models.DateTimeField(default=datetime.datetime(2023, 8, 2, 17, 43, 32, 646502))),
                ('personality', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='studentModel.personality')),
                ('studentProfile', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='studentModel.studentprofile')),
            ],
        ),
        migrations.CreateModel(
            name='Streak',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('interactions', models.IntegerField(default=0)),
                ('streak_date', models.DateField(default=django.utils.timezone.now)),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='studentModel.studentprofile')),
            ],
        ),
        migrations.CreateModel(
            name='SolveTrying',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', models.DecimalField(decimal_places=3, max_digits=6)),
                ('student_project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='studentModel.studentproject')),
            ],
        ),
        migrations.CreateModel(
            name='Recommend',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('recommend_date', models.DateTimeField(default=datetime.datetime(2023, 8, 2, 17, 43, 32, 662123))),
                ('solved', models.BooleanField(null=True)),
                ('solve_date', models.DateTimeField(null=True)),
                ('good_recommend', models.BooleanField(null=True)),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='domainModel.project')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='studentModel.studentprofile')),
            ],
        ),
        migrations.CreateModel(
            name='PracticalSkill',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('skill', models.IntegerField(default=0)),
                ('generalConcept', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='domainModel.generalconcept')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='studentModel.studentprofile')),
            ],
        ),
        migrations.CreateModel(
            name='HintPerformance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('performance', models.CharField(default='', max_length=500)),
                ('date', models.DateTimeField(default=datetime.datetime(2023, 8, 2, 17, 43, 32, 646502))),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='studentModel.studentprofile')),
            ],
        ),
        migrations.CreateModel(
            name='DifficultyPerformance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('performance', models.DecimalField(decimal_places=3, max_digits=6)),
                ('date', models.DateTimeField(default=datetime.datetime(2023, 8, 2, 17, 43, 32, 646502))),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='studentModel.studentprofile')),
            ],
        ),
    ]
