# Generated by Django 3.2.4 on 2021-06-24 20:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Icon',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='datetime created')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='datetime updated')),
                ('image', models.ImageField(blank=True, default=None, null=True, upload_to='img')),
                ('_hash', models.BinaryField(default=None, max_length=16, null=True, verbose_name='MD5 hash')),
                ('is_approved', models.BooleanField(default=False)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='MP3',
            fields=[
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='datetime created')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='datetime updated')),
                ('id', models.CharField(max_length=64, primary_key=True, serialize=False)),
                ('mp3', models.FileField(upload_to='mp3', verbose_name='MP3')),
                ('_hash', models.BinaryField(default=None, max_length=16, null=True, verbose_name='MD5 hash')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Word',
            fields=[
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='datetime created')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='datetime updated')),
                ('id', models.CharField(max_length=64, primary_key=True, serialize=False)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ThesaurusEntry',
            fields=[
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='datetime created')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='datetime updated')),
                ('id', models.CharField(max_length=64, primary_key=True, serialize=False)),
                ('json', models.TextField(default='', verbose_name='Merriam-Webster thesaurus entry')),
                ('icons', models.ManyToManyField(to='dictionary.Icon')),
                ('mp3', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='dictionary.mp3')),
                ('word', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dictionary.word')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='DictionaryEntry',
            fields=[
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='datetime created')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='datetime updated')),
                ('id', models.CharField(max_length=64, primary_key=True, serialize=False)),
                ('json', models.TextField(default='', verbose_name='Merriam-Webster dictionary entry')),
                ('icons', models.ManyToManyField(to='dictionary.Icon')),
                ('mp3', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='dictionary.mp3')),
                ('word', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dictionary.word')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
