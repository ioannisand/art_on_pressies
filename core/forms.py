from django import forms

from .models import Enquiry

INPUT_CLASS = (
    'w-full px-4 py-3 rounded-xl border border-white/60 '
    'bg-white/60 focus:border-orchid focus:outline-none text-plum backdrop-blur-sm'
)


class EnquiryForm(forms.ModelForm):
    class Meta:
        model = Enquiry
        fields = ['name', 'email', 'phone', 'design', 'message']
        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': 'Your name',
                'class': INPUT_CLASS,
            }),
            'email': forms.EmailInput(attrs={
                'placeholder': 'your@email.com',
                'class': INPUT_CLASS,
            }),
            'phone': forms.TextInput(attrs={
                'placeholder': 'Phone number (optional)',
                'class': INPUT_CLASS,
            }),
            'design': forms.Select(attrs={
                'class': INPUT_CLASS,
            }),
            'message': forms.Textarea(attrs={
                'placeholder': 'Tell us about your dream nails...',
                'rows': 5,
                'class': INPUT_CLASS,
            }),
        }
