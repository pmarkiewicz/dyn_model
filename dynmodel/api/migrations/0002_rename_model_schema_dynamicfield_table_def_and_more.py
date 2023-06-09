# Generated by Django 4.1.7 on 2023-03-27 09:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='dynamicfield',
            old_name='model_schema',
            new_name='table_def',
        ),
        migrations.AlterUniqueTogether(
            name='dynamicfield',
            unique_together={('name', 'table_def')},
        ),
        migrations.AlterField(
            model_name='dynamicfield',
            name='fld_type',
            field=models.CharField(choices=[('c', 'character'), ('b', 'boolean'), ('i', 'integer')], max_length=1),
        ),
    ]
