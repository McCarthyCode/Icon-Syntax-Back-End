# Generated by Django 4.0.3 on 2022-03-09 19:14

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='datetime created')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='datetime updated')),
                ('name', models.CharField(max_length=40, unique=True, verbose_name='Name')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='PDF',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='datetime created')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='datetime updated')),
                ('title', models.CharField(max_length=80, verbose_name='Title')),
                ('pdf', models.FileField(max_length=160, upload_to='pdf', verbose_name='PDF')),
                ('_hash', models.BinaryField(max_length=16, null=True, verbose_name='MD5 hash')),
                ('categories', models.ManyToManyField(to='pdf.category')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
