import uuid
from django.db import migrations, models


def assign_lookup_tokens(apps, schema_editor):
    Order = apps.get_model('core', 'Order')
    for order in Order.objects.filter(lookup_token__isnull=True):
        order.lookup_token = uuid.uuid4()
        order.save(update_fields=['lookup_token'])


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_order_orderitem'),
    ]

    operations = [
        # Step 1: add nullable, non-unique so SQLite can backfill without collisions
        migrations.AddField(
            model_name='order',
            name='lookup_token',
            field=models.UUIDField(null=True, blank=True),
        ),
        # Step 2: assign unique UUIDs to all existing rows
        migrations.RunPython(assign_lookup_tokens, migrations.RunPython.noop),
        # Step 3: enforce unique + not null
        migrations.AlterField(
            model_name='order',
            name='lookup_token',
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
        ),
        migrations.AddField(
            model_name='order',
            name='tracking_number',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AddField(
            model_name='order',
            name='tracking_url',
            field=models.URLField(blank=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(
                choices=[
                    ('pending', 'Pending'),
                    ('paid', 'Paid'),
                    ('shipped', 'Shipped'),
                    ('delivered', 'Delivered'),
                    ('cancelled', 'Cancelled'),
                    ('failed', 'Failed'),
                ],
                default='pending',
                max_length=20,
            ),
        ),
    ]
