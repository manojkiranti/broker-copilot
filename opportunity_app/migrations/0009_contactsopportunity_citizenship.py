# Generated by Django 5.0.6 on 2024-07-28 11:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('opportunity_app', '0008_alter_contactsopportunity_phone'),
    ]

    operations = [
        migrations.AddField(
            model_name='contactsopportunity',
            name='citizenship',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]