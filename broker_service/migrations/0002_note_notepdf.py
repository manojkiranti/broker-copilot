# Generated by Django 5.0.6 on 2024-08-29 10:11

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('broker_service', '0001_initial'),
        ('opportunity_app', '0009_contactsopportunity_citizenship'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Note',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('loan_details', models.JSONField(default=dict)),
                ('funds_available', models.JSONField(default=dict)),
                ('funds_complete', models.JSONField(default=dict)),
                ('loan_purpose_note', models.TextField(blank=True, null=True)),
                ('applicant_overview_note', models.TextField(blank=True, null=True)),
                ('living_condition_note', models.TextField(blank=True, null=True)),
                ('employment_income_note', models.TextField(blank=True, null=True)),
                ('commitments_note', models.TextField(blank=True, null=True)),
                ('other_note', models.TextField(blank=True, null=True)),
                ('mitigants_note', models.TextField(blank=True, null=True)),
                ('status', models.CharField(choices=[('active', 'Active'), ('inactive', 'Inactive')], default='active', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_broker_note', to=settings.AUTH_USER_MODEL)),
                ('opportunity', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='broker_opportunities', to='opportunity_app.opportunity')),
                ('updated_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='updated_broker_note', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='NotePdf',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pdf_url', models.URLField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('note', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pdfs', to='broker_service.note')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
