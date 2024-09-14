from django.urls import path

from . import views

urlpatterns = [
    path('classify/', views.classify_emails_view, name='classify_emails'),  # Map the classify view
]
