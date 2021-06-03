# Generated by Django 3.2.3 on 2021-05-26 13:21

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
                ('image', models.ImageField(blank=True, default=None, null=True, upload_to='icons')),
                ('_hash', models.BinaryField(default=None, max_length=16, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='MP3',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='datetime created')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='datetime updated')),
                ('mw', models.CharField(max_length=64)),
                ('wn', models.CharField(max_length=64)),
                ('data', models.FileField(upload_to='mp3', verbose_name='MP3')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Entry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='datetime created')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='datetime updated')),
                ('mw', models.CharField(max_length=64)),
                ('wn', models.CharField(max_length=64)),
                ('data', models.TextField(verbose_name='JSON data')),
                ('icon', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='dictionary.icon')),
                ('mp3', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='dictionary.mp3', verbose_name='MP3')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
