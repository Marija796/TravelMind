from django.db import migrations
from destinations.link_generators import generate_booking_url, generate_flight_url


def backfill(apps, schema_editor):
    # AddField (previous migration) sets booking_url/flight_url to '' on
    # every existing row via a raw ALTER TABLE - it does not run
    # Destination.save(), so the auto-fill-when-blank logic there never
    # touched these 100 rows. Backfill them here with the same generator
    # functions save() uses, so pre-existing destinations end up with the
    # same real, working links a newly-created one gets automatically.
    Destination = apps.get_model('destinations', 'Destination')
    for dest in Destination.objects.all():
        dest.booking_url = generate_booking_url(dest.city, dest.country)
        dest.flight_url = generate_flight_url(dest.city, dest.name)
        dest.save(update_fields=['booking_url', 'flight_url'])


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('destinations', '0014_add_booking_flight_and_searchlog'),
    ]

    operations = [
        migrations.RunPython(backfill, noop_reverse),
    ]
