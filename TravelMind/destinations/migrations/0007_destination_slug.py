import re
import unicodedata
from django.db import migrations, models


def _make_slug(name):
    name = unicodedata.normalize('NFKD', name)
    name = name.encode('ascii', 'ignore').decode('ascii')
    name = name.lower()
    name = re.sub(r'[^\w\s-]', '', name)
    name = re.sub(r'[-\s]+', '-', name)
    return name.strip('-')


def populate_slugs(apps, schema_editor):
    Destination = apps.get_model('destinations', 'Destination')
    used = set()
    for dest in Destination.objects.all().order_by('id'):
        base = _make_slug(dest.name) or f'destination-{dest.pk}'
        slug = base
        counter = 2
        while slug in used:
            slug = f'{base}-{counter}'
            counter += 1
        used.add(slug)
        dest.slug = slug
        dest.save(update_fields=['slug'])


class Migration(migrations.Migration):

    dependencies = [
        ('destinations', '0006_destination_cost_breakdown'),
    ]

    operations = [
        # Step 1: add field without unique constraint
        migrations.AddField(
            model_name='destination',
            name='slug',
            field=models.SlugField(blank=True, max_length=250, default=''),
            preserve_default=False,
        ),
        # Step 2: populate slugs from names
        migrations.RunPython(populate_slugs, migrations.RunPython.noop),
        # Step 3: enforce unique constraint
        migrations.AlterField(
            model_name='destination',
            name='slug',
            field=models.SlugField(blank=True, max_length=250, unique=True),
        ),
    ]
