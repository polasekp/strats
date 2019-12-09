from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path("activities/", views.ActivitiesView.as_view(), name="activities"),
]
