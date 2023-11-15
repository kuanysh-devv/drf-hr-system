# Generated by Django 4.2.7 on 2023-11-10 09:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('staffing_table', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='staffingtable',
            old_name='count',
            new_name='current_count',
        ),
        migrations.AddField(
            model_name='staffingtable',
            name='max_count',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
    ]