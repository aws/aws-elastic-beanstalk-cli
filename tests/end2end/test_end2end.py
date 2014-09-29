# Copyright 2014 Amazon.com, Inc. or its affiliates. All Rights Reserved.
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

"""
Test order
init - make sure application gets created and file is good
create - make sure environment is created

do tests on basic environment operations
    events
    status
    status verbose
    setenv
    status verbose - make sure env was set
    logs
    scale
    status verbose - make sure more instances were launched


    make a change
    deploy

    Cant really test for open or console because a CI wont be able to open browsers

list
terminate
delete

"""