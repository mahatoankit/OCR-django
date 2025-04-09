from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from ocr.views import landing_page  # Import the view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('ocr/', include('ocr.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    
    # Landing page as the root URL
    path('', landing_page, name='landing_page'),  # This line adds the landing_page URL pattern
    path('login/', RedirectView.as_view(url='/accounts/login/', permanent=False)),
]

# Add static and media serving for development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)