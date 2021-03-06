# coding: utf-8

from __future__ import (unicode_literals, print_function,
                        absolute_import, division)
import json
import copy
from collections import OrderedDict

from formpack.utils.expand_content import expand_content, _get_special_survey_cols
from formpack.utils.flatten_content import flatten_content


def test_expand_select_one():
    s1 = {'survey': [{'type': 'select_one dogs'}]}
    expand_content(s1)
    assert s1['survey'][0]['type'] == {'select_one': 'dogs'}


def test_expand_select_multiple():
    s1 = {'survey': [{'type': 'select_multiple dogs'}]}
    expand_content(s1)
    assert s1['survey'][0]['type'] == {'select_multiple': 'dogs'}


def test_expand_media():
    s1 = {'survey': [{'type': 'note',
                      'media::image': 'ugh.jpg'}]}
    expand_content(s1)
    assert s1 == {'survey': [
            {
              'type': 'note',
              'media::image': 'ugh.jpg'
            }
        ]}
    flatten_content(s1)
    assert s1 == {'survey': [{
        'type': 'note',
        'media::image': 'ugh.jpg',
      }]}


def test_expand_translated_media():
    s1 = {'survey': [{'type': 'note',
                      'media::image::English': 'eng.jpg'
                      }]}
    expand_content(s1)
    assert s1 == {'survey': [
            {'type': 'note',
                'media::image': ['eng.jpg']
             }
        ],
        'translations': ['English']}
    flatten_content(s1)
    assert s1 == {'survey': [{
        'type': 'note',
        'media::image::English': 'eng.jpg',
      }],
      'translations': ['English']}


def test_expand_translated_media_with_no_translated():
    s1 = {'survey': [{'type': 'note',
                      'media::image': 'nolang.jpg',
                      'media::image::English': 'eng.jpg',
                      }],
          'translations': ['English', None]}
    expand_content(s1)
    assert s1 == {'survey': [
            {'type': 'note',
                'media::image': ['eng.jpg', 'nolang.jpg']
             }
        ],
        'translations': ['English', None]}
    flatten_content(s1)
    assert s1 == {'survey': [{
        'type': 'note',
        'media::image': 'nolang.jpg',
        'media::image::English': 'eng.jpg',
      }],
      'translations': ['English', None]}


def test_expand_translated_choice_sheets():
    s1 = {'survey': [{'type': 'select_one yn',
                      'label::En': 'English Select1',
                      'label::Fr': 'French Select1',
                      }],
          'choices': [{'list_name': 'yn',
                       'name': 'y',
                       'label::En': 'En Y',
                       'label::Fr': 'Fr Y',
                      },
                      {
                       'list_name': 'yn',
                       'name': 'n',
                       'label::En': 'En N',
                       'label::Fr': 'Fr N',
                      }],
          'translations': ['En', 'Fr']}
    expand_content(s1)
    assert s1 == {'survey': [{'type': {'select_one': 'yn'},
                  'label': ['English Select1', 'French Select1'],
                  }],
                  'choices': [{'list_name': 'yn',
                               'name': 'y',
                               'label': ['En Y', 'Fr Y'],
                               },
                              {
                               'list_name': 'yn',
                               'name': 'n',
                               'label': ['En N', 'Fr N'],
                               }],
                  'translations': ['En', 'Fr']}

def _s(rows):
    return {'survey': [dict([[key, 'x']]) for key in rows]}

def test_ordered_dict_preserves_order():
    (special, t) = _get_special_survey_cols({
            'survey': [
                OrderedDict([
                        ('label::A', 'A'),
                        ('label::B', 'B'),
                        ('label::C', 'C'),
                    ])
            ]
        })
    assert t == ['A', 'B', 'C']
    (special, t) = _get_special_survey_cols({
            'survey': [
                OrderedDict([
                        ('label::C', 'C'),
                        ('label::B', 'B'),
                        ('label::A', 'A'),
                    ])
            ]
        })
    assert t == ['C', 'B', 'A']


def test_get_special_survey_cols():
    (special, t) = _get_special_survey_cols(_s([
            'type',
            'media::image',
            'media::image::English',
            'label::Français',
            'label',
            'label::English',
            'media::audio::chinese',
            'label: Arabic',
            'label :: German',
            'label:English',
            'hint:English',
        ]))
    assert sorted(special.keys()) == sorted([
            'label',
            'media::image',
            'media::image::English',
            'label::Français',
            'label::English',
            'media::audio::chinese',
            'label: Arabic',
            'label :: German',
            'label:English',
            'hint:English',
        ])
    values = [special[key] for key in sorted(special.keys())]
    assert sorted(map(lambda x: x.get('translation'), values)
                  ) == sorted(['English', 'English', 'English', 'English',
                               'chinese', 'Arabic', 'German', 'Français',
                               None, None])


def test_not_special_cols():
    not_special = [
        'bind::orx:for',
        'bind:jr:constraintMsg',
        'bind:relevant',
        'body::accuracyThreshold',
        'body::accuracyTreshold',
        'body::acuracyThreshold',
        'body:accuracyThreshold',
    ]
    (not_special, _t) = _get_special_survey_cols(_s(not_special))
    assert not_special.keys() == []


def test_expand_constraint_message():
    s1 = {'survey': [{'type': 'integer',
                      'constraint': '. > 3',
                      'label::XX': 'X number',
                      'label::YY': 'Y number',
                      'constraint_message::XX': 'X: . > 3',
                      'constraint_message::YY': 'Y: . > 3',
                      }],
          'translations': ['XX', 'YY']}
    s1_copy = copy.deepcopy(s1)
    x1 = {'survey': [{'type': 'integer',
                      'constraint': '. > 3',
                      'label': ['X number', 'Y number'],
                      'constraint_message': ['X: . > 3', 'Y: . > 3'],
                      }],
          'translations': ['XX', 'YY'],
          }
    expand_content(s1)
    assert s1 == x1
    flatten_content(x1)
    assert x1 == s1_copy


def test_expand_translations():
    s1 = {'survey': [{'type': 'text',
                      'label::English': 'OK?',
                      'label::Français': 'OK!'}]}
    x1 = {'survey': [{'type': 'text',
                      'label': ['OK?', 'OK!']}],
          'translations': ['English', 'Français']}
    expand_content(s1)
    assert s1 == x1
    flatten_content(s1)
    assert s1 == {'survey': [{'type': 'text',
                              'label::English': 'OK?',
                              'label::Français': 'OK!'}],
                  'translations': ['English', 'Français']}


def test_expand_translations_null_lang():
    s1 = {'survey': [{'type': 'text',
                      'label': 'NoLang',
                      'label::English': 'EnglishLang'}],
          'translations': [None, 'English']}
    x1 = {'survey': [{'type': 'text',
                      'label': ['NoLang', 'EnglishLang']}],
          'translations': [None, 'English']}
    s1_copy = copy.deepcopy(s1)
    expand_content(s1)
    assert s1 == x1
    flatten_content(s1)
    assert s1 == s1_copy
