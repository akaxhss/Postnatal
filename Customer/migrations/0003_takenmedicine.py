# Generated by Django 4.2.6 on 2023-11-22 08:23

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('Customer', '0002_alter_medicinetime_options'),
    ]

    operations = [
        migrations.CreateModel(
            name='TakenMedicine',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('taken', models.BooleanField(default=False)),
                ('customer', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('medicine', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='MedicineDetail', to='Customer.medicines')),
            ],
            options={
                'ordering': ['-date'],
                'unique_together': {('medicine', 'customer', 'date')},
            },
        ),
    ]
