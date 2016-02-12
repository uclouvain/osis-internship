##############################################################################
#
# OSIS stands for Open Student Information System. It's an application
# designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2016 Université catholique de Louvain (http://www.uclouvain.be)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
"""
File that contains health tests made with selenium
"""
from datetime import date
import os
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.utils.translation import ugettext as _
from selenium.common.exceptions import NoSuchElementException
from core.tests import util
from selenium import webdriver
from osis_backend.settings import SCREEN_SHOT_FOLDER, FIREFOX_PROFILE_PATH


class HealthTests(StaticLiveServerTestCase):

    def take_screen_shot(self, name):
        today = date.today().strftime("%d_%m_%y")
        screenshot_name = ''.join([name, '_', today, '.png'])
        self.selenium.save_screenshot(os.path.join(SCREEN_SHOT_FOLDER, screenshot_name))


    def getUrl(self, url):
        self.selenium.get('%s%s' % (self.live_server_url, url))

    def is_element_present(self,id):
        """
        Check if an element is present on a web page.
        :param id:
        :return:
        """
        try:
            self.selenium.find_element_by_id(id)
        except NoSuchElementException:
            return False
        return True


    @classmethod
    def setUpClass(cls):
        """
        Initialisation for all the testCase , done only once
        - Initialise Firefox driver
        - Maximize browser window
        :param cls:
        :return:
        """
        profile = webdriver.FirefoxProfile(FIREFOX_PROFILE_PATH)
        cls.selenium = webdriver.Firefox(profile)
        cls.selenium.implicitly_wait(10)
        cls.selenium.maximize_window()
        super(HealthTests, cls).setUpClass()

    def setUp(self):
        """
        Initialisation For each test:

        :return:
        """
        self.verificationErrors = []

    @classmethod
    def tearDownClass(cls):
        """
        - close selenium conexion
        :return:
        """
        cls.selenium.quit()
        super(HealthTests, cls).tearDownClass()

    def test_index_page(self):
        """
        Test if the index page is well loaded
        """
        self.getUrl("/")
        assert "OSIS" in self.selenium.title
        assert self.selenium.find_element_by_id('login_bt') is not None
        self.take_screen_shot('osis_index')

    def test_valid_admin_login(self):
        """
        Test the connecttion of a valid user which is also administrator
        """
        util.init_admin_user()
        self.getUrl("/")
        self.selenium.find_element_by_id('login_bt').click()
        assert self.is_element_present('id_username')
        assert self.is_element_present('id_password')
        user_name_field = self.selenium.find_element_by_id('id_username')
        user_name_field.send_keys(util.ADMIN_USER)
        user_password_field = self.selenium.find_element_by_id('id_password')
        user_password_field.send_keys(util.PASSWORD)
        self.selenium.find_element_by_id('post_login_btn').click()
        assert self.is_element_present('admin_bt')
        assert self.is_element_present('user_btn')
        self.assertFalse(self.is_element_present('login_bt'))
        self.take_screen_shot('valid_admin_login')