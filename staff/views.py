from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404

from accounts.decorators import admin_required
from accounts.models import User
from .models import StaffProfile
from . import forms


@admin_required
def staff_list(request):
    users = User.objects.filter(
        role__in=['admin', 'class_teacher', 'subject_teacher']
    ).select_related('staff_profile').order_by('last_name')
    return render(request, 'staff/staff_list.html', {'staff': users})


@admin_required
def staff_detail(request, pk):
    user = get_object_or_404(User, pk=pk)
    profile, _ = StaffProfile.objects.get_or_create(user=user)
    return render(request, 'staff/staff_detail.html', {'member': user, 'profile': profile})


@admin_required
def staff_edit(request, pk):
    user = get_object_or_404(User, pk=pk)
    profile, _ = StaffProfile.objects.get_or_create(user=user)
    form = forms.StaffProfileForm(request.POST or None, instance=profile)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, f'{user.get_full_name()} profile updated.')
        return redirect('staff:detail', pk=pk)
    return render(request, 'staff/staff_form.html', {
        'form': form, 'member': user, 'title': f'Edit: {user.get_full_name()}'
    })
