# Generated by Django 2.1 on 2018-08-21 13:25

import django.core.files.storage
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0012_auto_20180820_1924'),
    ]

    operations = [
        migrations.CreateModel(
            name='Imagen',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150)),
                ('image', models.ImageField(null=True, storage=django.core.files.storage.FileSystemStorage(location='C:\\salvar\\djangogirls\\static\\media'), upload_to='')),
                ('url', models.URLField(default='', max_length=100, unique=True)),
                ('preferred', models.BooleanField(default=False, verbose_name='Portada')),
            ],
        ),
        migrations.AddField(
            model_name='product',
            name='imagenes',
            field=models.ManyToManyField(to='shop.Imagen'),
        ),
    ]