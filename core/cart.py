class Cart:
    SESSION_KEY = 'cart'

    def __init__(self, request):
        self._session = request.session
        self._cart = self._session.setdefault(self.SESSION_KEY, {'items': {}})

    def _save(self):
        self._session.modified = True

    # ── public API ────────────────────────────────────────────────────────────

    def add(self, *, design_slug, design_title, design_image_url,
            shape_slug, shape_name, size_name, custom_label=None, qty=1):
        # custom_label arrives as "Thumb:14|Index:10|..." — convert to display form
        custom_display = None
        if custom_label:
            parts = []
            for segment in custom_label.split('|'):
                if ':' in segment:
                    finger, mm = segment.split(':', 1)
                    parts.append(f'{mm}mm')
            custom_display = ' · '.join(parts) if parts else custom_label

        key = self._make_key(design_slug, shape_slug, size_name, custom_label)
        items = self._cart['items']
        if key in items:
            items[key]['qty'] += qty
        else:
            items[key] = {
                'key': key,
                'design_slug': design_slug,
                'design_title': design_title,
                'design_image_url': design_image_url,
                'shape_slug': shape_slug,
                'shape_name': shape_name,
                'size_name': size_name,
                'custom_label': custom_display,
                'qty': qty,
            }
        self._save()

    def remove(self, key):
        self._cart['items'].pop(key, None)
        self._save()

    def update_qty(self, key, qty):
        qty = int(qty)
        if qty <= 0:
            self.remove(key)
        elif key in self._cart['items']:
            self._cart['items'][key]['qty'] = qty
            self._save()

    def clear(self):
        self._cart['items'] = {}
        self._save()

    @property
    def items(self):
        return list(self._cart['items'].values())

    @property
    def count(self):
        return sum(item['qty'] for item in self._cart['items'].values())

    # ── helpers ───────────────────────────────────────────────────────────────

    @staticmethod
    def _make_key(design_slug, shape_slug, size_name, custom_label):
        if custom_label:
            return f'{design_slug}|{shape_slug}|custom|{custom_label}'
        return f'{design_slug}|{shape_slug}|{size_name}'
