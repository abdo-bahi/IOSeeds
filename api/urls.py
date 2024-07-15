from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import MCUViewSet,get_related_mcus , add_new_mcu, fields,read,login_view, index, sse_stream, auth_reset_pass,charts_morris,live, login, page_403, page_500, page_blank, register,settings,ui_forms,ui_tables


from .views import SensorDataViewSet, ActionViewSet

router = DefaultRouter()
router.register('sensordata', SensorDataViewSet)
router.register('actions', ActionViewSet)
router.register('mcu',MCUViewSet)


urlpatterns = [ 
    path('api/', include(router.urls)),
    path('api/mcu/<int:pk>/', MCUViewSet.as_view({'put': 'update'}), name='mcu-detail'),
    path('sensor-data-stream/<int:mcu_id>/', sse_stream, name='sse_stream'),
    # pages
    path('', index, name='index'),
    path('index/<int:mcu_id>/', index, name='index_with_mcu'),
    path('auth-reset-pass.html', auth_reset_pass, name='auth-reset-pass'), 
    path('charts-morris.html', charts_morris, name='charts-morris.html'), 
    path('live.html', live, name='live'), 
    path('login.html', login_view, name='login'), 
    path('page-403.html', page_403, name='page-403'), 
    path('page-500.html', page_500, name='page-500'), 
    path('page-blank.html', page_blank, name='page-blank'), 
    path('register.html', register, name='register'), 
    path('settings.html', settings, name='settings'), 
    path('ui-forms.html', ui_forms, name='ui-forms'),
    path('ui-forms.html/<int:mcu_id>/', ui_forms, name='ui_forms_with_mcu'), 
    path('ui-tables.html/<int:mcu_id>/', ui_tables, name='ui-tables'), 
    path('read/<int:year>/<int:month>/<int:day>/<int:mcu_id>/', read, name='read') ,
    path('fields.html/<int:mcu_id>/', fields,name='fields'),    
    path('get_related_mcus/<int:mcu_id>/', get_related_mcus, name='get_related_mcus') ,
    path('add_new_mcu/<int:mcu_id>/', add_new_mcu,name='add_new_mcu'),

]