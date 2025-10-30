from django.urls import path

from . import views


urlpatterns = [
    path("", views.index, name="timers"),
    path("add/", views.timer_add, name="timer_add"),
    path("detail/<int:timer_id>/", views.timer_detail, name="timer_detail")
]
