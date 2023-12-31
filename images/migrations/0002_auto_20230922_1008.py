# Generated by Django 4.1.3 on 2023-09-22 10:08

from django.db import migrations
from django.contrib.auth.models import Permission, Group
from django.core.management.sql import emit_post_migrate_signal


def create_groups(apps, schema_editor):
    # workaround for creating permissions in migrations
    db_alias = schema_editor.connection.alias
    emit_post_migrate_signal(2, False, db_alias)

    perm_200px = Permission.objects.get(codename="thumbnail:200")
    perm_400px = Permission.objects.get(codename="thumbnail:400")
    perm_original = Permission.objects.get(codename="can_access_original_image")
    perm_expiring_link = Permission.objects.get(codename="can_generate_expiring_link")

    basic_tier, _ = Group.objects.get_or_create(name="BasicTierUsers")
    basic_tier.permissions.add(perm_200px)

    premium_tier, _ = Group.objects.get_or_create(name="PremiumTierUsers")
    premium_tier.permissions.add(perm_200px, perm_400px)

    enterprise_tier, _ = Group.objects.get_or_create(name="EnterpriseTierUsers")
    enterprise_tier.permissions.add(
        perm_200px, perm_400px, perm_original, perm_expiring_link
    )


class Migration(migrations.Migration):
    dependencies = [
        ("images", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(create_groups),
    ]
