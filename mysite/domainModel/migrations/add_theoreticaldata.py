from django.db import migrations, models
import django.db.models.deletion
import csv


class Migration(migrations.Migration):
    def load_data(apps, schema_editor):
        GeneralConcept = apps.get_model('domainModel', 'GeneralConcept')
        SubConcept = apps.get_model('domainModel', 'SubConcept')
        Lesson = apps.get_model('domainModel', 'Lesson')
        ParagraphData = apps.get_model('domainModel', 'ParagraphData')
        CodeData = apps.get_model('domainModel', 'CodeData')
        ExampleData = apps.get_model('domainModel', 'ExampleData')
        concepts_level = {'الأساسيات': 1,
                          'أنواع البيانات': 2,
                          'المتغيرات': 2,
                          'التعامل مع الأعداد': 3,
                          'التعامل مع النصوص': 3,
                          'العوامل': 3,
                          'المصفوفات': 3,
                          'الدوال': 3,
                          'الحلقات': 4,
                          'الشروط': 4}
        with open('harmash_data.csv', encoding='utf-8') as f:
            reader = csv.reader(f)
            header = next(reader)  # skip header row
            i = 0
            for row in reader:
                i += 1
                # Create or get the GeneralConcept object
                generalconcept, created = GeneralConcept.objects.get_or_create(name=row[0],
                                                                               concept_level=concepts_level[row[0]])
                # Create the SubConcept object with foreign key to GeneralConcept
                subconcept, created = SubConcept.objects.get_or_create(name=row[1], order=row[14],
                                                                       generalConcept=generalconcept)
                # Create the Lesson object with foreign key to SubConcept
                lesson, created = Lesson.objects.get_or_create(name=row[2], subConcept=subconcept)
                # Create the ParagraphData object with foreign key to Lesson
                paragraphData = ParagraphData.objects.create(title=lesson, subheading=row[3],
                                                             order=row[13],
                                                             explanation=row[4], nb=row[5], img_src=row[6])

                codeData = CodeData.objects.create(paragraph=paragraphData, prefix_text=row[9], code=row[10],
                                                   output=row[11],
                                                   codeExplanation=row[12])
                exampleData = ExampleData.objects.create(paragraph=paragraphData, prefix_text=row[8], example=row[7])
                # print(f"data {i} loaded!")

    dependencies = [
        ('domainModel', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(load_data),
    ]
