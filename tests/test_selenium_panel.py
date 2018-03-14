import json
import socket
from mock import patch, PropertyMock

from django.test import TestCase, LiveServerTestCase
from django.core.management import call_command
from django.core.management.base import CommandError
from django.core.urlresolvers import reverse

from selenium_panel.management.commands import runselenium
from selenium_panel.models import Browser
from selenium_panel.tasks import SeleniumRemoteTask
from selenium_panel.webdriver import RemoteWebDriver


class ServiceMock(object):
    service_url = "http://localhost:8000"


class BrowserMock(object):
    session_id = "qwerty"

    def __init__(self, exception=None, *args, **kwargs):
        self.exception = exception

    def execute(self, command):
        if self.exception:
            raise self.exception

    def quit(self):
        pass


class AsyncResultMock(object):
    fail = False

    def __init__(self, fail=False, *args, **kwargs):
        if fail:
            self.fail = True

    def failed(self):
        return self.fail

    def ready(self):
        return False


class SeleniumPanelTestCase(TestCase):

    def setUp(self):
        self.browser = Browser.objects.create(
            service_url="http://localhost:8080",
            session_id="qwerty",
            username="testuser",
            platform="Linux",
            driver="firefox"
        )

    def test_index_view(self):
        response = self.client.get(reverse('selenium_panel:index'))
        self.assertEqual(response.status_code, 200)
        config = json.loads(response.context['config'])
        self.assertTrue(config['tasks'].get('selenium.open_google_result'))
        parents = config['tasks']['selenium.open_google_result']['parents']
        self.assertIn('selenium.google_search', parents)

    def test_add_browser_required_fields(self):
        browser_data = {
            'service_url': "http://192.168.0.2:8080",
            'driver': "firefox",
        }
        response = self.client.post(
            reverse('selenium_panel:add_browser'),
            json.dumps(browser_data),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn('are required', json.loads(response.content)['detail'])

    def test_add_browser(self):
        browser_data = {
            'service_url': "http://192.168.0.2:8080",
            'session_id': "qwerty",
            'driver': "firefox",
            'username': "testuser",
        }
        response = self.client.post(
            reverse('selenium_panel:add_browser'),
            json.dumps(browser_data),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 201)
        self.assertTrue(
            Browser.objects.filter(
                session_id=browser_data['session_id'],
                driver=browser_data['driver'],
                username=browser_data['username'],
            ).exists()
        )

    def test_browser_list_view(self):
        response = self.client.get(reverse('selenium_panel:browser_list'))
        self.assertEqual(response.status_code, 200)
        browser_data = json.loads(response.content)['http://localhost:8080']
        self.assertEqual(browser_data['platform'], self.browser.platform)
        self.assertEqual(browser_data['username'], self.browser.username)
        self.assertEqual(browser_data['driver'], self.browser.driver)
        self.assertEqual(browser_data['status'], "Idle")

    @patch('selenium_panel.views.Browser.status', new_callable=PropertyMock)
    @patch('selenium_panel.tasks.GoogleSearchTask.run')
    def test_run_task_view(self, mock_run, mock_status):
        mock_run.return_value = None
        mock_status.return_value = "Running"
        data = {
            'task': 'selenium.google_search',
            'service_url': self.browser.service_url,
        }
        response = self.client.post(
            reverse('selenium_panel:run_task'),
            json.dumps(data),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 201)
        mock_run.assert_called_once_with(
            service_url=self.browser.service_url,
            session_id=self.browser.session_id
        )

    @patch('selenium_panel.models.AsyncResult')
    def test_browser_status(self, mock_async_result):
        self.browser.running_task = "qwerty"
        mock_async_result.return_value = AsyncResultMock(fail=True)
        self.assertEqual(self.browser.status, "Failed")
        mock_async_result.return_value = AsyncResultMock()
        self.assertEqual(self.browser.status, "Running")

    def test_webdriver(self):
        browser = RemoteWebDriver(
            command_executor='http://localhost:8080/',
            session_id='qwerty',
        )
        self.assertEqual(browser.session_id, 'qwerty')


class SeleniumTaskTestCase(TestCase):

    def test_selenium_base_task(self):
        task = SeleniumRemoteTask()
        task.run(
            service_url='http://localhost:8080/',
            session_id='qwerty',
            server='default',
        )
        self.assertEqual(task.browser.session_id, 'qwerty')
        self.assertEqual(task.server, 'https://www.google.com')


class SeleniumPanelManagementCommandTestCase(LiveServerTestCase):

    def test_no_settings(self):
        assert_error = self.assertRaises(CommandError)
        with self.settings(SELENIUM_PANEL=None), assert_error:
            call_command('runselenium')
        # No browser
        with self.settings(SELENIUM_PANEL={}), assert_error:
            call_command('runselenium')
        # Unknown browser
        with self.settings(SELENIUM_PANEL={'BROWSER': "none"}), assert_error:
            call_command('runselenium')
        # No driver path
        with self.settings(SELENIUM_PANEL={'BROWSER': "chrome"}), assert_error:
            call_command('runselenium')

    def test_add_browser_method(self):
        command = runselenium.Command()
        browser = BrowserMock()
        browser.service = ServiceMock()
        command.add_browser(browser, server=self.live_server_url)
        self.assertTrue(
            Browser.objects.filter(session_id=browser.session_id).exists()
        )

    def test_listen_keyboard_interrupt(self):
        command = runselenium.Command()
        browser = BrowserMock(exception=KeyboardInterrupt)
        browser.service = ServiceMock()
        command.add_browser(browser)
        with self.assertRaises(SystemExit):
            command.listen(browser)
        self.assertFalse(Browser.objects.count())

    def test_listen_connection_error(self):
        command = runselenium.Command()
        browser = BrowserMock(exception=socket.error)
        browser.service = ServiceMock()
        command.add_browser(browser)
        with self.assertRaises(CommandError):
            command.listen(browser)
        self.assertFalse(Browser.objects.count())

    @patch('selenium_panel.management.commands.runselenium.Command.listen')
    @patch('selenium_panel.management.commands.runselenium.Command.'
           'add_browser')
    @patch('selenium_panel.management.commands.runselenium.FirefoxDriver.'
           '__init__')
    def test_runselenium_command(self, mock_init, mock_add, mock_listen):
        mock_init.return_value = None
        call_command('runselenium', server=self.live_server_url)
        self.assertTrue(mock_add.called)
        self.assertEqual(mock_add.call_args[1]['server'], self.live_server_url)
        self.assertTrue(mock_listen.called)
