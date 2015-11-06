# -*- coding: utf-8 -*-
"""
Presence analyzer unit tests.
"""
import os.path
import json
import datetime
import unittest

from presence_analyzer import main, views, utils
import flask

TEST_DATA_CSV = os.path.join(
    os.path.dirname(__file__), '..', '..', 'runtime', 'data', 'test_data.csv'
)


# pylint: disable=maybe-no-member, too-many-public-methods
class PresenceAnalyzerViewsTestCase(unittest.TestCase):
    """
    Views tests.
    """

    def setUp(self):
        """
        Before each test, set up a environment.
        """
        main.app.config.update({'DATA_CSV': TEST_DATA_CSV})
        self.client = main.app.test_client()

    def tearDown(self):
        """
        Get rid of unused objects after each test.
        """
        pass

    def test_mainpage(self):
        """
        Test main page redirect.
        """
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 302)
        assert resp.headers['Location'].endswith('/presence_weekday.html')

    def test_api_users(self):
        """
        Test users listing.
        """
        resp = self.client.get('/api/v1/users')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        data = json.loads(resp.data)
        self.assertEqual(len(data), 2)
        self.assertDictEqual(data[0], {u'user_id': 10, u'name': u'User 10'})

    def test_api_mean_time_weekday(self):
        """
        Test calculating mean per day of week
        """
        resp = self.client.get('/api/v1/mean_time_weekday/11')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        data = json.loads(resp.data)
        self.assertEqual(len(data), 7)
        self.assertListEqual(data[0], ['Mon', 24123.0])
        self.assertListEqual(data[6], ['Sun', 0])

    def test_api_presence_weekday(self):
        """
        Test calculating sum per day of week
        """
        resp = self.client.get('/api/v1/presence_weekday/11')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        data = json.loads(resp.data)
        self.assertEqual(len(data), 8)
        self.assertListEqual(data[0], [u'Weekday', u'Presence (s)'])
        self.assertListEqual(data[1], [u'Mon', 24123])
        self.assertListEqual(data[7], [u'Sun', 0])


class PresenceAnalyzerUtilsTestCase(unittest.TestCase):
    """
    Utility functions tests.
    """

    def setUp(self):
        """
        Before each test, set up a environment.
        """
        main.app.config.update({'DATA_CSV': TEST_DATA_CSV})

    def tearDown(self):
        """
        Get rid of unused objects after each test.
        """
        pass

    def test_get_data(self):
        """
        Test parsing of CSV file.
        """
        data = utils.get_data()
        self.assertIsInstance(data, dict)
        self.assertItemsEqual(data.keys(), [10, 11])
        sample_date = datetime.date(2013, 9, 10)
        self.assertIn(sample_date, data[10])
        self.assertItemsEqual(data[10][sample_date].keys(), ['start', 'end'])
        self.assertEqual(
            data[10][sample_date]['start'],
            datetime.time(9, 39, 5)
        )

    def test_jsonify(self):
        """
        Test if jsonify wrapper creates proper JSON object
        """

        some_dict = {'a': 'b', 'c': 'd'}

        @utils.jsonify
        def some_func():
            return some_dict
        resp = some_func()

        # if is function
        self.assertTrue(callable(utils.jsonify))
        # if got Flask Response as result
        self.assertTrue(isinstance(resp, flask.wrappers.Response))
        # if data are correct
        self.assertEqual(resp.data, json.dumps(some_dict))
        # if assigned mimetype is proper
        self.assertEqual(resp.mimetype, u'application/json')

    def test_seconds_since_midnight(self):
        """
        Test seconds counting
        """
        s_array = [(15, 8, 6), (12, 0, 0), (0, 0, 0), (23, 59, 59)]
        secs_array = [(x[0] * 3600 + x[1] * 60 + x[2], utils.seconds_since_midnight(datetime.time(*x))) for x in s_array]
        print secs_array
        for sa in secs_array:
            self.assertEqual(sa[0], sa[1])

    def test_mean(self):
        """
        Test mean function
        """
        self.assertEqual(utils.mean([]), 0)
        self.assertEqual(utils.mean([1, 2, 3, 4, 5]), 3.0)
        self.assertEqual(utils.mean([1000, 99999, 999999]), 366999.3333333333)

    def test_group_by_weekday(self):
        """
        test if grouping is right
        """
        user_id = 11
        data = utils.get_data()
        groups = [[24123], [16564], [25321], [22969, 22999], [6426], [], []]
        self.assertListEqual(groups, utils.group_by_weekday(data[user_id]))


def suite():
    """
    Default test suite.
    """
    base_suite = unittest.TestSuite()
    base_suite.addTest(unittest.makeSuite(PresenceAnalyzerViewsTestCase))
    base_suite.addTest(unittest.makeSuite(PresenceAnalyzerUtilsTestCase))
    return base_suite


if __name__ == '__main__':
    unittest.main()
