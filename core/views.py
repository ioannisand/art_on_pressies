from decimal import Decimal

import stripe
from django.conf import settings
from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .cart import Cart
from .forms import EnquiryForm
from .models import Category, NailDesign, NailSize, Order, OrderItem


def home(request):
    featured = NailDesign.objects.filter(featured=True)[:6]
    return render(request, 'home.html', {'featured_designs': featured})


def gallery(request):
    categories = Category.objects.all()
    category_slug = request.GET.get('category')

    designs = NailDesign.objects.select_related('category')
    active_category = None
    if category_slug:
        active_category = get_object_or_404(Category, slug=category_slug)
        designs = designs.filter(category=active_category)

    return render(request, 'gallery.html', {
        'designs': designs,
        'categories': categories,
        'active_category': active_category,
    })


def design_detail(request, slug):
    design = get_object_or_404(
        NailDesign.objects
        .select_related('category')
        .prefetch_related(
            'available_shapes',
            'available_size_sets__thumb',
            'available_size_sets__index',
            'available_size_sets__middle',
            'available_size_sets__ring',
            'available_size_sets__pinky',
        ),
        slug=slug,
    )
    nail_sizes = list(NailSize.objects.values_list('width_mm', flat=True))
    return render(request, 'design_detail.html', {
        'design': design,
        'nail_sizes': nail_sizes,
        'fingers': ['Thumb', 'Index', 'Middle', 'Ring', 'Pinky'],
    })


def search(request):
    query = request.GET.get('q', '').strip()
    results = []
    if query:
        results = NailDesign.objects.filter(
            Q(title__icontains=query) | Q(description__icontains=query) |
            Q(category__name__icontains=query)
        ).select_related('category').distinct()
    return render(request, 'search.html', {'query': query, 'results': results})


def about(request):
    return render(request, 'about.html')


@require_POST
def add_to_cart(request, slug):
    design = get_object_or_404(NailDesign, slug=slug)
    cart = Cart(request)

    shape_slug = request.POST.get('shape_slug', '')
    shape_name = request.POST.get('shape_name', '')
    size_name  = request.POST.get('size_name', '')
    custom_label = request.POST.get('custom_label', '') or None

    # Fall back if nothing selected
    if not shape_slug:
        first_shape = design.available_shapes.first()
        if first_shape:
            shape_slug = first_shape.slug
            shape_name = first_shape.name

    if not size_name and not custom_label:
        first_size = design.available_size_sets.order_by('sort_order').first()
        if first_size:
            size_name = first_size.name

    cart.add(
        design_slug=design.slug,
        design_title=design.title,
        design_image_url=design.image.url,
        shape_slug=shape_slug,
        shape_name=shape_name,
        size_name=size_name if not custom_label else 'Custom',
        custom_label=custom_label,
        unit_price=str(design.price),
    )
    messages.success(request, f'"{design.title}" added to your cart.')
    return redirect('design_detail', slug=slug)


def view_cart(request):
    cart = Cart(request)
    return render(request, 'cart.html', {'cart': cart})


@require_POST
def remove_from_cart(request):
    Cart(request).remove(request.POST.get('key', ''))
    return redirect('view_cart')


@require_POST
def update_cart(request):
    cart = Cart(request)
    key = request.POST.get('key', '')
    qty = request.POST.get('qty', 1)
    cart.update_qty(key, qty)
    return redirect('view_cart')


def checkout(request):
    cart = Cart(request)
    if not cart.items:
        return redirect('view_cart')
    shipping = Decimal(settings.SHIPPING_FEE_CENTS) / Decimal(100)
    return render(request, 'checkout.html', {
        'cart': cart,
        'shipping': shipping,
        'grand_total': cart.total + shipping,
    })


