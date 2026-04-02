from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect


def root_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:home')
    return redirect('accounts:login')


@login_required
def home_view(request):
    user = request.user
    modules = user.dashboard_modules
    context = {
        'modules': modules,
        'user': user,
    }
    return render(request, 'dashboard/home.html', context)
