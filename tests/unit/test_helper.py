# Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
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
import os


class EnvVarSubstitutor(object):
    def __init__(self, variable, new_value):
        self.variable = variable
        self.original_value = os.environ.get(variable)

        if new_value is not None:
            os.environ[variable] = new_value
        elif new_value is None and self.original_value is not None:
            del os.environ[variable]

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.original_value is not None:
            os.environ[self.variable] = self.original_value
        elif self.original_value is None and os.environ.get(self.variable):
            del os.environ[self.variable]
