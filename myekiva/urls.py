from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('admin/', admin.site.urls),

    # JWT Auth endpoints
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Include app routes
    path('api/', include('users.urls')),  # or your router url
    path('api/', include('schools.urls')),
    path('api/', include('subjects.urls')),  # or your router url
    path('api/', include('content.urls')),
]
