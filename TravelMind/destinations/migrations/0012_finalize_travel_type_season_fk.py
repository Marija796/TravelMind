from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('destinations', '0011_seed_categories_seasons'),
    ]

    operations = [
        migrations.RemoveField(model_name='destination', name='travel_type'),
        migrations.RemoveField(model_name='destination', name='best_season'),
        migrations.RenameField(model_name='destination', old_name='travel_type_new', new_name='travel_type'),
        migrations.RenameField(model_name='destination', old_name='best_season_new', new_name='best_season'),
        migrations.AlterField(
            model_name='destination',
            name='travel_type',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name='destinations',
                to='destinations.travelcategory',
            ),
        ),
    ]
