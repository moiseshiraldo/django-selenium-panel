from django.conf.urls import include, url

urlpatterns = [
    url(r'^selenium/',
        include('selenium_panel.urls', namespace='selenium_panel')),
]
