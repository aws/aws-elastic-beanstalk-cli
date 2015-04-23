from mock import patch, Mock
from unittest import TestCase

from ebcli.docker.multicontainer import MultiContainer
from ebcli.docker import dockerrun


COMPOSE_PATH = '/.elsaticbeanstalk/docker-compose.yml'


class TestMultiContainer(TestCase):
    def setUp(self):
        self.soln_stk = Mock()
        self.fs_handler = Mock()
        self.fs_handler.make_docker_compose = Mock()
        self.fs_handler.compose_path = COMPOSE_PATH
        self.fs_handler.dockerrun = {dockerrun.VERSION_KEY:
                                     dockerrun.VERSION_TWO}
        self.env = {'a': 'b'}
        self.multicontainer = MultiContainer(self.fs_handler, self.env,
                                             self.soln_stk)

    def test_containerize(self):
        self.multicontainer._containerize()
        self.fs_handler.make_docker_compose.assert_called_once_with(self.env)

    @patch('ebcli.docker.multicontainer.commands')
    def test_up(self, commands):
        self.multicontainer._up()
        commands.up.assert_called_once_with(COMPOSE_PATH)

    @patch('ebcli.docker.multicontainer.MultiContainer._remove')
    @patch('ebcli.docker.multicontainer.MultiContainer._up')
    @patch('ebcli.docker.multicontainer.MultiContainer._containerize')
    def test_start(self, _containerize, _up, _remove):
        self.multicontainer.start()

        _containerize.assert_called_once_with()
        _up.assert_called_once_with()
        _remove.assert_called_once_with()

    @patch('ebcli.docker.multicontainer.fileoperations')
    def test_list_services(self, fops):
        fops._get_yaml_dict.return_value = {'a': {}, 'b': {}, 'c': {}}
        proj_name = MultiContainer.PROJ_NAME

        expected_list = ['elasticbeanstalk_a_1', 'elasticbeanstalk_b_1',
                         'elasticbeanstalk_c_1']

        self.assertItemsEqual(expected_list,
                              self.multicontainer.list_services())

    @patch('ebcli.docker.multicontainer.commands')
    @patch('ebcli.docker.multicontainer.MultiContainer.list_services')
    def test_is_running_one(self, list_services, commands):
        list_services.return_value = ['a', 'b', 'c']
        commands.is_running.side_effeect = [False, False, True]

        self.assertTrue(self.multicontainer.is_running())

    @patch('ebcli.docker.multicontainer.commands')
    @patch('ebcli.docker.multicontainer.MultiContainer.list_services')
    def test_is_running_none(self, list_services, commands):
        list_services.return_value = ['a', 'b', 'c']
        commands.is_running.side_effect = [False, False, False]

        self.assertFalse(self.multicontainer.is_running())

    @patch('ebcli.docker.multicontainer.commands')
    @patch('ebcli.docker.multicontainer.MultiContainer.list_services')
    def test_remove(self, list_services, commands):
        list_services.return_value = ['a', 'b', 'c']
        self.multicontainer._remove()
        commands.rm_container.assert_any_call('a', force=True)
        commands.rm_container.assert_any_call('b', force=True)
        commands.rm_container.assert_any_call('c', force=True)
