# Generated by Django 5.1.4 on 2025-02-08 05:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0014_alter_bid_options_alter_bid_amount'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='bid',
            options={'ordering': ['-amount']},
        ),
    ]
