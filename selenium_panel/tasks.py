from celery.task import Task
from selenium.webdriver.common.by import By

from django.conf import settings

from selenium_panel.webdriver import RemoteWebDriver

import time


class SeleniumRemoteTask(Task):
    name = "selenium.base_task"
    SELENIUM_CONFIG = {}

    def run(self, *args, **kwargs):
        self.browser = RemoteWebDriver(
            command_executor=kwargs.pop('service_url'),
            session_id=kwargs.pop('session_id'),
        )
        self.server = settings.SELENIUM['SERVERS'][
            kwargs.pop('server')]['address']
        self.username = kwargs.pop('username', "")
        self.password = kwargs.pop('password', "")
        self.run_selenium_task(*args, **kwargs)

    def run_selenium_task(self, *args, **kwargs):
        pass


class GoogleSearchTask(SeleniumRemoteTask):
    name = "selenium.google_search"
    SELENIUM_CONFIG = {
        'arguments': {
            'words': {
                'name': "Words",
                'required': True,
            }
        }
    }

    def run_selenium_task(self, *args, **kwargs):
        words = kwargs['arguments']['words']
        self.browser.get(self.server)
        search_input = self.browser.find_element_by_name("q")
        search_input.send_keys(words)
        search_input.submit()
        time.sleep(2)
        return {
            'search_url': self.browser.current_url
        }


class OpenGoogleResultTask(GoogleSearchTask):
    name = "selenium.open_google_result"
    SELENIUM_CONFIG = {
        'arguments': {
            'search_url': {
                'name': "Search URL",
                'required': True,
                'from_parent': True,
            },
            'result': {
                'name': "Result number",
                'required': True,
            }
        }
    }

    def run_selenium_task(self, *args, **kwargs):
        if 'selenium.google_search' in kwargs['parents']:
            super(OpenGoogleResultTask, self).run_selenium_task(
                *args, **kwargs)
        else:
            self.browser.get(kwargs['arguments']['search_url'])
            time.sleep(2)
        results = self.browser.find_elements_by_class_name("g")
        result = results[int(kwargs['arguments']['result'])]
        result.find_element(By.XPATH, './/a').click()
