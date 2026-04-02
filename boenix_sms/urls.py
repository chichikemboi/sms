from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('students/', include('students.urls')),
    path('exams/', include('exams.urls')),
    path('fees/', include('fees.urls')),
    path('attendance/', include('attendance.urls')),
    path('staff/', include('staff.urls')),
    path('inventory/', include('inventory.urls')),
    path('timetable/', include('timetable.urls')),
    path('lessons/', include('lessons.urls')),
    path('letters/', include('letters.urls')),
    path('', include('dashboard.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
