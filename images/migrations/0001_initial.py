# Generated by Django 4.1.3 on 2023-09-25 10:22

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import images.models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('original_file', models.ImageField(upload_to=images.models.original_image_path)),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'permissions': [('can_access_original_image', 'Can access original image'), ('thumbnail:200', 'can access 200px thumbnail'), ('thumbnail:400', 'can access 400px thumbnail')],
            },
        ),
        migrations.CreateModel(
            name='ExpiringLink',
            fields=[
                ('alias', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('expires_in', models.IntegerField(validators=[django.core.validators.MinValueValidator(30), django.core.validators.MaxValueValidator(30000)])),
                ('image', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='images.image')),
            ],
            options={
                'permissions': [('can_generate_expiring_link', 'Can generate expiring link')],
            },
        ),
    ]
