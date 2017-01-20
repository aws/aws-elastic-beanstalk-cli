from unittest import TestCase

from mock import patch, Mock

from ebcli.containers import dockerrun
from ebcli.containers.envvarcollector import EnvvarCollector
from ebcli.containers.multicontainer import MultiContainer
from tests.unit.containers import dummy


class TestMultiContainer(TestCase):
    def setUp(self):
        self.soln_stk = dummy.get_soln_stk()
        self.fs_handler = dummy.get_multicontainer_fs_handler()
        self.pathconfig = self.fs_handler.pathconfig
        self.fs_handler.make_docker_compose = Mock()
        self.fs_handler.dockerrun = {dockerrun.VERSION_KEY:
                                     dockerrun.VERSION_TWO}
        self.fs_handler.get_setenv_env.return_value = EnvvarCollector({'a': '3',
                                                                       'z': '0'})
        self.env = EnvvarCollector({'a': '1', 'b': '2', 'c': '5'})
        self.multicontainer = MultiContainer(fs_handler=self.fs_handler,
                                             soln_stk=self.soln_stk,
                                             opt_env=self.env)

    def test_containerize(self):
        self.multicontainer._containerize()

        make_docker_compose_args = self.fs_handler.make_docker_compose.call_args[0]
        actual_env_arg = make_docker_compose_args[0]

        # Optional --envvars has higher priority than ones set through setenv
        self.assertDictEqual({'a': '1', 'b': '2', 'z': '0', 'c': '5'}, actual_env_arg.map)
        self.assertSetEqual(set(), actual_env_arg.to_remove)

    @patch('ebcli.containers.multicontainer.commands')
    def test_up_not_allow_insecure_ssl(self, commands):
        self.multicontainer.allow_insecure_ssl = False
        self.multicontainer._up()

        commands.up.assert_called_once_with(compose_path=dummy.COMPOSE_PATH,
                                            allow_insecure_ssl=False)

    @patch('ebcli.containers.multicontainer.commands')
    def test_up_allow_insecure_ssl(self, commands):
        self.multicontainer.allow_insecure_ssl = True
        self.multicontainer._up()

        commands.up.assert_called_once_with(compose_path=dummy.COMPOSE_PATH,
                                            allow_insecure_ssl=True)

    @patch('ebcli.containers.multicontainer.MultiContainer._remove')
    @patch('ebcli.containers.multicontainer.MultiContainer._up')
    @patch('ebcli.containers.multicontainer.MultiContainer._containerize')
    def test_start(self, _containerize, _up, _remove):
        self.multicontainer.start()

        _containerize.assert_called_once_with()
        _up.assert_called_once_with()
        _remove.assert_called_once_with()

    @patch('ebcli.containers.multicontainer.fileoperations')
    def test_list_services(self, fops):
        fops._get_yaml_dict.return_value = {'a': {}, 'b': {}, 'c': {}}
        proj_name = MultiContainer.PROJ_NAME

        expected_list = ['elasticbeanstalk_a_1', 'elasticbeanstalk_b_1',
                         'elasticbeanstalk_c_1']

        self.assertListEqual(sorted(expected_list),
                             sorted(self.multicontainer.list_services()))

    @patch('ebcli.containers.multicontainer.commands')
    @patch('ebcli.containers.multicontainer.MultiContainer.list_services')
    def test_is_running_one(self, list_services, commands):
        list_services.return_value = ['a', 'b', 'c']
        commands.is_running.side_effeect = [False, False, True]

        self.assertTrue(self.multicontainer.is_running())

    @patch('ebcli.containers.multicontainer.commands')
    @patch('ebcli.containers.multicontainer.MultiContainer.list_services')
    def test_is_running_none(self, list_services, commands):
        list_services.return_value = ['a', 'b', 'c']
        commands.is_running.side_effect = [False, False, False]

        self.assertFalse(self.multicontainer.is_running())

    @patch('ebcli.containers.multicontainer.commands')
    @patch('ebcli.containers.multicontainer.MultiContainer.list_services')
    def test_remove(self, list_services, commands):
        list_services.return_value = ['a', 'b', 'c']
        self.multicontainer._remove()
        commands.rm_container.assert_any_call('a', force=True)
        commands.rm_container.assert_any_call('b', force=True)
        commands.rm_container.assert_any_call('c', force=True)
