# Generated by Django 3.2.3 on 2021-07-02 14:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dictionary', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='dictionaryentry',
            name='icons',
        ),
        migrations.RemoveField(
            model_name='thesaurusentry',
            name='icons',
        ),
        migrations.AddField(
            model_name='icon',
            name='descriptor',
            field=models.CharField(blank=True, max_length=32, null=True),
        ),
        migrations.AddField(
            model_name='icon',
            name='tense',
            field=models.PositiveSmallIntegerField(blank=True, choices=[(None, 0), ('1', 1), ('c', 2), ('p', 3), ('pp', 4)], default=None, null=True),
        ),
        migrations.AddField(
            model_name='icon',
            name='word',
            field=models.CharField(default='word', max_length=32),
            preserve_default=False,
        ),
    ]
