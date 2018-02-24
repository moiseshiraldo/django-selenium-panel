import json

from collections import OrderedDict
from celery import current_app as celery_app

from django.views.generic import View
from django.views.generic.base import TemplateView
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.core.urlresolvers import reverse
from django.http import JsonResponse
from django.conf import settings
from django.shortcuts import get_object_or_404

from .models import Browser


class SeleniumIndexView(TemplateView):
    http_method_names = ('get',)
    template_name = 'selenium_panel/browsers_list.html'

    def get_context_data(self, **kwargs):
        context = super(SeleniumIndexView, self).get_context_data(**kwargs)
        context['config'] = json.dumps({
            'urls': {
                'browser_list': reverse("selenium_panel:browser_list"),
                'run_task': reverse("selenium_panel:run_task"),
            },
            'tasks': self.get_tasks(),
            'servers': settings.SELENIUM['SERVERS'],
        })
        return context

    def get_tasks(self):
        celery_app.loader.import_default_modules()
        tasks = OrderedDict()
        for (task, name) in settings.SELENIUM['TASKS']:
            task_class = type(celery_app.tasks[task])
            parents = []
            parent_class = task_class.__bases__[0]
            while parent_class.name != 'selenium.base_task':
                parents.append(parent_class.name)
                parent_class = parent_class.__bases__[0]
            parents.reverse()
            tasks[task] = {
                'name': name,
                'config': task_class.SELENIUM_CONFIG,
                'parents': parents,
            }
        return tasks


class SeleniumBrowserListView(View):

    def get(self, request):
        browsers = {}
        for browser in Browser.objects.iterator():
            browsers[browser.service_url] = browser.as_dict()
        return JsonResponse(browsers, safe=False)


class SeleniumTaskRunView(View):
    http_method_names = ('post',)

    def post(self, request):
        celery_app.loader.import_default_modules()
        data = json.loads(request.body)
        task = celery_app.tasks[data.pop('task')]
        browser = get_object_or_404(Browser, service_url=data['service_url'])
        data['session_id'] = browser.session_id
        result = task.delay(**data)
        browser.running_task = result.task_id
        browser.save(update_fields=["running_task"])
        return JsonResponse(browser.as_dict(), safe=False, status=201)


class SeleniumBrowserAddView(View):
    http_method_names = ('post',)
    required_fields = ('service_url', 'session_id', 'driver', 'username')

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(SeleniumBrowserAddView, self).dispatch(
            request, *args, **kwargs)

    def has_required_fields(self, data):
        return all([data.get(f) for f in self.required_fields])

    def post(self, request):
        data = json.loads(request.body)
        if not self.has_required_fields(data):
            error_message = "{} are required.".format(
                ", ".join(self.required_fields)
            )
            return JsonResponse(
                {'detail': error_message}, safe=False, status=400
            )
        remote_ip = request.META.get('REMOTE_ADDR')
        data['service_url'] = "http://{}:{}".format(
            remote_ip, data['service_url'].split(':')[2]
        )
        browser = Browser.objects.create(**data)
        return JsonResponse(browser.as_dict(), safe=False, status=201)
