from django import forms
from .models import Service, Review

class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['title', 'description', 'karma_reward']

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.HiddenInput(),
            'comment': forms.Textarea(attrs={
                'rows': 3, 
                'placeholder': 'Optional: Share your experience...',
                'class': 'form-control'
            }),
        }