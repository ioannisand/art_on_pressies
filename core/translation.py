from modeltranslation.translator import register, TranslationOptions

from .models import NailDesign


@register(NailDesign)
class NailDesignTranslationOptions(TranslationOptions):
    # Only the long-form description is translated. Titles and category names
    # stay identical in both languages (brand-style names read fine untranslated).
    fields = ('description',)
