# Copyright 2015 Amazon.com, Inc. or its affiliates. All Rights Reserved.
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


from ..core.abstractcontroller import AbstractBaseController
from ..resources.strings import strings
from ..core import io


class ConvertDockerrunController(AbstractBaseController):
    class Meta:
        label = 'convert-dockerrun'
        stacked_on = 'labs'
        stacked_type = 'nested'
        description = strings['convert-dockkerrun.info']
        usage = 'eb labs convert-dockerrun [options...]'

    def do_command(self):
        io.echo('Version 1 file saved as Dockerrun.aws.json_backup.')
        io.echo('Dockerrun.aws.json successfully converted to Version 2.')

        io.echo()
        io.echo('To change your default platform, type "eb platform select".')