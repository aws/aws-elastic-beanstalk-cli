# -*- coding: utf-8 -*-

# Copyright 2018 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You
# may not use this file except in compliance with the License. A copy of
# the License is located at
#
# http://aws.amazon.com/apache2.0/
#
# or in the "license" file accompanying this file. This file is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF
# ANY KIND, either express or implied. See the License for the specific
# language governing permissions and limitations under the License.
from collections import Counter

from six import iteritems
import unittest

from ebcli.operations import envvarops


class TestEnvvarOps(unittest.TestCase):

	def assertListsOfDictsEquivalent(self, ls1, ls2):
		return self.assertEqual(
			Counter(frozenset(iteritems(d)) for d in ls1),
			Counter(frozenset(iteritems(d)) for d in ls2))

	def test_sanitize_environment_variables_from_customer_input(self):
		environment_variables_input = 'DB_USER="r=o\"o\'t\"\"",DB_PAS\=SWORD="\"pass=\'\"word\""'

		self.assertEqual(
			[
				'DB_USER=r=o"o\'t',
				'DB_PAS\\=SWORD=""pass=\'"word'
			],
			envvarops.sanitize_environment_variables_from_customer_input(environment_variables_input)
		)

	def test_sanitize_environment_variables_from_customer_input_blank_key(self):
		with self.assertRaises(envvarops.InvalidSyntaxError):
			envvarops.sanitize_environment_variables_from_customer_input('=')

		with self.assertRaises(envvarops.InvalidSyntaxError):
			envvarops.sanitize_environment_variables_from_customer_input('=bar')

	def test_create_environment_variables_list_empty(self):
		options, options_to_remove = envvarops.create_environment_variables_list([])
		self.assertEqual(options, list())
		self.assertEqual(options_to_remove, list())

		options, options_to_remove = envvarops.create_environment_variables_list(
			[],
			as_option_settings=False
		)
		self.assertEqual(options, dict())
		self.assertEqual(options_to_remove, set())

	def test_create_environment_variables_list_blank_key(self):
		with self.assertRaises(envvarops.InvalidSyntaxError):
			envvarops.create_environment_variables_list(['='])

		with self.assertRaises(envvarops.InvalidSyntaxError):
			envvarops.create_environment_variables_list(['=bar'])

	def test_create_environment_variables_list_simple(self):
		namespace = 'aws:elasticbeanstalk:application:environment'

		options, options_to_remove = envvarops.create_environment_variables_list(['foo=bar'])
		self.assertListsOfDictsEquivalent(
			options,
			[
				dict(
					Namespace=namespace,
					OptionName='foo',
					Value='bar'
				)
			]
		)
		self.assertListEqual(options_to_remove, list())

		options, options_to_remove = envvarops.create_environment_variables_list(['foo=bar', 'fish=good'])
		self.assertListsOfDictsEquivalent(
			options,
			[
				dict(
					Namespace=namespace,
					OptionName='foo',
					Value='bar'
				),
				dict(
					Namespace=namespace,
					OptionName='fish',
					Value='good'
				)
			]
		)
		self.assertEqual(options_to_remove, list())

		options, options_to_remove = envvarops.create_environment_variables_list(
			['foo=bar', 'fish=good', 'trout=', 'baz='])
		self.assertListsOfDictsEquivalent(
			options,
			[
				dict(
					Namespace=namespace,
					OptionName='foo',
					Value='bar'
				),
				dict(
					Namespace=namespace,
					OptionName='fish',
					Value='good'
				)
			]
		)
		self.assertListsOfDictsEquivalent(
			options_to_remove, [
				dict(
					Namespace=namespace,
					OptionName='trout'
				),
				dict(
					Namespace=namespace,
					OptionName='baz'
				)
			]
		)

	def test_create_envvars_not_as_option_settings(self):
		options, options_to_remove = envvarops.create_environment_variables_list(
			['foo=bar'],
			as_option_settings=False
		)
		self.assertEqual(options, dict(foo='bar'))
		self.assertEqual(options_to_remove, set())

		options, options_to_remove = envvarops.create_environment_variables_list(
			['foo=bar', 'fish=good'],
			as_option_settings=False
		)
		self.assertDictEqual(options, dict(foo='bar', fish='good'))
		self.assertEqual(options_to_remove, set())

		options, options_to_remove = envvarops.create_environment_variables_list(
			['foo=bar', 'fish=good', 'trout=', 'baz='],
			as_option_settings=False
		)
		self.assertDictEqual(options, dict(foo='bar', fish='good'))
		self.assertEqual(options_to_remove, {'trout', 'baz'})

	def test_create_envvars_crazy_characters(self):
		string1 = 'http://some.url.com/?quer=true&othersutff=1'
		string2 = 'some other !@=:;#$%^&*() weird, key'

		options, options_to_remove = envvarops.create_environment_variables_list(
			[
				'foo=' + string1,
				'wierd er value='+ string2
			],
			as_option_settings=False
		)
		self.assertEqual(
			options,
			{
				'foo': string1,
				'wierd er value': string2
			}
		)
		self.assertEqual(options_to_remove, set())

	def test_create_envvars_not_bad_characters(self):
		strings = [
			'!hello',
			',hello',
			'?hello',
			';hello',
			'=hello',
			'$hello',
			'%hello',
			'😊'
		]
		for s in strings:
			options, options_to_remove = envvarops.create_environment_variables_list(
				['foo=' + s],
				as_option_settings=False
			)
			self.assertEqual(
				options,
				{
					'foo': s
				}
			)
