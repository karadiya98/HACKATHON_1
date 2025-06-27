from django.contrib import admin # type: ignore
from django.urls import path # type: ignore
from .views import home,DATA,signup,login,about_logout,logout,predict_csv,userdata_view,login_view,download_predicted_csv


urlpatterns = [
    path('admin/', admin.site.urls),
    path('',home,name='home'),
    #path('HOME',HOME,name='HOME1'),
    path('DATA',DATA,name='DATA'),
    path('signup',signup,name='signup'),
    path('login',login_view,name='login'),
    path('about',about_logout,name='login'),
    path('datainserted',userdata_view,name='datainserted'),
    path('logout',logout,name='logout'),
    path('HOME',predict_csv, name='predict_csv'),
    
    path('download_predicted_csv',download_predicted_csv, name='download_predicted_csv'),
]
