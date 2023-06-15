from django.db import migrations


def load_fixture(apps, schema_editor):
    from django.core.management import call_command
    call_command('loaddata', 'fixture_data.json')


def reverse_func(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0024_alter_profile_slug'),
    ]

    operations = [
        migrations.RunPython(load_fixture, reverse_func),
    ]
