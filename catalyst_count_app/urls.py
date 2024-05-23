from django.urls import path
from . import views

from .views import CustomLoginView, SignUpView ,delete_user_by_id

urlpatterns = [
  path('uploaddata', views.csv_upload , name = "uploaddata"),
  path('Querybuilder/' , views.querybuilder , name = 'querybuilder'),
  path('userdata/' ,views.userdata , name = 'userdata'),
  path('accounts/login/', CustomLoginView.as_view(), name='account_login'),
  path('accounts/signup/', SignUpView.as_view(), name='account_signup'),
  path('delete_user/<int:user_id>/', delete_user_by_id, name='delete_user_by_id'),
]
    
