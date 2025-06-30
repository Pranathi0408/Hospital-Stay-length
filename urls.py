# predictor/urls.py
from django.urls import path
from . import views  # Importing views from the same directory

urlpatterns = [
    path('login/', views.login_view, name="login"),
    path('register/', views.register, name="register"),
    path('logout/', views.logout_view, name='logout_view'),
    path('predict_hospital_stay/', views.predict_hospital_stay, name="predict_hospital_stay"),
    path('home/', views.home, name="home"),
]


# In your urls.py
from django.conf import settings
from django.conf.urls.static import static



# Serve static files during development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
