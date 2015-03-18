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

from ..objects.exceptions import ValidationError
from ..core import fileoperations


def get_dockerrun(dockerrun_path):
    """
    Return dict representation of Dockerrun.aws.json in dockerrun_path
    Return None if Dockerrun doesn't exist at that path.
    :param dockerrun_path: str: full path to Dockerrun.aws.json
    :return: dict
    """

    try:
        return fileoperations.get_json_dict(dockerrun_path)
    except ValueError:
        err_msg = 'You provided an invalid Dockerrun.aws.json file. ' \
                  'Reason was: {}'
        raise ValidationError(err_msg.format('Invalid JSON format.'))
    except IOError:  # Dockerrun.aws.json doesn't exist
        return None
