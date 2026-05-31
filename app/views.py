from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Count, Avg, Max, Min, Sum, Q, RestrictedError
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from .models import Product, Category, SKU, Stock, Location, Color, Size, Order, OrderItem, Customer
from .forms import (
    ProductForm, SearchForm, CategoryForm, ColorForm, SizeForm, SKUForm,
    LocationForm, StockForm, OrderForm, SKUFormSet, CustomerForm, OrderItemFormSet
)


# ─────────────────────────────────────────────────────────────
# 1. PRODUITS (avec SKU en ligne)
# ─────────────────────────────────────────────────────────────
class ProductListView(ListView):
    model = Product
    template_name = 'products/list.html'
    context_object_name = 'products'
    ordering = ['name']

    def get_queryset(self):
        queryset = super().get_queryset().select_related('category')
        # 'none' is a sentinel for "products without category"; strip it before form validation
        get_data = self.request.GET.copy() if self.request.GET else None
        category_none = bool(get_data and get_data.get('category') == 'none')
        if category_none:
            get_data = get_data.copy()
            get_data['category'] = ''
        self.form = SearchForm(get_data or None)
        if self.form.is_valid():
            keyword   = self.form.cleaned_data.get('keyword')
            category  = self.form.cleaned_data.get('category')
            min_price = self.form.cleaned_data.get('min_price')
            max_price = self.form.cleaned_data.get('max_price')
            if keyword:
                queryset = queryset.filter(Q(name__icontains=keyword) | Q(description__icontains=keyword))
            if category_none:
                queryset = queryset.filter(category__isnull=True)
            elif category:
                queryset = queryset.filter(category=category)
            if min_price:
                queryset = queryset.filter(price__gte=min_price)
            if max_price:
                queryset = queryset.filter(price__lte=max_price)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.form
        context['total'] = self.object_list.count()
        context['keyword'] = self.request.GET.get('keyword', '')
        return context


class ProductDetailView(DetailView):
    model = Product
    template_name = 'products/detail.html'
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.object
        context['skus'] = SKU.objects.filter(product=product).select_related('size', 'color').prefetch_related('stock_set__location')
        context['total_stock'] = Stock.objects.filter(sku__product=product).aggregate(total=Sum('quantity'))['total'] or 0
        return context


class ProductCreateUpdateMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['sku_formset'] = SKUFormSet(self.request.POST, instance=self.object)
        else:
            context['sku_formset'] = SKUFormSet(instance=self.object)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        sku_formset = context['sku_formset']
        if form.is_valid() and sku_formset.is_valid():
            self.object = form.save()
            sku_formset.instance = self.object
            sku_formset.save()
            return HttpResponseRedirect(self.get_success_url())
        return self.render_to_response(self.get_context_data(form=form))


