from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0007_backfill_user_taxonomy_fks'),
        ('destinations', '0012_finalize_travel_type_season_fk'),
    ]

    operations = [
        migrations.RemoveField(model_name='customuser', name='preferred_travel_type'),
        migrations.RemoveField(model_name='customuser', name='preferred_season'),
        migrations.RenameField(model_name='customuser', old_name='preferred_travel_type_new', new_name='preferred_travel_type'),
        migrations.RenameField(model_name='customuser', old_name='preferred_season_new', new_name='preferred_season'),
    ]
