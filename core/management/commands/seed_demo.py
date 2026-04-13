from pathlib import Path

from django.conf import settings
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from core.models import Category, NailDesign, NailShape, NailSize, NailSizeSet


# ── Catalogue data ────────────────────────────────────────────────────────────

CATEGORIES = [
    ('Abstract Art', 'abstract-art'),
    ('Floral',       'floral'),
    ('Glitter',      'glitter'),
    ('Minimalist',   'minimalist'),
    ('French Tips',  'french-tips'),
]

# (title, slug, category_slug, description, featured, image_filename)
DESIGNS = [
    (
        'Autumn Passion', 'autumn-passion', 'abstract-art',
        'Warm autumnal tones swirl together in an abstract display of rich reds, '
        'burnt oranges and golden highlights.',
        True, 'autumn_passion.jpg',
    ),
    (
        'Emerald Green', 'emerald-green', 'glitter',
        'Deep emerald base with a shimmer that catches every light. '
        'Bold, luxurious, unforgettable.',
        True, 'emerald_green.jpg',
    ),
    (
        'Floral Classic', 'floral-classic', 'floral',
        'Delicate hand-painted florals on a soft nude base — timeless femininity '
        'at your fingertips.',
        True, 'floral.png',
    ),
    (
        'Floral Lilac', 'floral-lilac', 'floral',
        'Dreamy lilac blooms on a blush background. Soft, romantic, '
        'and impossible to ignore.',
        True, 'floral_lila.png',
    ),
    (
        'Futuristic', 'futuristic', 'abstract-art',
        'Sharp geometric lines and metallic accents inspired by sci-fi aesthetics. '
        'Wear the future.',
        True, 'futurustic.png',
    ),
    (
        'Press-On Set', 'press-on-set', 'minimalist',
        'A clean, everyday set that proves less is more. '
        'Versatile enough for any occasion.',
        False, 'Screenshot_2026-04-13_122913.png',
    ),
]

SHAPES = [
    ('Short Almond',  'short-almond'),
    ('Short Square',  'short-square'),
    ('Medium Coffin', 'medium-coffin'),
    ('Medium Almond', 'medium-almond'),
]

# (sort_order, label, thumb, index, middle, ring, pinky) in mm
SIZE_SETS = [
    (1, 'XS', 14, 10, 11, 10,  9),
    (2, 'S',  15, 11, 12, 11,  9),
    (3, 'M',  16, 12, 13, 12, 10),
    (4, 'L',  17, 13, 14, 13, 10),
    (5, 'XL', 19, 14, 15, 14, 11),
]


# ── Command ───────────────────────────────────────────────────────────────────

class Command(BaseCommand):
    help = 'Seed categories, designs, shapes, sizes and admin user in one step'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Wipe all NailDesign records before re-seeding (keeps variants intact)',
        )

    def handle(self, *args, **options):
        self._seed_superuser()
        if options['reset']:
            self._reset_designs()
        cats = self._seed_categories()
        self._seed_designs(cats)
        shapes, size_sets = self._seed_variants()
        self._assign_variants(shapes, size_sets)

        self.stdout.write(self.style.SUCCESS(
            f'\nAll done — {NailDesign.objects.count()} designs, '
            f'{Category.objects.count()} categories, '
            f'{len(shapes)} shapes, {len(size_sets)} size sets.'
        ))
        self.stdout.write(self.style.WARNING(
            'Admin: http://localhost:8000/admin/  username=admin  password=admin'
        ))

    # ── helpers ───────────────────────────────────────────────────────────────

    def _seed_superuser(self):
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@artonpressies.com', 'admin')
            self.stdout.write(self.style.SUCCESS('Created superuser admin'))
        else:
            self.stdout.write('Superuser admin already exists')

    def _reset_designs(self):
        deleted, _ = NailDesign.objects.all().delete()
        self.stdout.write(self.style.WARNING(f'Deleted {deleted} design(s)'))

    def _seed_categories(self):
        cats = {}
        for name, slug in CATEGORIES:
            cat, created = Category.objects.get_or_create(slug=slug, defaults={'name': name})
            cats[slug] = cat
            if created:
                self.stdout.write(f'  + category: {name}')
        return cats

    def _seed_designs(self, cats):
        media_designs = Path(settings.MEDIA_ROOT) / 'designs'
        for title, slug, cat_slug, desc, featured, filename in DESIGNS:
            if NailDesign.objects.filter(slug=slug).exists():
                continue
            image_path = media_designs / filename
            if not image_path.exists():
                self.stdout.write(self.style.ERROR(
                    f'  missing image {filename} — skipping "{title}"'
                ))
                continue
            NailDesign.objects.create(
                title=title, slug=slug, description=desc,
                category=cats[cat_slug], featured=featured,
                image=f'designs/{filename}',
            )
            self.stdout.write(self.style.SUCCESS(f'  + design: {title}'))

    def _seed_variants(self):
        # Shapes
        shapes = []
        for name, slug in SHAPES:
            shape, created = NailShape.objects.get_or_create(slug=slug, defaults={'name': name})
            shapes.append(shape)
            if created:
                self.stdout.write(f'  + shape: {name}')

        # Individual mm sizes
        all_mm = sorted({mm for _order, _label, *vals in SIZE_SETS for mm in vals})
        size_objs = {}
        for mm in all_mm:
            obj, _ = NailSize.objects.get_or_create(width_mm=mm)
            size_objs[mm] = obj

        # Size sets — always patch sort_order so ordering is correct
        size_sets = []
        for order, label, thumb, index, middle, ring, pinky in SIZE_SETS:
            ss, created = NailSizeSet.objects.get_or_create(
                name=label,
                defaults=dict(
                    sort_order=order,
                    thumb=size_objs[thumb],   index=size_objs[index],
                    middle=size_objs[middle], ring=size_objs[ring],
                    pinky=size_objs[pinky],
                ),
            )
            if ss.sort_order != order:
                ss.sort_order = order
                ss.save(update_fields=['sort_order'])
            size_sets.append(ss)
            if created:
                self.stdout.write(self.style.SUCCESS(f'  + size set: {ss}'))

        return shapes, size_sets

    def _assign_variants(self, shapes, size_sets):
        for design in NailDesign.objects.all():
            design.available_shapes.set(shapes)
            design.available_size_sets.set(size_sets)
        self.stdout.write(f'  Variants assigned to all designs')
