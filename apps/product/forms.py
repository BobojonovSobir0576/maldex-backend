from django import forms
from ckeditor.widgets import CKEditorWidget
from apps.product.models import Products


class ProductAdminForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditorWidget())

    class Meta:
        model = Products
        fields = '__all__'