class ProductCreateView(SuccessMessageMixin, ProductCreateUpdateMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'products/product_form.html'
    success_message = '✅ Produit "%(name)s" ajouté avec succès !'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Ajouter un produit'
        context['btn_label'] = 'Ajouter'
        context['back_url'] = reverse_lazy('product_list')
        return context

    def get_success_url(self):
        return reverse_lazy('product_detail', kwargs={'pk': self.object.pk})


class ProductUpdateView(SuccessMessageMixin, ProductCreateUpdateMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'products/product_form.html'
    success_message = '✅ Produit "%(name)s" modifié avec succès !'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Modifier — {self.object.name}'
        context['btn_label'] = 'Enregistrer'
        context['back_url'] = reverse_lazy('product_detail', kwargs={'pk': self.object.pk})
        return context

    def get_success_url(self):
        return reverse_lazy('product_detail', kwargs={'pk': self.object.pk})


class ProductDeleteView(DeleteView):
    model = Product
    template_name = 'products/confirm_delete.html'
    success_url = reverse_lazy('product_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cancel_url'] = reverse_lazy('product_detail', kwargs={'pk': self.object.pk})
        return context

    def post(self, request, *args, **kwargs):
        try:
            return super().post(request, *args, **kwargs)
        except RestrictedError:
            product = self.get_object()
            messages.error(
                request,
                f'❌ Impossible de supprimer "{product.name}" : '
                f'il est référencé dans des commandes existantes.'
            )
            return HttpResponseRedirect(
                reverse_lazy('product_detail', kwargs={'pk': product.pk})
            )

    def delete(self, request, *args, **kwargs):
        product = self.get_object()
        messages.success(request, f'🗑️ Produit "{product.name}" supprimé.')
        return super().delete(request, *args, **kwargs)


# ─────────────────────────────────────────────────────────────
# 2. CATÉGORIES
# ─────────────────────────────────────────────────────────────
class CategoryListView(ListView):
    model = Category
    template_name = 'products/category_list.html'
    context_object_name = 'categories'

    def get_queryset(self):
        return super().get_queryset().annotate(nb_products=Count('products')).order_by('name')


class CategoryCreateView(SuccessMessageMixin, CreateView):
    model = Category
    form_class = CategoryForm
    template_name = 'products/form.html'
    success_url = reverse_lazy('category_list')
    success_message = '✅ Catégorie "%(name)s" ajoutée !'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Ajouter une catégorie'
        context['btn_label'] = 'Ajouter'
        context['back_url'] = reverse_lazy('category_list')
        return context


class CategoryUpdateView(SuccessMessageMixin, UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = 'products/form.html'
    success_url = reverse_lazy('category_list')
    success_message = '✅ Catégorie "%(name)s" modifiée !'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Modifier — {self.object.name}'
        context['btn_label'] = 'Enregistrer'
        context['back_url'] = reverse_lazy('category_list')
        return context


class CategoryDeleteView(DeleteView):
    model = Category
    template_name = 'products/confirm_delete.html'
    success_url = reverse_lazy('category_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cancel_url'] = reverse_lazy('category_list')
        return context

    def delete(self, request, *args, **kwargs):
        cat = self.get_object()
        messages.success(request, f'🗑️ Catégorie "{cat.name}" supprimée.')
        return super().delete(request, *args, **kwargs)


# ─────────────────────────────────────────────────────────────
# 3. LOCATIONS
# ─────────────────────────────────────────────────────────────
class LocationListView(ListView):
    model = Location
    template_name = 'products/location_list.html'
    context_object_name = 'locations'


class LocationCreateView(SuccessMessageMixin, CreateView):
    model = Location
    form_class = LocationForm
    template_name = 'products/form.html'
    success_url = reverse_lazy('location_list')
    success_message = '✅ Lieu "%(name)s" ajouté !'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Ajouter un lieu'
        context['btn_label'] = 'Ajouter'
        context['back_url'] = reverse_lazy('location_list')
        return context


class LocationUpdateView(SuccessMessageMixin, UpdateView):
    model = Location
    form_class = LocationForm
    template_name = 'products/form.html'
    success_url = reverse_lazy('location_list')
    success_message = '✅ Lieu "%(name)s" modifié !'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Modifier un lieu'
        context['btn_label'] = 'Enregistrer'
        context['back_url'] = reverse_lazy('location_list')
        return context


class LocationDeleteView(DeleteView):
    model = Location
    template_name = 'products/confirm_delete.html'
    success_url = reverse_lazy('location_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cancel_url'] = reverse_lazy('location_list')
        return context

    def delete(self, request, *args, **kwargs):
        location = self.get_object()
        messages.success(request, f'🗑️ Lieu "{location.name}" supprimé.')
        return super().delete(request, *args, **kwargs)


# ─────────────────────────────────────────────────────────────
# 4. COLORS & SIZES
# ─────────────────────────────────────────────────────────────
class ColorListView(ListView):
    model = Color
    template_name = 'products/color_list.html'
    context_object_name = 'colors'


class ColorCreateView(SuccessMessageMixin, CreateView):
    model = Color
    form_class = ColorForm
    template_name = 'products/form.html'
    success_url = reverse_lazy('color_list')
    success_message = '✅ Couleur "%(name)s" ajoutée !'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Ajouter une couleur'
        context['btn_label'] = 'Ajouter'
        context['back_url'] = reverse_lazy('color_list')
        return context


class ColorUpdateView(SuccessMessageMixin, UpdateView):
    model = Color
    form_class = ColorForm
    template_name = 'products/form.html'
    success_url = reverse_lazy('color_list')
    success_message = '✅ Couleur "%(name)s" modifiée !'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Modifier une couleur'
        context['btn_label'] = 'Enregistrer'
        context['back_url'] = reverse_lazy('color_list')
        return context


class ColorDeleteView(DeleteView):
    model = Color
    template_name = 'products/confirm_delete.html'
    success_url = reverse_lazy('color_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cancel_url'] = reverse_lazy('color_list')
        return context

    def delete(self, request, *args, **kwargs):
        color = self.get_object()
        messages.success(request, f'🗑️ Couleur "{color.name}" supprimée.')
        return super().delete(request, *args, **kwargs)


class SizeListView(ListView):
    model = Size
    template_name = 'products/size_list.html'
    context_object_name = 'sizes'


class SizeCreateView(SuccessMessageMixin, CreateView):
    model = Size
    form_class = SizeForm
    template_name = 'products/form.html'
    success_url = reverse_lazy('size_list')
    success_message = '✅ Taille "%(name)s" ajoutée !'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Ajouter une taille'
        context['btn_label'] = 'Ajouter'
        context['back_url'] = reverse_lazy('size_list')
        return context


class SizeUpdateView(SuccessMessageMixin, UpdateView):
    model = Size
    form_class = SizeForm
    template_name = 'products/form.html'
    success_url = reverse_lazy('size_list')
    success_message = '✅ Taille "%(name)s" modifiée !'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Modifier une taille'
        context['btn_label'] = 'Enregistrer'
        context['back_url'] = reverse_lazy('size_list')
        return context


class SizeDeleteView(DeleteView):
    model = Size
    template_name = 'products/confirm_delete.html'
    success_url = reverse_lazy('size_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cancel_url'] = reverse_lazy('size_list')
        return context

    def delete(self, request, *args, **kwargs):
        size = self.get_object()
        messages.success(request, f'🗑️ Taille "{size.name}" supprimée.')
        return super().delete(request, *args, **kwargs)


# ─────────────────────────────────────────────────────────────
# 5. SKU
# ─────────────────────────────────────────────────────────────
class SKUListView(ListView):
    model = SKU
    template_name = 'products/sku_list.html'
    context_object_name = 'skus'

    def get_queryset(self):
        return super().get_queryset().select_related('product', 'size', 'color')


class SKUCreateView(SuccessMessageMixin, CreateView):
    model = SKU
    form_class = SKUForm
    template_name = 'products/form.html'
    success_url = reverse_lazy('sku_list')
    success_message = '✅ SKU ajouté !'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Ajouter un SKU'
        context['btn_label'] = 'Ajouter'
        context['back_url'] = reverse_lazy('sku_list')
        return context


class SKUUpdateView(SuccessMessageMixin, UpdateView):
    model = SKU
    form_class = SKUForm
    template_name = 'products/form.html'
    success_url = reverse_lazy('sku_list')
    success_message = '✅ SKU modifié !'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Modifier SKU — {self.object}'
        context['btn_label'] = 'Enregistrer'
        context['back_url'] = reverse_lazy('sku_list')
        return context


class SKUDeleteView(DeleteView):
    model = SKU
    template_name = 'products/confirm_delete.html'
    success_url = reverse_lazy('sku_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cancel_url'] = reverse_lazy('sku_list')
        return context

    def delete(self, request, *args, **kwargs):
        sku = self.get_object()
        messages.success(request, f'🗑️ SKU "{sku}" supprimé.')
        return super().delete(request, *args, **kwargs)


# ─────────────────────────────────────────────────────────────
# 6. STOCK
# ─────────────────────────────────────────────────────────────
class StockListView(ListView):
    model = Stock
    template_name = 'products/stock_list.html'
    context_object_name = 'stocks'

    def get_queryset(self):
        queryset = super().get_queryset().select_related('sku__product', 'sku__size', 'sku__color', 'location')
        q = self.request.GET.get('q')
        if q:
            if q.isdigit():
                queryset = queryset.filter(Q(sku__id=q) | Q(sku__product__name__icontains=q))
            else:
                queryset = queryset.filter(sku__product__name__icontains=q)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['q'] = self.request.GET.get('q', '')
        return context


class StockCreateView(SuccessMessageMixin, CreateView):
    model = Stock
    form_class = StockForm
    template_name = 'products/form.html'
    success_message = '✅ Stock ajouté !'

    def get_initial(self):
        initial = super().get_initial()
        sku_pk = self.request.GET.get('sku')
        if sku_pk:
            initial['sku'] = sku_pk
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Ajouter un stock'
        context['btn_label'] = 'Enregistrer'
        context['back_url'] = self.request.GET.get('next') or reverse_lazy('stock_list')
        return context

    def get_success_url(self):
        return self.request.GET.get('next') or reverse_lazy('stock_list')


class StockUpdateView(SuccessMessageMixin, UpdateView):
    model = Stock
    form_class = StockForm
    template_name = 'products/form.html'
    success_message = '✅ Stock modifié !'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Modifier un stock'
        context['btn_label'] = 'Enregistrer'
        context['back_url'] = self.request.GET.get('next') or reverse_lazy('stock_list')
        return context

    def get_success_url(self):
        return self.request.GET.get('next') or reverse_lazy('stock_list')


class StockDeleteView(DeleteView):
    model = Stock
    template_name = 'products/confirm_delete.html'
    success_url = reverse_lazy('stock_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cancel_url'] = reverse_lazy('stock_list')
        return context

    def delete(self, request, *args, **kwargs):
        stock = self.get_object()
        messages.success(request, f'🗑️ Stock "{stock}" supprimé.')
        return super().delete(request, *args, **kwargs)


# ─────────────────────────────────────────────────────────────
# 7. ORDERS
# ─────────────────────────────────────────────────────────────
class OrderFormMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['item_formset'] = OrderItemFormSet(self.request.POST, instance=self.object, prefix='items')
        else:
            context['item_formset'] = OrderItemFormSet(instance=self.object, prefix='items')
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        item_formset = context['item_formset']
        if form.is_valid() and item_formset.is_valid():
            self.object = form.save()
            item_formset.instance = self.object
            item_formset.save()
            return HttpResponseRedirect(self.get_success_url())
        return self.render_to_response(self.get_context_data(form=form))


class OrderListView(ListView):
    model = Order
    template_name = 'products/order_list.html'
    context_object_name = 'orders'
    ordering = ['-created_at']

    def get_queryset(self):
        return super().get_queryset().select_related('customer', 'location')


class OrderDetailView(DetailView):
    model = Order
    template_name = 'products/order_detail.html'
    context_object_name = 'order'

    def get_queryset(self):
        return super().get_queryset().select_related('customer', 'location').prefetch_related(
            'items__sku__product',
            'items__sku__size',
            'items__sku__color',
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        items_with_total = []
        order_total = 0
        for item in self.object.items.all():
            line_total = item.price * item.quantity
            items_with_total.append({'item': item, 'line_total': line_total})
            order_total += line_total
        context['items_with_total'] = items_with_total
        context['order_total'] = order_total
        return context


class OrderCreateView(SuccessMessageMixin, OrderFormMixin, CreateView):
    model = Order
    form_class = OrderForm
    template_name = 'products/order_form.html'
    success_url = reverse_lazy('order_list')
    success_message = '✅ Commande créée avec succès !'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Créer une commande'
        context['btn_label'] = 'Commander'
        context['back_url'] = reverse_lazy('order_list')
        return context


class OrderUpdateView(SuccessMessageMixin, OrderFormMixin, UpdateView):
    model = Order
    form_class = OrderForm
    template_name = 'products/order_form.html'
    success_message = '✅ Commande modifiée !'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Modifier commande #{self.object.pk}'
        context['btn_label'] = 'Enregistrer'
        context['back_url'] = reverse_lazy('order_detail', kwargs={'pk': self.object.pk})
        return context

    def get_success_url(self):
        return reverse_lazy('order_detail', kwargs={'pk': self.object.pk})


class OrderDeleteView(DeleteView):
    model = Order
    template_name = 'products/confirm_delete.html'
    success_url = reverse_lazy('order_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cancel_url'] = reverse_lazy('order_detail', kwargs={'pk': self.object.pk})
        return context

    def delete(self, request, *args, **kwargs):
        order = self.get_object()
        messages.success(request, f'🗑️ Commande #{order.pk} supprimée.')
        return super().delete(request, *args, **kwargs)


# ─────────────────────────────────────────────────────────────
# 8. CUSTOMERS
# ─────────────────────────────────────────────────────────────
class CustomerListView(ListView):
    model = Customer
    template_name = 'products/customer_list.html'
    context_object_name = 'customers'
    ordering = ['lastname', 'firstname']


class CustomerCreateView(SuccessMessageMixin, CreateView):
    model = Customer
    form_class = CustomerForm
    template_name = 'products/form.html'
    success_url = reverse_lazy('customer_list')
    success_message = '✅ Client "%(firstname)s %(lastname)s" ajouté !'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Ajouter un client'
        context['btn_label'] = 'Ajouter'
        context['back_url'] = reverse_lazy('customer_list')
        return context


class CustomerUpdateView(SuccessMessageMixin, UpdateView):
    model = Customer
    form_class = CustomerForm
    template_name = 'products/form.html'
    success_url = reverse_lazy('customer_list')
    success_message = '✅ Client "%(firstname)s %(lastname)s" modifié !'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Modifier client — {self.object}'
        context['btn_label'] = 'Enregistrer'
        context['back_url'] = reverse_lazy('customer_list')
        return context


class CustomerDeleteView(DeleteView):
    model = Customer
    template_name = 'products/confirm_delete.html'
    success_url = reverse_lazy('customer_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cancel_url'] = reverse_lazy('customer_list')
        return context

    def delete(self, request, *args, **kwargs):
        customer = self.get_object()
        messages.success(request, f'🗑️ Client "{customer}" supprimé.')
        return super().delete(request, *args, **kwargs)


# ─────────────────────────────────────────────────────────────
# 9. STATISTIQUES & CLASSEMENT
# ─────────────────────────────────────────────────────────────
class StatsView(TemplateView):
    template_name = 'products/stats.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['by_category'] = Category.objects.annotate(
            nb_products=Count('products')
        ).filter(nb_products__gt=0).order_by('-nb_products')
        context['nb_uncategorized'] = Product.objects.filter(category__isnull=True).count()

        context['global_stats'] = Product.objects.aggregate(
            avg_price=Avg('price'),
            max_price=Max('price'),
            min_price=Min('price'),
            total_products=Count('id'),
        )

        context['top_products'] = Product.objects.select_related('category').order_by('-price')[:5]

        RICH_THRESHOLD = 200
        context['rich_threshold'] = RICH_THRESHOLD
        context['rich_categories'] = Category.objects.annotate(
            sum_price=Sum('products__price')
        ).filter(sum_price__gt=RICH_THRESHOLD).order_by('-sum_price')

        avg_price = context['global_stats']['avg_price'] or 0
        context['avg_price'] = avg_price
        context['above_avg'] = Product.objects.filter(price__gt=avg_price).count()

        return context
