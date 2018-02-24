from django.conf.urls import url

from .views import (
    SeleniumIndexView,
    SeleniumBrowserListView,
    SeleniumBrowserAddView,
    SeleniumTaskRunView,
)

urlpatterns = [
    url(r'^$', SeleniumIndexView.as_view(), name="index"),
    url(r'^browsers/.json$', SeleniumBrowserListView.as_view(),
        name="browser_list"),
    url(r'^browsers/add/.json$', SeleniumBrowserAddView.as_view(),
        name="add_browser"),
    url(r'^run/.json$', SeleniumTaskRunView.as_view(), name="run_task"),
]
