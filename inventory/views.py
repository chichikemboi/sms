from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q

from accounts.decorators import admin_required
from .models import InventoryItem, InventoryCategory
from .forms import InventoryItemForm


@admin_required
def inventory_list(request):
    items = InventoryItem.objects.select_related('category').all()
    q = request.GET.get('q', '')
    category = request.GET.get('category', '')
    condition = request.GET.get('condition', '')
    if q:
        items = items.filter(Q(name__icontains=q) | Q(location__icontains=q))
    if category:
        items = items.filter(category_id=category)
    if condition:
        items = items.filter(condition=condition)
    categories = InventoryCategory.objects.all()
    return render(request, 'inventory/inventory_list.html', {
        'items': items, 'categories': categories,
        'q': q, 'sel_category': category, 'sel_condition': condition,
        'condition_choices': InventoryItem.CONDITION_CHOICES,
    })


@admin_required
def item_create(request):
    form = InventoryItemForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        item = form.save()
        messages.success(request, f'"{item.name}" added to inventory.')
        return redirect('inventory:list')
    return render(request, 'inventory/item_form.html', {'form': form, 'title': 'Add Item'})


@admin_required
def item_edit(request, pk):
    item = get_object_or_404(InventoryItem, pk=pk)
    form = InventoryItemForm(request.POST or None, instance=item)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, f'"{item.name}" updated.')
        return redirect('inventory:list')
    return render(request, 'inventory/item_form.html', {'form': form, 'title': f'Edit: {item.name}', 'item': item})


@admin_required
def item_delete(request, pk):
    item = get_object_or_404(InventoryItem, pk=pk)
    if request.method == 'POST':
        name = item.name
        item.delete()
        messages.success(request, f'"{name}" removed from inventory.')
    return redirect('inventory:list')
