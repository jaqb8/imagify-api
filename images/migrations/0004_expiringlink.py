# Generated by Django 4.1.3 on 2023-09-21 09:56

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('images', '0003_alter_image_id_alter_image_thumbnail_200_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExpiringLink',
            fields=[
                ('alias', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('expires_in', models.IntegerField(validators=[django.core.validators.MinValueValidator(30), django.core.validators.MaxValueValidator(30000)])),
                ('image', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='images.image')),
            ],
        ),
    ]