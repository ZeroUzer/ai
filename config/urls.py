from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from shops.views import home

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('accounts/', include('accounts.urls')),
    path('shops/', include('shops.urls')),
    # Редирект с /shop/... на /shops/...
    path('shop/<path:path>/', RedirectView.as_view(url='/shops/%(path)s/', permanent=True)),
    path('ai/', include('ai_assistant.urls')),
    path('platform-admin/', include('platform_admin.urls')),
]