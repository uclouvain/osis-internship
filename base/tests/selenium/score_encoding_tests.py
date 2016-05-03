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
File that contains all the selenium tests for the scores encoding.
Each class represent a specific feature to test.
Most of the time a feature need tata to be on a specific state; for that reason the database is reconstructed on the class level.
Data will be injected for specific state.
"""
from datetime import date

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
import os
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException

from backoffice.settings import FIREFOX_PROFILE_PATH, SCREEN_SHOT_FOLDER


class ScoreEncodingTests(StaticLiveServerTestCase):
    """
    This class test the sending of a message to all the tutors of a learning_unit , after the score encoding is submitted.
    All the previous states of this business feature are supposed to be done.
    We only test the fact that after the submission , a mail is sent
    """

    fixtures = ['core/fixtures/score_encoding_base.json']

    def take_screen_shot(self, name):
        today = date.today().strftime("%d_%m_%y")
        screenshot_name = ''.join([name, '_', today, '.png'])
        self.selenium.save_screenshot(os.path.join(SCREEN_SHOT_FOLDER, screenshot_name))

    def getUrl(self, url):
        self.selenium.get('%s%s' % (self.live_server_url, url))

    def is_element_present(self,id):
        """
        Check if an element is present on a web page.
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
        """
        profile = webdriver.FirefoxProfile(FIREFOX_PROFILE_PATH)
        cls.selenium = webdriver.Firefox(profile)
        cls.selenium.implicitly_wait(10)
        cls.selenium.maximize_window()
        super(ScoreEncodingTests, cls).setUpClass()


    def setUp(self):
        """
        Initialisation For each test:
        """
        self.verificationErrors = []

    @classmethod
    def tearDownClass(cls):
        """
        - close selenium conexion
        """
        cls.selenium.quit()
        super(ScoreEncodingTests, cls).tearDownClass()

    def test_score_encoding(self):
        test_no_decimal_allowed_submission(self)


def test_no_decimal_allowed_submission (score_encoding):
    """
    Test if a mail is sent after the submission of encoded scores
    """
    score_encoding.getUrl("/")
    score_encoding.selenium.find_element_by_id('login_bt').click()
    assert score_encoding.is_element_present('id_username')
    assert score_encoding.is_element_present('id_password')
    user_name_field = score_encoding.selenium.find_element_by_id('id_username')
    user_name_field.send_keys('prof3')
    user_password_field = score_encoding.selenium.find_element_by_id('id_password')
    user_password_field.send_keys('prof3')
    score_encoding.selenium.find_element_by_id('post_login_btn').click()
    assert score_encoding.is_element_present('lnk_home_dropdown_parcours')
    score_encoding.selenium.find_element_by_id('lnk_home_dropdown_parcours').click()
    assert score_encoding.is_element_present('lnk_dropdown_evaluations')
    score_encoding.selenium.find_element_by_id('lnk_dropdown_evaluations').click()
    assert score_encoding.is_element_present('lnk_score_encoding')
    score_encoding.selenium.find_element_by_id("lnk_score_encoding").click()
    assert score_encoding.is_element_present('lnk_encode')
    score_encoding.selenium.find_element_by_id("lnk_encode").click()
    assert score_encoding.is_element_present('num_score_14')
    score_encoding.selenium.find_element_by_id("num_score_14").send_keys('7.9')
    assert score_encoding.is_element_present('bt_submit_online_encoding')
    score_encoding.selenium.find_element_by_id("bt_submit_online_encoding").click()
    assert score_encoding.is_element_present('num_score_14')
    score_encoding.selenium.find_element_by_id("num_score_14").send_keys('7')
    assert score_encoding.is_element_present('bt_submit_online_encoding')
    score_encoding.selenium.find_element_by_id("bt_submit_online_encoding").click()
    score_encoding.selenium.find_element_by_id("lnk_online_double_encoding").click()
    assert score_encoding.is_element_present('num_double_score_14')
    score_encoding.selenium.find_element_by_id("num_double_score_14").send_keys('7.9')
    assert score_encoding.is_element_present('bt_compare')
    score_encoding.selenium.find_element_by_id("bt_compare").click()
    assert score_encoding.is_element_present('num_double_score_14')
    score_encoding.selenium.find_element_by_id("num_double_score_14").send_keys('8')
    assert score_encoding.is_element_present('bt_compare')
    score_encoding.selenium.find_element_by_id("bt_compare").click()
    assert score_encoding.is_element_present('bt_take_reencoded_14')
    score_encoding.selenium.find_element_by_id("bt_take_reencoded_14").click()
    assert score_encoding.is_element_present('bt_submit_online_double_encoding_validation')
    score_encoding.selenium.find_element_by_id("bt_submit_online_double_encoding_validation").click()


