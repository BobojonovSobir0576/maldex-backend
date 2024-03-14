from django import forms
from ckeditor.widgets import CKEditorWidget
from apps.product.models import Products, ProductCategories
from django.utils.translation import gettext_lazy as _


class ProductAdminForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditorWidget())
    dimensions_length = forms.IntegerField(label='Размеры Длина', min_value=0)
    dimensions_width = forms.IntegerField(label='Размеры Ширина', min_value=0)
    dimensions_height = forms.IntegerField(label='Размеры Высота', min_value=0)
    package_dimensions_length = forms.IntegerField(label='Размеры упаковки Длина', min_value=0)
    package_dimensions_width = forms.IntegerField(label='Размеры упаковки Ширина', min_value=0)
    package_dimensions_height = forms.IntegerField(label='Размеры упаковки Высота', min_value=0)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.dimensions:
            try:
                length, width, height = self.instance.dimensions.split('x')
                self.fields['dimensions_length'].initial = length
                self.fields['dimensions_width'].initial = width
                self.fields['dimensions_height'].initial = height
            except ValueError:
                pass

        if self.instance.package_dimensions:
            try:
                length, width, height = self.instance.package_dimensions.split('x')
                self.fields['package_dimensions_length'].initial = length
                self.fields['package_dimensions_width'].initial = width
                self.fields['package_dimensions_height'].initial = height
            except ValueError:
                pass

    def save(self, commit=True):
        self.instance.dimensions = f"{self.cleaned_data['dimensions_length']}x{self.cleaned_data['dimensions_width']}x{self.cleaned_data['dimensions_height']}"
        self.instance.package_dimensions = f"{self.cleaned_data['package_dimensions_length']}x{self.cleaned_data['package_dimensions_width']}x{self.cleaned_data['package_dimensions_height']}"
        return super().save(commit=commit)


    class Meta:
        model = Products
        fields = "__all__"


