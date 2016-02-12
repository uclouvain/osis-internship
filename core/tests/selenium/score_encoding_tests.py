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
from core.tests import util
from osis_backend.settings import FIREFOX_PROFILE_PATH, SCREEN_SHOT_FOLDER, EMAIL_FILE_PATH


class TestSendMailAfterSubmission(StaticLiveServerTestCase):
    """
    This class test the sending of a message to all the tutors of a learning_unit , after the score encoding is submitted.
    All the previous states of this business feature are supposed to be done.
    We only test the fact that after the submission , a mail is sent
    """

    fixtures = ['core/fixtures/send_mail_after_encoding.json']

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
        super(TestSendMailAfterSubmission, cls).setUpClass()


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
        super(TestSendMailAfterSubmission, cls).tearDownClass()

    def test_send_mail_after_encoding_submission(self):
        """
        Test if a mail is sent after the submission of encoded scores
        """
        self.getUrl("/")
        self.selenium.find_element_by_id('login_bt').click()
        assert self.is_element_present('id_username')
        assert self.is_element_present('id_password')
        user_name_field = self.selenium.find_element_by_id('id_username')
        user_name_field.send_keys('osis')
        user_password_field = self.selenium.find_element_by_id('id_password')
        user_password_field.send_keys('osis')
        self.selenium.find_element_by_id('post_login_btn').click()
        self.selenium.find_element_by_id('home_studies_btn').click()
        self.take_screen_shot('submission_1')
        assert self.is_element_present('studies_evaluation_btn')
        self.selenium.find_element_by_id('studies_evaluation_btn').click()
        self.take_screen_shot('submission_2')
        assert self.is_element_present('score_encoding_btn')
        self.selenium.find_element_by_id("score_encoding_btn").click()
        self.take_screen_shot('submission_3')
        assert self.is_element_present('DROI1000_link')
        self.selenium.find_element_by_id("DROI1000_link").click()
        self.take_screen_shot('submission_4')
        assert self.is_element_present('score_submission_modal_btn')
        self.selenium.find_element_by_id("score_submission_modal_btn").click()
        self.take_screen_shot('submission_5')
        assert self.is_element_present('post_scores_submission_btn')
        self.selenium.find_element_by_id("post_scores_submission_btn").click()
        self.take_screen_shot('submission_6')


