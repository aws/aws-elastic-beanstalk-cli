from ebcli.docker.container_viewmodel import ContainerViewModel, ServiceInfo
from mock import patch, Mock
from unittest import TestCase


IP = '127.0.0.1'
SERVICE_INFO0 = ServiceInfo(is_running=True,
                            cid='123',
                            ip=IP,
                            hostports=['9000', '9001'])
SERVICE_INFO1 = ServiceInfo(is_running=True,
                            cid='543',
                            ip=IP,
                            hostports=['80', '9005'])
SERVICE_INFO2 = ServiceInfo(is_running=False,
                            cid='zzz',
                            ip=IP,
                            hostports=[])
NUM_EXPOSED_HOSTPORS = 4


class TestContainerViewModel(TestCase):
    def setUp(self):
        self.service_infos = [SERVICE_INFO0, SERVICE_INFO1, SERVICE_INFO2]

        self.cnt_viewmodel = ContainerViewModel(soln_stk=Mock(),
                                                ip=IP,
                                                service_infos=self.service_infos)

    def test_get_cids_multiple(self):
        self.assertItemsEqual(['123', '543', 'zzz'],
                              self.cnt_viewmodel.get_cids())

    def test_get_cids_zero(self):
        self.cnt_viewmodel.service_infos = []
        self.assertItemsEqual([], self.cnt_viewmodel.get_cids())

    def test_get_cid_hostports_map(self):
        expected_map = {'123': ['9000', '9001'],
                        '543': ['80', '9005'],
                        'zzz': []}

        self.assertDictEqual(expected_map,
                             self.cnt_viewmodel.get_cid_hostports_map())

    def test_get_cid_hostport_pairs(self):
        expected_list = [('123', '9000'), ('123', '9001'), ('543', '80'),
                         ('543', '9005')]
        self.assertItemsEqual(expected_list,
                              self.cnt_viewmodel.get_cid_hostport_pairs())

    def test_is_running_multiple_true(self):
        self.assertTrue(self.cnt_viewmodel.is_running())

    def test_is_running_one_true(self):
        self.cnt_viewmodel.service_infos = [SERVICE_INFO0]
        self.assertTrue(self.cnt_viewmodel.is_running())

    def test_is_running_none(self):
        self.cnt_viewmodel.service_infos = []
        self.assertFalse(self.cnt_viewmodel.is_running())

    def test_num_exposed_hostports_multiple(self):
        self.assertEqual(NUM_EXPOSED_HOSTPORS,
                         self.cnt_viewmodel.num_exposed_hostports())

    def test_num_exposed_hostports_zero(self):
        self.cnt_viewmodel.service_infos = []
        self.assertEqual(0, self.cnt_viewmodel.num_exposed_hostports())


class TestServiceInfo(TestCase):
    def test_get_urls(self):
        expected = ['{}:{}'.format(IP, '9000'), '{}:{}'.format(IP, '9001')]
        self.assertListEqual(expected, SERVICE_INFO0.get_urls())

    def test_get_urls_empty(self):
        expected = []
        self.assertListEqual(expected, SERVICE_INFO2.get_urls())
