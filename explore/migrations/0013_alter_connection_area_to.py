# Generated by Django 3.2.5 on 2022-01-31 23:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('explore', '0012_news'),
    ]

    operations = [
        migrations.AlterField(
            model_name='connection',
            name='area_to',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='incoming', to='explore.area'),
        ),
    ]
