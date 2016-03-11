# coding: utf-8

from __future__ import (unicode_literals, print_function,
                        absolute_import, division)

import unittest
import json

from f8dff.models.formpack.pack import FormPack
from f8dff.fixtures import build_fixture


customer_satisfaction = build_fixture('customer_satisfaction')
restaurant_profile = build_fixture('restaurant_profile')


class TestFormPackExport(unittest.TestCase):
    maxDiff = None

    def test_generator_export(self):
        forms = FormPack(**customer_satisfaction)
        values_exported = forms._export_to_lists()
        expected = [["submissions", [
                        ["restaurant_name", "customer_enjoyment"],
                        [
                            ["Felipes", "yes"],
                            ["Dunkin Donuts", "no"],
                            ["McDonalds", "no"]]]
                     ]]

        self.assertEqual(expected, values_exported)

    def test_generator_export_translation_headers(self):
        fp = FormPack(**restaurant_profile)
        self.assertEqual(len(fp.versions), 3)
        self.assertEqual(len(fp[1].translations), 2)

        # by default, exports use the question 'name' attribute
        headers = fp._export_to_lists(version=0)[0][1][0]
        self.assertEquals(headers, ['restaurant_name', 'location'])

        # the first translation in the list is the translation that
        # appears first in the column list. in this case, 'label::english'
        translations = fp[1].translations
        headers = fp._export_to_lists(header_lang=translations[0],
                                      version=1)[0][1][0]
        self.assertEquals(headers, ['restaurant name', 'location'])

        headers = fp._export_to_lists(header_lang=translations[1],
                                      version=1)[0][1][0]
        self.assertEquals(headers, ['nom du restaurant', 'lieu'])

        # "default" use the "Label" field
        # TODO: make a separate test to test to test __getitem__
        formpack = FormPack(**restaurant_profile)

        # we should discuss how to do this a bit better. "default" could
        # be the name of a language
        headers = formpack._export_to_lists(header_lang="default",
                                            version='rpv1')
        self.assertEquals(headers[0][1][0], ['restaurant name', 'location'])

    def test_export_with_choice_lists(self):
        fp = FormPack(**restaurant_profile)
        self.assertEqual(len(fp[1].translations), 2)
        # by default, exports use the question 'name' attribute
        options = {'version': 'rpV3'}
        (headers, submissions) = fp._export_to_lists(**options)[0][1]
        self.assertEquals(headers, ['restaurant_name', 'location', 'eatery_type'])
        self.assertEquals(submissions, [['Taco Truck', '13.42 -25.43', 'takeaway'],
                                        ['Harvest', '12.43 -24.53', 'sit_down']])

        options['translation'] = fp[1].translations[0]
        (headers, submissions) = fp._export_to_lists(**options)[0][1]
        self.assertEquals(submissions, [['Taco Truck', '13.42 -25.43', 'take-away'],
                                        ['Harvest', '12.43 -24.53', 'sit down']])

        options['translation'] = fp[1].translations[1]
        (headers, submissions) = fp._export_to_lists(**options)[0][1]
        self.assertEquals(submissions, [['Taco Truck', '13.42 -25.43', 'avec vente à emporter'],
                                        ['Harvest', '12.43 -24.53', 'traditionnel']])

    def test_headers_of_group_exports(self):
        grouped_questions = build_fixture('grouped_questions')
        fp = FormPack(**grouped_questions)
        options = {'version': 'gqs'}

        # by default, groups are stripped. (Sound good?)
        (headers, submissions) = fp._export_to_lists(**options)[0][1]
        self.assertEquals(headers, ['q1', 'g1', 'g2', 'qz'])

        # verifying false value of include_groups_in_header gives same result
        options['include_groups_in_header'] = False
        (headers, submissions) = fp._export_to_lists(**options)[0][1]
        self.assertEquals(headers, ['q1', 'g1', 'g2', 'qz'])

        # include_groups_in_header=True means the groups are counted as columns
        options['include_groups_in_header'] = True
        self.assertEquals(headers, ['q1', 'g1', 'g1q1', 'g2', 'g2q1', 'qz'])

    def test_submissions_of_group_exports(self):
        grouped_questions = build_fixture('grouped_questions')
        fp = FormPack(**grouped_questions)
        options = {'version': 'gqs',
                   'include_groups_in_header': False}

        (headers, submissions) = fp._export_to_lists(**options)[0][1]
        self.assertEquals(headers, ['q1', 'g1q1', 'g2q1', 'qz'])
        self.assertEquals(submissions, [['correct values need to be here for respondent 1'],
                                        ['correct values need to be here for respondent 2']])

        options['include_groups_in_header'] = True
        (headers, submissions) = fp._export_to_lists(**options)[0][1]
        self.assertEquals(headers, ['q1', 'g1', 'g1q1', 'g2', 'g2q1', 'qz'])
        self.assertEquals(submissions, [['correct values need to be here for respondent 1'],
                                        ['correct values need to be here for respondent 2']])
