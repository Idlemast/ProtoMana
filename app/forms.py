from django import forms
from .models import Product, Category, Color, Size, SKU, Location, Stock, Order, OrderItem, Customer
from django.forms import inlineformset_factory

class TailwindFormMixin:
    """Mixin to add Tailwind CSS classes to form fields."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            tailwind_classes = 'block w-full rounded-xl border-gray-200 bg-gray-50 px-4 py-3 text-gray-900 outline-none focus:bg-white focus:ring-2 focus:ring-blue-500 transition-all sm:text-sm'
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs['class'] = 'h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-600'
            elif isinstance(field.widget, (forms.Select, forms.SelectMultiple)):
                field.widget.attrs['class'] = tailwind_classes + ' appearance-none'
            else:
                field.widget.attrs['class'] = tailwind_classes

class ProductForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'category', 'description', 'price']
        labels = {
            'name': 'Nom',
            'category': 'Catégorie',
            'description': 'Description',
            'price': 'Prix (€)',
        }

class CategoryForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'parent']
        labels = {
            'name': 'Nom de la catégorie',
            'parent': 'Catégorie parente (optionnel)',
        }

class SKUForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = SKU
        fields = ['product', 'size', 'color']
        labels = {
            'product': 'Produit',
            'size': 'Taille',
            'color': 'Couleur',
        }

class SKUInlineForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = SKU
        fields = ['size', 'color']
        labels = {'size': 'Taille', 'color': 'Couleur'}

SKUFormSet = inlineformset_factory(
    Product, SKU,
    form=SKUInlineForm,
    extra=1,
    can_delete=True,
)

class SearchForm(TailwindFormMixin, forms.Form):
    keyword = forms.CharField(
        required=False,
        label="Mot-clé",
        widget=forms.TextInput(attrs={'placeholder': '🔍 Rechercher...'})
    )
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        empty_label='Toutes les catégories'
    )
    min_price = forms.DecimalField(required=False, min_value=0, label="Prix min")
    max_price = forms.DecimalField(required=False, min_value=0, label="Prix max")

    def clean(self):
        cleaned_data = super().clean()
        min_p = cleaned_data.get('min_price')
        max_p = cleaned_data.get('max_price')
        if min_p is not None and max_p is not None and min_p > max_p:
            raise forms.ValidationError("Le prix minimum ne peut pas être supérieur au prix maximum.")
        return cleaned_data

class ColorForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = Color
        fields = ['name']
        labels = {'name': 'Nom de la couleur'}

class SizeForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = Size
        fields = ['name']
        labels = {'name': 'Taille (ex: XL, 42)'}

class LocationForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = Location
        fields = ['name', 'type', 'address']
        labels = {
            'name': 'Nom du lieu',
            'type': 'Type',
            'address': 'Adresse',
        }

class StockForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = Stock
        fields = ['location', 'sku', 'quantity']
        labels = {
            'location': 'Lieu de stockage',
            'sku': 'Variante (SKU)',
            'quantity': 'Quantité',
        }

class OrderForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = Order
        fields = ['customer', 'location', 'status']
        labels = {
            'customer': 'Client',
            'location': 'Lieu de vente',
            'status': 'Statut',
        }

class OrderItemForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = OrderItem
        fields = ['sku', 'quantity', 'price']
        labels = {
            'sku': 'Variante (SKU)',
            'quantity': 'Quantité',
            'price': 'Prix unitaire (€)',
        }

OrderItemFormSet = inlineformset_factory(
    Order, OrderItem,
    form=OrderItemForm,
    extra=1,
    can_delete=True,
)

class CustomerForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['firstname', 'lastname', 'email']
        labels = {
            'firstname': 'Prénom',
            'lastname': 'Nom',
            'email': 'Email',
        }
