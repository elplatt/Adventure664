# Generated by Django 3.0.2 on 2020-02-09 16:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('explore', '0010_auto_20200209_1653'),
    ]

    operations = [
        migrations.AlterField(
            model_name='area',
            name='description',
            field=models.TextField(blank=True, default=''),
        ),
    ]