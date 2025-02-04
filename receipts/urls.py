from django.urls import path

from . import views

app_name = "receipts"
urlpatterns = [
    # ex: /receipts/
    path("", views.get_receipt, name="get_receipt"),

    # ex: /receipts/process/
    path("process", views.get_id_for_receipt, name="get_id_for_receipt"),

    # ex: /receipts/{id}/
    # path("<int:pk>/", views.DetailView.as_view(), name="detail")
]