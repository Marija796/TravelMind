from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_add_wishlist_visited'),
    ]

    operations = [
        migrations.RenameField(
            model_name='customuser',
            old_name='bio',
            new_name='short_summary',
        ),
        migrations.AlterField(
            model_name='customuser',
            name='short_summary',
            field=models.CharField(blank=True, max_length=280),
        ),
        migrations.AddField(
            model_name='customuser',
            name='gender',
            field=models.CharField(blank=True, choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other'), ('prefer_not_to_say', 'Prefer not to say')], max_length=20),
        ),
        migrations.AddField(
            model_name='customuser',
            name='profile_image',
            field=models.ImageField(blank=True, null=True, upload_to='profile_images/'),
        ),
        migrations.RemoveField(
            model_name='customuser',
            name='avatar_url',
        ),
    ]
