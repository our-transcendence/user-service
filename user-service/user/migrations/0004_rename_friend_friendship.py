# Generated by Django 5.0.4 on 2024-05-18 15:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0003_alter_user_id'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Friend',
            new_name='Friendship',
        ),
    ]
