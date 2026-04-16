from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.views.decorators.http import require_POST

from django.db.models import Q

from .cart import Cart
from .models import Category, NailDesign, NailSize
from .forms import EnquiryForm


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
    return render(request, 'checkout.html', {'cart': cart})


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
