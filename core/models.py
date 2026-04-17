import uuid

from django.db import models


class SiteSettings(models.Model):
    logo = models.ImageField(upload_to='site/', blank=True)
    site_name = models.CharField(max_length=200, default='Art on Pressies')

    class Meta:
        verbose_name = 'Site Settings'
        verbose_name_plural = 'Site Settings'

    def __str__(self):
        return 'Site Settings'

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name_plural = 'categories'
        ordering = ['name']

    def __str__(self):
        return self.name


class NailDesign(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='designs/')
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name='designs'
    )
    price = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    original_price = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    available_shapes    = models.ManyToManyField('NailShape',   blank=True, related_name='designs')
    available_size_sets = models.ManyToManyField('NailSizeSet', blank=True, related_name='designs')

    class Meta:
        ordering = ['-created_at']

    @property
    def discount_percent(self):
        if self.original_price and self.original_price > self.price:
            return int(round((1 - self.price / self.original_price) * 100))
        return None

    def __str__(self):
        return self.title


class NailShape(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class NailSize(models.Model):
    """A single nail-width measurement in mm (e.g. 9, 10, 11 …)."""
    width_mm = models.PositiveSmallIntegerField(unique=True)

    class Meta:
        ordering = ['width_mm']

    def __str__(self):
        return f'{self.width_mm} mm'


class NailSizeSet(models.Model):
    """
    A named set of per-finger widths (thumb → index → middle → ring → pinky).
    Standard sets: XS, S, M, L, XL. Admins can also create custom sets.
    """
    name       = models.CharField(max_length=30)
    sort_order = models.PositiveSmallIntegerField(default=0)
    thumb  = models.ForeignKey(NailSize, related_name='thumb_sets',  on_delete=models.PROTECT)
    index  = models.ForeignKey(NailSize, related_name='index_sets',  on_delete=models.PROTECT)
    middle = models.ForeignKey(NailSize, related_name='middle_sets', on_delete=models.PROTECT)
    ring   = models.ForeignKey(NailSize, related_name='ring_sets',   on_delete=models.PROTECT)
    pinky  = models.ForeignKey(NailSize, related_name='pinky_sets',  on_delete=models.PROTECT)

    class Meta:
        ordering = ['sort_order', 'name']

    @property
    def measurements(self):
        return (
            self.thumb.width_mm, self.index.width_mm, self.middle.width_mm,
            self.ring.width_mm,  self.pinky.width_mm,
        )

    @property
    def measurements_display(self):
        return ' · '.join(f'{w}' for w in self.measurements) + ' mm'

    def __str__(self):
        return f'{self.name}  ({self.measurements_display})'


class Order(models.Model):
    DELIVERY_BOXNOW = 'boxnow'
    DELIVERY_COURIER = 'courier'
    DELIVERY_CHOICES = [
        (DELIVERY_BOXNOW, 'BoxNow'),
        (DELIVERY_COURIER, 'Courier'),
    ]

    STATUS_PENDING = 'pending'
    STATUS_PAID = 'paid'
    STATUS_SHIPPED = 'shipped'
    STATUS_DELIVERED = 'delivered'
    STATUS_CANCELLED = 'cancelled'
    STATUS_FAILED = 'failed'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_PAID, 'Paid'),
        (STATUS_SHIPPED, 'Shipped'),
        (STATUS_DELIVERED, 'Delivered'),
        (STATUS_CANCELLED, 'Cancelled'),
        (STATUS_FAILED, 'Failed'),
    ]

    lookup_token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    delivery_method = models.CharField(max_length=20, choices=DELIVERY_CHOICES, blank=True)
    stripe_session_id = models.CharField(max_length=200, unique=True, blank=True, null=True)
    stripe_payment_intent_id = models.CharField(max_length=200, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    tracking_number = models.CharField(max_length=200, blank=True)
    tracking_url = models.URLField(blank=True)

    customer_email = models.EmailField(blank=True)
    customer_name = models.CharField(max_length=200, blank=True)
    shipping_address = models.TextField(blank=True)

    subtotal = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    shipping = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    currency = models.CharField(max_length=3, default='eur')

    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Order #{self.pk} ({self.status})'


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    design = models.ForeignKey(
        NailDesign, on_delete=models.SET_NULL, null=True, blank=True, related_name='order_items'
    )
    design_slug = models.CharField(max_length=200)
    design_title = models.CharField(max_length=200)
    design_image_url = models.CharField(max_length=500, blank=True)
    shape_name = models.CharField(max_length=100, blank=True)
    size_name = models.CharField(max_length=100, blank=True)
    custom_label = models.CharField(max_length=200, blank=True)
    unit_price = models.DecimalField(max_digits=6, decimal_places=2)
    qty = models.PositiveIntegerField(default=1)

    @property
    def line_total(self):
        return self.unit_price * self.qty

    def __str__(self):
        return f'{self.qty} × {self.design_title}'


class Enquiry(models.Model):
    name = models.CharField(max_length=150)
    email = models.EmailField()
    phone = models.CharField(max_length=30, blank=True)
    design = models.ForeignKey(
        NailDesign, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='enquiries'
    )
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'enquiries'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name} — {self.created_at:%Y-%m-%d}'
