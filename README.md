# Django Selenium Panel

[![Build Status](https://travis-ci.org/moiseshiraldo/django-selenium-panel.svg?branch=master)](https://travis-ci.org/moiseshiraldo/django-selenium-panel)
[![Test coverage status](https://codecov.io/gh/moiseshiraldo/django-selenium-panel/branch/master/graph/badge.svg)](https://codecov.io/gh/moiseshiraldo/django-selenium-panel)

A Django web panel to control the execution of Selenium automated tests on browsers running within the local network.

## Installation

`$ pip install -e git+https://github.com/moiseshiraldo/django-selenium-panel#egg=selenium_panel`

## Configuration

Add `selenium_panel` to your `INSTALLED_APPS` settings:

```python
INSTALLED_APPS = (
    # ...
    'selenium_panel',
)
```

Add the Selenium Panel's URLs to your project’s URLconf:

```python
urlpatterns = [
    # ...
    url(r'^selenium/', include('selenium_panel.urls', namespace='selenium_panel')),
]
```

You should be able to access the Selenium Panel by running your server and going to `/selenium/`.

### Connecting a browser

First, download the driver for the browser you want to use (you can find the links [here](http://selenium-python.readthedocs.io/installation.html#drivers)).

Add the browser type and the path to the driver to your project configuration:

```python
SELENIUM_PANEL = {
    'BROWSER': "firefox",
    'DRIVER': "/home/username/geckodriver",
}
```

You can now launch a browser using `python manage.py runselenium -s http://selenium-panel-server`.

You can omit the server address if you're running Selenium Panel on your local machine.

### Creating tasks

You can create your Selenium tests inheriting from `SeleniumRemoteTask` and overriding the `run_selenium_task` method:

```python
from selenium_panel.tasks import SeleniumRemoteTask

class GoogleSearchTask(SeleniumRemoteTask):
    name = "selenium.google_search"
    SELENIUM_CONFIG = {
        # Arguments entered when you run the test from Selenium Panel
        'arguments': {
            'words': {
                'name': "Words",
                'required': True,
            }
        }
    }

    def run_selenium_task(self, *args, **kwargs):
        # You can access the entered arguments here
        words = kwargs['arguments']['words']
        self.browser.get(self.server)
        search_input = self.browser.find_element_by_name("q")
        search_input.send_keys(words)
        search_input.submit()
```

Interact with the Selenium driver using `self.browser`. Have a look at [Selenium with Python](http://selenium-python.readthedocs.io/index.html) to see what you can do.

Once your task is ready, add it to your project configuration so you can launch it on any browser connected to the Selenium Panel:

```python
SELENIUM_PANEL = {
    # ...
    'TASKS': [
        # ...
        ('selenium.google_search', 'Google Search'),
    ],
    'SERVERS': {
        'default': {
            'address': "https://www.google.com",
            'name': "Google",
        },
        'google_uk': {
            'address': "https://www.google.co.uk",
            'name': "Google UK"
        }
    },
}
```

You can also add a list of servers that can be selected when you launch the task from the Selenium Panel. The selected server will be stored on the `self.server` attribute of your task.
