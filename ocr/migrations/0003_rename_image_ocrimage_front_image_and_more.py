# Generated by Django 5.2 on 2025-04-10 07:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ocr', '0002_ocrimage_authority_ocrimage_birth_place_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='ocrimage',
            old_name='image',
            new_name='front_image',
        ),
        migrations.AddField(
            model_name='ocrimage',
            name='back_image',
            field=models.ImageField(blank=True, null=True, upload_to='ocr_images/'),
        ),
        migrations.AddField(
            model_name='ocrimage',
            name='labeled_back_image',
            field=models.ImageField(blank=True, null=True, upload_to='labeled_images/'),
        ),
        migrations.AddField(
            model_name='ocrimage',
            name='labeled_front_image',
            field=models.ImageField(blank=True, null=True, upload_to='labeled_images/'),
        ),
    ]
