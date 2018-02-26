import getpass
import platform
import requests
import socket
import sys
import time

from datetime import datetime
from httplib import CannotSendRequest
from selenium.webdriver.firefox.webdriver import WebDriver as FirefoxDriver
from selenium.webdriver.chrome.webdriver import WebDriver as ChromeDriver
from selenium.webdriver.remote.command import Command as BrowserCommand

from django.conf import settings
from django.core.urlresolvers import reverse
from django.core.management.base import BaseCommand, CommandError
from selenium_panel.models import Browser


class Command(BaseCommand):
    help = "Starts a Selenium browser."

    driver = {
        'firefox': FirefoxDriver,
        'chrome': ChromeDriver
    }

    def add_arguments(self, parser):
        parser.add_argument(
            '--server', '-s',
            help='Selenium remote server address'
        )

    def handle(self, *args, **options):

        if not getattr(settings, 'SELENIUM_PANEL', False):
            raise CommandError("You must set selenium settings first.")

        if not settings.SELENIUM_PANEL.get('BROWSER'):
            raise CommandError("You must set a browser.")

        if not self.driver.get(settings.SELENIUM_PANEL['BROWSER']):
            raise CommandError("Browser setting not recognized.")

        if not settings.SELENIUM_PANEL.get('DRIVER'):
            raise CommandError("You must set the path to the geckodriver.")

        driver = self.driver[settings.SELENIUM_PANEL['BROWSER']]
        browser = driver(executable_path=settings.SELENIUM_PANEL['DRIVER'])

        browser_data = {
            'service_url': browser.service.service_url,
            'session_id': browser.session_id,
            'username': getpass.getuser(),
            'driver': settings.SELENIUM_PANEL['BROWSER'],
            'platform': "{} {} {}".format(
                platform.system(),
                platform.release(),
                "-".join(platform.dist()),
            )
        }

        if options.get('server'):
            server = options['server']
            if server.endswith('/'):
                server = server[:-1]
            url = "{}{}".format(server, reverse('selenium:add_browser'))
            response = requests.post(url, json=browser_data)
            if response.status_code != 201:
                browser.quit()
                raise CommandError("Couldn't register browser.")
        else:
            Browser.objects.create(**browser_data)

        now = datetime.now().strftime('%B %d, %Y - %X')
        self.stdout.write(now)
        self.stdout.write((
            "Selenium %(browser)s browser\n"
            "Starting at %(url)s\n"
            "With session ID %(session_id)s\n"
        ) % {
            'browser': settings.SELENIUM_PANEL['BROWSER'],
            'url': browser.service.service_url,
            'session_id': browser.session_id,
        })

        try:
            while True:
                browser.execute(BrowserCommand.STATUS)
                time.sleep(30)
        except (socket.error, CannotSendRequest):
            Browser.objects.filter(
                service_url=browser.service.service_url,
                session_id=browser.session_id,
            ).delete()
            raise CommandError("Browser closed unexpectedly.")
        except KeyboardInterrupt:
            Browser.objects.filter(
                service_url=browser.service.service_url,
                session_id=browser.session_id,
            ).delete()
            browser.quit()
            sys.exit(0)
