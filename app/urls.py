from django.urls import path
from . import views

urlpatterns=[
    path('',views.index,name='index'),
    path('cal/',views.cal,name='cal'),
    path('cal/add/',views.newcal,name='newcal'),
    path('cal/details/<int:tk>/',views.calview,name='caledit'),
    path('cal/edit/<int:tk>/',views.caledit,name='caledit'),
    path('cal/stdins/',views.stdins,name='stdins'),
    path('cal/stdins/add/',views.stdinsadd,name='stdins'),
    path('cal/stdins/view/<int:id>/',views.stdinsview,name='stdins'),
    path('cems/',views.cems,name='cems'),
    path('cems/add/',views.cemsadd,name='add'),
    path('cems/details/<int:id>/',views.cemsdetails,name='details'),
    path('cems/edit/<int:id>/',views.cemsedit,name='edit'),
    path('gallery/',views.gallery,name='gallery'),
    path('gallery/delete/<int:id>/',views.gallerydelete,name='gallery'),
    path('interpolations',views.interpol,name='interpolations'),
    path('manual/',views.manual,name='manual'),
    path('manual/view/<int:id>/',views.manual_view,name='manual_view'),
    path('manuals/delete/<int:id>/',views.manualdelete,name='manual'),



    path('users/',views.users,name='users'),
    path('users/add/',views.newusers,name='newusers'),
    path('users/details/<str:username>/',views.userdetails,name='details'),
    path('users/self/',views.userself,name='userself'),

    path('accounts/login/',views.acclog,name='acclog'),
    path('login',views.signin,name='login'),
    path('password-reset/<str:username>/',views.adminPasswordReset,name='password-reset'),
    path('logout/',views.signout,name='logout'),
    path('password_reset_request/',views.resetRequest,name='resetRequest'),

    path('safety_moment/',views.safety_moment,name='safety_moment'), 
    path('safety_moment/add/',views.safety_moment_add,name='safety_moment_add'), 

    path('todo/',views.todo,name='todo'),
    path('todo/add/',views.todo_add,name='todo'),
    path('reports/',views.reports,name='report'),
    path('reports/add/',views.report_add,name='report-add'),
    path('reports/view/<int:id>/',views.report_view,name='report-view'),
    path('reports/edit/<int:id>/',views.report_edit,name='report-edit'),
     
    path('test',views.test,name='test'),
]
from django.conf import settings
from django.conf.urls.static import static

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)