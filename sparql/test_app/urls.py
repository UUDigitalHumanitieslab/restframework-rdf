from .views import UpdateView, QueryView
from rest_framework.urlpatterns import format_suffix_patterns
from django.urls import path

urlpatterns = format_suffix_patterns([
    path('test/query', QueryView.as_view()),
    path('test/update', UpdateView.as_view()),
])