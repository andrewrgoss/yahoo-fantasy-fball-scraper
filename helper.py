#!/usr/bin/python3
__author__ = 'agoss'

from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait


def _wait_for_first(browser, selectors, timeout=15):
    """Return the first matching element across Yahoo's supported login layouts."""

    for selector in selectors:
        try:
            return WebDriverWait(browser, timeout).until(
                expected_conditions.presence_of_element_located((By.CSS_SELECTOR, selector))
            )
        except TimeoutException:
            continue
    raise TimeoutException(f'None of the selectors matched: {selectors}')


def yahoo_account_login(user_email, user_pw, browser):
    """
    Login to Yahoo account to access fantasy football player projections based on league settings.
    """

    browser.get('https://login.yahoo.com')
    email_elem = _wait_for_first(browser, (
        '#login-username',
        '#username',
        'input[name="username"]',
    ))
    email_elem.send_keys(user_email)
    login_btn = _wait_for_first(browser, (
        '#login-signin',
        'button[name="signin"]',
        'input[type="submit"][name="signin"]',
    ))
    login_btn.click()
    pw_elem = _wait_for_first(browser, (
        '#login-passwd',
        '#password',
        'input[name="password"]',
        'input[type="password"]',
    ))
    pw_elem.send_keys(user_pw)
    submit_btn = _wait_for_first(browser, (
        '#login-signin',
        'button[name="verify"]',
        'button[type="submit"]',
        'input[type="submit"]',
    ))
    submit_btn.click()
    # Yahoo redirects asynchronously after credential submission. Do not
    # navigate to Fantasy Football until the login page has handed off.
    try:
        WebDriverWait(browser, 30).until(
            lambda driver: 'login.yahoo.com' not in driver.current_url
        )
    except TimeoutException:
        # Leave any account challenge visible for the caller; the auction page
        # will produce a clear error if authentication did not complete.
        pass
    return browser