@require_POST
def create_checkout_session(request):
    cart = Cart(request)
    if not cart.items:
        return redirect('view_cart')

    stripe.api_key = settings.STRIPE_SECRET_KEY

    order = Order.objects.create(
        subtotal=cart.total,
        shipping=Decimal(settings.SHIPPING_FEE_CENTS) / Decimal(100),
        total=cart.total + Decimal(settings.SHIPPING_FEE_CENTS) / Decimal(100),
        currency=settings.CURRENCY,
    )

    line_items = []
    for item in cart.items:
        design = NailDesign.objects.filter(slug=item['design_slug']).first()
        OrderItem.objects.create(
            order=order,
            design=design,
            design_slug=item['design_slug'],
            design_title=item['design_title'],
            design_image_url=item['design_image_url'],
            shape_name=item['shape_name'] or '',
            size_name=item['size_name'] or '',
            custom_label=item.get('custom_label') or '',
            unit_price=item['unit_price_decimal'],
            qty=item['qty'],
        )

        parts = []
        if item['shape_name']:
            parts.append(f'Shape: {item["shape_name"]}')
        if item.get('custom_label'):
            parts.append(f'Size: {item["custom_label"]}')
        elif item['size_name']:
            parts.append(f'Size: {item["size_name"]}')
        product_data = {'name': item['design_title']}
        if parts:
            product_data['description'] = ' | '.join(parts)

        line_items.append({
            'quantity': item['qty'],
            'price_data': {
                'currency': settings.CURRENCY,
                'unit_amount': int(item['unit_price_decimal'] * 100),
                'product_data': product_data,
            },
        })

    session = stripe.checkout.Session.create(
        mode='payment',
        line_items=line_items,
        shipping_address_collection={'allowed_countries': settings.ALLOWED_SHIPPING_COUNTRIES},
        shipping_options=[{
            'shipping_rate_data': {
                'type': 'fixed_amount',
                'fixed_amount': {
                    'amount': settings.SHIPPING_FEE_CENTS,
                    'currency': settings.CURRENCY,
                },
                'display_name': 'Standard shipping (Greece)',
            },
        }],
        success_url=(
            request.build_absolute_uri(reverse('checkout_success'))
            + '?session_id={CHECKOUT_SESSION_ID}'
        ),
        cancel_url=request.build_absolute_uri(reverse('checkout_cancel')),
        client_reference_id=str(order.pk),
        metadata={'order_id': str(order.pk)},
    )

    order.stripe_session_id = session.id
    order.save(update_fields=['stripe_session_id'])

    return redirect(session.url, permanent=False)


def checkout_success(request):
    session_id = request.GET.get('session_id', '')
    order = Order.objects.filter(stripe_session_id=session_id).first() if session_id else None
    Cart(request).clear()
    return render(request, 'checkout_success.html', {'order': order})


def checkout_cancel(request):
    return render(request, 'checkout_cancel.html')


@csrf_exempt
@require_POST
def stripe_webhook(request):
    import sys
    import traceback
    try:
        stripe.api_key = settings.STRIPE_SECRET_KEY
        payload = request.body
        sig_header = request.headers.get('Stripe-Signature', '')

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
        except (ValueError, stripe.error.SignatureVerificationError) as sig_err:
            print(f'[stripe-webhook] signature error: {sig_err}', file=sys.stderr, flush=True)
            return HttpResponseBadRequest('Invalid webhook signature')

        print(f'[stripe-webhook] received event type={event["type"]} id={event["id"]}',
              file=sys.stderr, flush=True)

        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']

            def _g(obj, key, default=''):
                if obj is None:
                    return default
                try:
                    val = obj[key]
                except (KeyError, TypeError):
                    return default
                return val if val is not None else default

            order = Order.objects.filter(stripe_session_id=_g(session, 'id')).first()
            if order and order.status != Order.STATUS_PAID:
                order.status = Order.STATUS_PAID
                order.paid_at = timezone.now()
                order.stripe_payment_intent_id = _g(session, 'payment_intent')
                customer = _g(session, 'customer_details', None) or {}
                order.customer_email = _g(customer, 'email')
                order.customer_name = _g(customer, 'name')
                shipping_details = _g(session, 'shipping_details', None) or {}
                addr = _g(shipping_details, 'address', None) or {}
                if addr:
                    lines = [
                        _g(addr, 'line1'),
                        _g(addr, 'line2'),
                        f"{_g(addr, 'postal_code')} {_g(addr, 'city')}".strip(),
                        _g(addr, 'country'),
                    ]
                    order.shipping_address = '\n'.join(l for l in lines if l.strip())
                order.save()
                print(f'[stripe-webhook] order {order.pk} marked paid', file=sys.stderr, flush=True)
            else:
                print(f'[stripe-webhook] order not found or already paid for session {_g(session, "id")}',
                      file=sys.stderr, flush=True)

        return HttpResponse(status=200)
    except Exception as exc:
        print(f'[stripe-webhook] UNHANDLED: {type(exc).__name__}: {exc}',
              file=sys.stderr, flush=True)
        traceback.print_exc(file=sys.stderr)
        sys.stderr.flush()
        raise


def contact(request):
    if request.method == 'POST':
        form = EnquiryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Thanks for your enquiry! We\'ll get back to you soon.')
            return redirect('contact')
    else:
        design_slug = request.GET.get('design')
        initial = {}
        if design_slug:
            design = NailDesign.objects.filter(slug=design_slug).first()
            if design:
                initial['design'] = design.pk
        form = EnquiryForm(initial=initial)

    return render(request, 'contact.html', {'form': form})
