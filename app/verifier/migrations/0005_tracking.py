# Generated by Django 2.2.9 on 2020-01-31 17:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('verifier', '0004_auto_20200127_1923'),
    ]

    operations = [
        migrations.AddField(
            model_name='lookup',
            name='source',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='lookup',
            name='utm_campaign',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='lookup',
            name='utm_medium',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='lookup',
            name='utm_source',
            field=models.TextField(blank=True, null=True),
        ),
    ]
