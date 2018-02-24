from selenium.webdriver import Remote


class RemoteWebDriver(Remote):
    """
    Overrides Selenium Remote class to allow connections to existing browsers
    """

    def __init__(self, command_executor='http://127.0.0.1:4444/wd/hub',
                 desired_capabilities=None, browser_profile=None, proxy=None,
                 keep_alive=False, file_detector=None, options=None,
                 session_id=None):
        super(RemoteWebDriver, self).__init__(
            command_executor=command_executor,
            desired_capabilities=desired_capabilities or {},
            browser_profile=browser_profile,
            proxy=proxy,
            keep_alive=keep_alive,
            file_detector=file_detector,
            options=options
        )
        self.session_id = session_id

    def start_session(self, capabilities, browser_profile=None):
        # W3C Compliant browser
        self.w3c = True
        self.command_executor.w3c = self.w3c
