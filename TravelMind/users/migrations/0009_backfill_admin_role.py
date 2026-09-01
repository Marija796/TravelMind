from django.db import migrations, models


def backfill_admin_role(apps, schema_editor):
    """
    Accounts created via `createsuperuser` before the `role` field existed
    (is_staff/is_superuser=True) default to role='user'. Without this, an
    existing Django-admin superuser can't reach the app's own admin
    dashboard, which is gated on `role`, not is_staff/is_superuser.
    """
    CustomUser = apps.get_model('users', 'CustomUser')
    CustomUser.objects.filter(role='user').filter(
        models.Q(is_staff=True) | models.Q(is_superuser=True)
    ).update(role='admin')


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0008_finalize_taxonomy_fk'),
    ]

    operations = [
        migrations.RunPython(backfill_admin_role, noop_reverse),
    ]
