from django.urls import path
from .views import *

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("userdata/", GetUsersView.as_view(), name="get_users"),
    path("download-users/", DownloadUsersPDFView.as_view(), name="download_users_pdf"),
    path("logout/", Logout.as_view()),
]
