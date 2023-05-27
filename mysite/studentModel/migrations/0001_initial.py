# Generated by Django 4.1.5 on 2023-05-25 16:13

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('domainModel', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PersonalitiesNames',
            fields=[
                ('personalityName', models.CharField(max_length=255, primary_key=True, serialize=False)),
            ],
        ),
        migrations.CreateModel(
            name='StudentProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('studentKnowledge', models.ManyToManyField(to='domainModel.paragraphdata')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='TimePerformance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('performance', models.DecimalField(decimal_places=3, max_digits=6)),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='studentModel.studentprofile')),
            ],
        ),
        migrations.CreateModel(
            name='TheoreticalSkill',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('skill', models.IntegerField()),
                ('self_rate', models.IntegerField()),
                ('availability', models.BooleanField()),
                ('generalConcept', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='domainModel.generalconcept')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='studentModel.studentprofile')),
            ],
        ),
        migrations.CreateModel(
            name='StudentProject',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('solve_date', models.DateTimeField(default=None)),
                ('solutionCode', models.TextField()),
                ('used_concept_difficulty', models.IntegerField()),
                ('hint_levels', models.CharField(default='', max_length=255)),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='domainModel.project')),
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
            name='PracticalSkill',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('skill', models.IntegerField(default=0)),
                ('generalConcept', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='domainModel.generalconcept')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='studentModel.studentprofile')),
            ],
        ),
        migrations.CreateModel(
            name='PersonalitiesLetters',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('e', models.DecimalField(decimal_places=2, max_digits=6)),
                ('i', models.DecimalField(decimal_places=2, max_digits=6)),
                ('s', models.DecimalField(decimal_places=2, max_digits=6)),
                ('n', models.DecimalField(decimal_places=2, max_digits=6)),
                ('t', models.DecimalField(decimal_places=2, max_digits=6)),
                ('f', models.DecimalField(decimal_places=2, max_digits=6)),
                ('j', models.DecimalField(decimal_places=2, max_digits=6)),
                ('p', models.DecimalField(decimal_places=2, max_digits=6)),
                ('personalityName', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='studentModel.personalitiesnames')),
                ('studentProfile', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='studentModel.studentprofile')),
            ],
        ),
        migrations.CreateModel(
            name='HintPerformance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('performance', models.DecimalField(decimal_places=3, max_digits=6)),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='studentModel.studentprofile')),
            ],
        ),
        migrations.CreateModel(
            name='DifficultyPerformance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('performance', models.DecimalField(decimal_places=3, max_digits=6)),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='studentModel.studentprofile')),
            ],
        ),
    ]
