# Generated by Django 5.1.5 on 2025-02-04 18:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('category', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='category',
            old_name='categoty_name',
            new_name='category_name',
        ),
    ]
