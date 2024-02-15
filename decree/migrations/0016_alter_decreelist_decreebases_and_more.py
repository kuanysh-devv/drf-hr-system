# Generated by Django 4.2.7 on 2024-02-14 11:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('decree', '0015_alter_decreelist_decreebases'),
    ]

    operations = [
        migrations.AlterField(
            model_name='decreelist',
            name='decreeBases',
            field=models.ManyToManyField(blank=True, to='decree.base', verbose_name='Bases'),
        ),
        migrations.AlterField(
            model_name='decreelist',
            name='minioDocName',
            field=models.CharField(blank=True, default='None', max_length=4048, null=True, verbose_name='minioDocName'),
        ),
    ]
