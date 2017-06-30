from unittest import TestCase
from mock import MagicMock

from docker.errors import APIError

from ebcli.bundled._compose import project, container


class TestProject(TestCase):
    def test_get_volumes_from__raises_api_error_exception(self):
        project_instance = project.Project(None, None, None)
        service_dict = {
            'name': 'myfakeservice',
            'volumes_from': ['non_existent_volume']
        }

        project_instance.get_service = MagicMock(side_effect=self._get_service__with_failure)
        container.Container.from_id = MagicMock(side_effect=self._from_id__with_failure)

        with self.assertRaises(project.ConfigurationError) as context_manager:
            project_instance.get_volumes_from(service_dict)

        exception_message = 'Service "myfakeservice" mounts volumes from "non_existent_volume", which is not the name of a service or container.'
        self.assertEqual(context_manager.exception.msg, exception_message)

    def test_get_net__raises_api_error_exception(self):
        project_instance = project.Project(None, None, None)
        service_dict = {
            'name': 'myfakeservice',
            'net': 'non_existent_net'
        }

        project.get_service_name_from_net = MagicMock(return_value='non_existent_net')
        project_instance.get_service = MagicMock(side_effect=self._get_service__with_failure)
        container.Container.from_id = MagicMock(side_effect=self._from_id__with_failure)

        with self.assertRaises(project.ConfigurationError) as context_manager:
            project_instance.get_net(service_dict)

        exception_message = 'Serivce "myfakeservice" is trying to use the network of "non_existent_net", which is not the name of a service or container.'
        self.assertEqual(context_manager.exception.msg, exception_message)

    def _get_service__with_failure(self, name):
        raise project.NoSuchService(name)

    def _from_id__with_failure(self, client, volume_name):
        raise APIError('There was an error making an API call.')
