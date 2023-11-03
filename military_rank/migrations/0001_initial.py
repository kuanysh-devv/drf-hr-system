# Generated by Django 4.2.7 on 2023-11-03 04:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='MilitaryRank',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rankTitle', models.CharField(max_length=255)),
                ('order', models.IntegerField()),
                ('nextPromotionDateInDays', models.IntegerField(default=1, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='RankInfo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('receivedType', models.CharField(max_length=255)),
                ('receivedDate', models.DateField()),
                ('militaryRank', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='military_rank.militaryrank')),
            ],
        ),
    ]
