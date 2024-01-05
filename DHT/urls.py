from django.urls import path
from . import views
from . import api

urlpatterns = [
    path("receive/",views.receive_data,name='receive'),
    path("api/",api.dhtser,name='json'),
    path('download_csv/', views.download_csv, name='download_csv'),
    path('index/',views.index_view,name='index'),
    path('',views.table,name='table'),
    path('myChart/',views.graphique,name='myChart'),
    path('chart-data/',views.chart_data, name='chart-data'),
    path('chart-data-heure/',views.chart_data_heure,name='chart-data-jour'),
    path('chart-data-jour/',views.chart_data_jour,name='chart-data-semaine'),
    path('chart-data-mois/',views.chart_data_mois,name='chart-data-mois'),


]