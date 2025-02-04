from django.urls import path

from . import views

urlpatterns = [
    # ex: /receipts/process/
    path("process", views.get_id_for_receipt, name="get_id_for_receipt"),

    # ex: /receipts/{id}/
    # path("<int:pk>/", views.DetailView.as_view(), name="detail"),
]