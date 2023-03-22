# Generated by Django 4.1.5 on 2023-03-11 14:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='GeneralConcept',
            fields=[
                ('name', models.CharField(max_length=255, primary_key=True, serialize=False)),
            ],
        ),
        migrations.CreateModel(
            name='SubConcept',
            fields=[
                ('name', models.CharField(max_length=255, primary_key=True, serialize=False)),
                ('generalConcept', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='domainModel.generalconcept')),
            ],
        ),
        migrations.CreateModel(
            name='Lesson',
            fields=[
                ('name', models.CharField(max_length=255, primary_key=True, serialize=False)),
                ('subConcept',
                 models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='domainModel.subconcept')),
            ],
        ),
        migrations.CreateModel(
            name='ParagraphData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subheading', models.CharField(max_length=255)),
                ('explanation', models.TextField()),
                ('nb', models.TextField(null=True)),
                ('img_src', models.TextField(null=True)),
                ('title', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='domainModel.lesson')),
            ],
        ),
        migrations.CreateModel(
            name='CodeData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('prefix_text', models.TextField()),
                ('code', models.TextField()),
                ('output', models.TextField()),
                ('codeExplanation', models.TextField()),
                ('paragraph', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='code_data', to='domainModel.paragraphdata')),
            ],
        ),
        migrations.CreateModel(
            name='ExampleData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('prefix_text', models.TextField()),
                ('example', models.TextField()),
                ('paragraph', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='example_data', to='domainModel.paragraphdata')),
            ],
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question', models.TextField()),
                ('correctAnswerSample', models.TextField()),
                ('output', models.TextField()),
                ('explanation', models.TextField()),
                ('hint', models.TextField(null=True)),
                ('difficulty', models.DecimalField(decimal_places=3, max_digits=6)),
                ('img_src', models.TextField(null=True)),
                ('subConcepts', models.ManyToManyField(to='domainModel.subconcept')),
            ],
        ),
        migrations.CreateModel(
            name='Operator',
            fields=[
                ('name', models.CharField(max_length=6, primary_key=True, serialize=False)),
                ('subConcepts', models.ManyToManyField(related_name='operators', to='domainModel.subconcept')),
            ],
        ),
        migrations.CreateModel(
            name='Keyword',
            fields=[
                ('name', models.CharField(max_length=50, primary_key=True, serialize=False)),
                ('subConcepts', models.ManyToManyField(related_name='keywords', to='domainModel.subconcept')),
            ],
        ),
    ]
