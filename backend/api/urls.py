from django.urls import path
from .views import (
    health, upload_csv, summary_latest, history, 
    report_latest, login_view, logout_view, dataset_latest_rows
)


urlpatterns = [
    path('health/', health),
    path('upload/', upload_csv),
    path('summary/latest/', summary_latest),
    path('history/', history),
    path('report/latest/', report_latest),
    path('auth/login/', login_view),
    path('auth/logout/', logout_view),
    path("dataset/latest/rows/", dataset_latest_rows),
]
