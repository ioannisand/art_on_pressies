from django.db import migrations, models


def copy_description_to_en(apps, schema_editor):
    """Backfill the English translation column from the existing description."""
    NailDesign = apps.get_model('core', 'NailDesign')
    for design in NailDesign.objects.all():
        NailDesign.objects.filter(pk=design.pk).update(description_en=design.description)


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_pricing_and_delivery'),
    ]

    operations = [
        migrations.AddField(
            model_name='naildesign',
            name='description_en',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='naildesign',
            name='description_el',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.RunPython(copy_description_to_en, noop),
    ]
