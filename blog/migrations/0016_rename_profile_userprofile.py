# Generated by Django 4.2.4 on 2023-10-01 19:03

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('blog', '0015_profile_delete_userprofile'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Profile',
            new_name='UserProfile',
        ),
    ]