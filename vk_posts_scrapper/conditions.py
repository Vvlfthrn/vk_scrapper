from selenium.common import StaleElementReferenceException
from selenium.webdriver.support.expected_conditions import WebDriverOrWebElement


def images_loaded(locator):
    def _predicate(driver: WebDriverOrWebElement):
        try:
            elements = driver.find_elements(*locator)
            if not elements:
                return True
            for element in elements:
                if (
                        element.tag_name == 'video' and not element.get_property('played')
                ) or (
                        element.tag_name=='img' and not element.get_property('complete')):
                    return False
            return elements
        except StaleElementReferenceException:
            return False

    return _predicate