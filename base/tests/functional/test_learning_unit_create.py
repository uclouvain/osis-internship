##############################################################################
#
# OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################

from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import WebDriverException
import time
import unittest

MAX_WAIT = 10


class LearningUnitsSearchTest(unittest.TestCase):

    def setUp(self):
        self.create_user()
        self.browser = webdriver.Firefox()

    def create_user(self):
        self.user=User.objects.create_user(username='dummy_usr',
                                 email='dummy@dummy.com',
                                password='dummy_pwd')

    def error_displayed(self,error_msg):
        start_time = time.time()
        while True:
            try:
                error_invalid_search= self.browser.find_element_by_class_name('error').text
                self.assertEqual(_(error_msg), error_invalid_search)
                return
            except (AssertionError, WebDriverException) as e:
                if time.time() - start_time > MAX_WAIT:
                    raise e
                time.sleep(0.5)

    def go_home_page(self):
        start_time = time.time()
        while True:
            try:
                self.assertIn('OSIS', self.browser.title)
                header_text = self.browser.find_element_by_tag_name('h1').text
                self.assertIn('Log-in', header_text)
                return
            except (AssertionError, WebDriverException) as e:
                if time.time() - start_time > MAX_WAIT:
                    raise e
                time.sleep(0.5)

    def go_learning_units_page(self):
        # She goes on the homepage to log in
        self.browser.get('http://127.0.0.1:8000/')  # We should use : self.live_server_url
        self.go_home_page()

        # She is invited to log in
        self.user_logs_in('defat','osis')

        # She goes in the header menu and clicks on 'Formation Catalogue'
        # and then 'Learning Units' to go on the search page of learning units.
        self.browser.get('http://127.0.0.1:8000/learning_units/')
        # She notices the title of the learning units search page
        self.wait_for_tag('h2','learning_units')

    def user_logs_in(self, usr, pwd):
        inputbox_login_usr = self.browser.find_element_by_id('id_username')
        self.assertEqual(
            inputbox_login_usr.get_attribute('placeholder'),
            _('user')
        )
        inputbox_login_pwd = self.browser.find_element_by_id('id_password')
        self.assertEqual(
            inputbox_login_pwd.get_attribute('placeholder'),
            _('password')
        )
        inputbox_login_usr.send_keys('dummy_usr')
        inputbox_login_pwd.send_keys('dummy_pwd')
        login_button = self.browser.find_element_by_id('post_login_btn')
        login_button.send_keys(Keys.ENTER)
        start_time = time.time()
        while True:
            try:
                dropdown_text = self.browser.find_element_by_id('lnk_home_dropdown_catalog').text
                self.assertEqual(_('formation_catalogue'), dropdown_text)
                return
            except (AssertionError, WebDriverException) as e:
                if time.time() - start_time > MAX_WAIT:
                    raise e
                time.sleep(0.5)

    def wait_for_row_in_list_table(self, row_text):
        start_time = time.time()
        while True:
            try:
                table = self.browser.find_element_by_id('table_learning_units')
                rows = table.find_elements_by_tag_name('tr')
                self.assertIn(row_text, [row.text for row in rows])
                return
            except (AssertionError, WebDriverException) as e:
                if time.time() - start_time > MAX_WAIT:
                    raise e
                time.sleep(0.5)

    def wait_for_cols_in_list_table(self, col_text):
        start_time = time.time()
        while True:
            try:
                table = self.browser.find_element_by_id('table_learning_units')
                cols = table.find_elements_by_tag_name('td')
                self.assertIn(col_text, [col.text for col in cols])
                return
            except (AssertionError, WebDriverException) as e:
                if time.time() - start_time > MAX_WAIT:
                    raise e
                time.sleep(0.5)

    def wait_for_tag(self,tag_name,tag_value):
        start_time = time.time()
        while True:
            try:
                header_text = self.browser.find_element_by_tag_name(tag_name).text
                self.assertEqual(_(tag_value), header_text)
                return
            except (AssertionError, WebDriverException) as e:
                if time.time() - start_time > MAX_WAIT:
                    raise e
                time.sleep(0.5)

    def tearDown(self):
        self.browser.quit()

    def test_error_when_search_has_academic_year_and_acronym_only(self):
        # Sarah needs to check out an existing learning_unit
        self.go_learning_units_page()

        # She specifies an academic year and an acronym,
        # to see if a learning unit exists in a particular year.
        academic_year = Select(self.browser.find_element_by_id('slt_academic_year'))
        #print ([ay.text for ay in academic_year.options])
        academic_year.select_by_visible_text('2016-2017')

        # She enters a valid acronym only,
        # to see if a learning unit exists in a particular year.
        inputbox_acronym=self.browser.find_element_by_id('id_acronym')
        inputbox_acronym.send_keys('ESPO1234')

        # She starts a search by pressing ENTER
        login_button= self.browser.find_element_by_id('bt_submit_learning_unit_search')
        login_button.send_keys(Keys.ENTER)

        # She sees a message "no result found" when the page refreshes
        #

        # Unhappy of the situation, she closes the browser...