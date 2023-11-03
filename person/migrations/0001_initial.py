# Generated by Django 4.2.7 on 2023-11-03 04:45

import django.contrib.auth.models
import django.contrib.auth.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('location', '0001_initial'),
        ('identity_card_info', '0001_initial'),
        ('birth_info', '0001_initial'),
        ('auth', '0012_alter_user_first_name_max_length'),
        ('resident_info', '0001_initial'),
        ('photo', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='FamilyStatus',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('statusName', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Gender',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('genderName', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Person',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('iin', models.CharField(max_length=12)),
                ('pin', models.CharField(max_length=255)),
                ('surname', models.CharField(max_length=255)),
                ('firstName', models.CharField(max_length=255)),
                ('patronymic', models.CharField(max_length=255)),
                ('nationality', models.CharField(max_length=255)),
                ('birthInfoId', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='birth_info.birthinfo')),
                ('departmentId', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='location.department')),
                ('familyStatus', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='person.familystatus')),
                ('gender', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='person.gender')),
                ('identityCardInfoId', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='identity_card_info.identitycardinfo')),
                ('photoId', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='photo.photo')),
                ('residentInfoId', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='resident_info.residentinfo')),
            ],
        ),
        migrations.CreateModel(
            name='Relative',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('relativeName', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='SportSkill',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sportType', models.CharField(max_length=255)),
                ('sportSkillLvl', models.CharField(max_length=255)),
                ('personId', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='person.person')),
            ],
        ),
        migrations.CreateModel(
            name='Reward',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rewardType', models.CharField(max_length=255)),
                ('rewardDocNumber', models.CharField(max_length=255)),
                ('rewardDate', models.DateField()),
                ('personId', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='person.person')),
            ],
        ),
        migrations.CreateModel(
            name='LanguageSkill',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('langName', models.CharField(max_length=255)),
                ('skillLvl', models.CharField(max_length=255)),
                ('personId', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='person.person')),
            ],
        ),
        migrations.CreateModel(
            name='FamilyComposition',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('relName', models.CharField(max_length=255)),
                ('relSurname', models.CharField(max_length=255)),
                ('relPatronymic', models.CharField(max_length=255)),
                ('relIin', models.CharField(max_length=12)),
                ('relBirthDate', models.DateField()),
                ('relJobPlace', models.CharField(max_length=255)),
                ('personId', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='person.person')),
                ('relativeTypeId', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='person.relative')),
            ],
        ),
        migrations.CreateModel(
            name='ClassCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('categoryType', models.CharField(max_length=255)),
                ('personId', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='person.person')),
            ],
        ),
        migrations.CreateModel(
            name='Autobiography',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('autobiographyText', models.CharField(max_length=2096)),
                ('autobiographyImage', models.TextField()),
                ('personId', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='person.person')),
            ],
        ),
        migrations.CreateModel(
            name='CustomUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('person_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='person.person')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
    ]
