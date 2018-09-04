from django.conf.urls import patterns, url
from . import views

urlpatterns = [
    url(r"^heatmap/$", views.heatmap, name='ui_heatmap'),
    url(r"^geo_query/$", views.geo_query, name='ui_geo_query'),
    url(r"^ue/$", views.ue_info, name='ui_ue_info'),
    url(r"^ue/(?P<ue_id>\w+)/$", views.ue_detail, name="ui_ue_detail"),
    url(r"^$", views.static_view, name='home'),
]
