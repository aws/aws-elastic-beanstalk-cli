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

import datetime
from dateutil.tz import tzutc
from botocore.compat import six
from collections import defaultdict
"""
Mock responses for Integration tests.
These responses are designed to replace the requests/httplib
make_requests method.
We want mocks to be as low level as possible in order to test
integration with botocore.
"""

mock = None
queue_dict = defaultdict(lambda: defaultdict(six.moves.queue.Queue))
calls = defaultdict(lambda: defaultdict(list))


def handle_response(operational_model, *args, **kwargs):
    service = operational_model._service_model.service_name
    operation = operational_model._operation_model['name']
    try:
        body = args[0]['body']
    except:
        body = 'Unknown'
    calls[service][operation].append(body)
    try:
        return dequeue(service, operation)
    except six.moves.queue.Empty:
        # Get standard responses
        if service == 'elasticbeanstalk':
            handler = MockBeanstalk
        elif service == 's3':
            handler = MockS3
        else:
            raise NotImplementedError('Service "{0}" and Operation "{1}" not '
                                      'implemented'.format(service, operation))
        return handler(operation, *args, **kwargs).handle()


def enqueue(service, operation, response, http_code=200, http_object=None):
    if not http_object:
        http_object = Http(http_code)
    queue_dict[service][operation].put_nowait((http_object, response))


def dequeue(service, operation):
    return queue_dict[service][operation].get_nowait()


def reset():
    global queue_dict, calls
    queue_dict = defaultdict(lambda: defaultdict(six.moves.queue.Queue))
    calls = defaultdict(lambda: defaultdict(list))


def called_with(service, operation, body):
    for b in calls[service][operation]:
        if b == body:
            return True

    return False


def get_calls(service, operation):
    return calls[service][operation]


class Http(object):
    def __init__(self, status_code):
        self.status_code = status_code


class MockService(object):
    def __init__(self, operation, *args, **kwargs):
        self.operation = operation
        self.args = args
        self.kwargs = kwargs
        try:
            self.body = self.args[0]['body']
        except KeyError:
            self.body = None

    def handle(self):
        try:
            handler = getattr(self, self.operation)
            return handler()
        except AttributeError:
            raise NotImplementedError(self.operation + ' not yet implemented.')


class MockBeanstalk(MockService):
    """
    Mock of the beanstalk service.
    We will assume the following things:
    bad-env is a none existing environment
    my-env is a good environment
    single-env is a single instance environment


    The function names need to match the service operation call exactly.
    Camel-case and all.
    """

    def DescribeConfigurationSettings(self):
        if self.body['EnvironmentName'] == 'my-env':
            return Http(200), standard_describe_configuration_settings()

        raise NotImplementedError

    def ListAvailableSolutionStacks(self):
        return (Http(200), {
            u'SolutionStacks': ['64bit Amazon Linux 2014.09 v1.2.0 running PHP 5.5', '32bit Amazon Linux 2014.09 v1.2.0 running PHP 5.5', '64bit Amazon Linux 2014.09 v1.2.0 running PHP 5.4', '32bit Amazon Linux 2014.09 v1.2.0 running PHP 5.4', '64bit Amazon Linux 2014.09 v1.1.0 running PHP 5.5', '64bit Amazon Linux 2014.09 v1.1.0 running PHP 5.4', '64bit Amazon Linux 2014.09 v1.0.9 running PHP 5.5', '64bit Amazon Linux 2014.09 v1.0.9 running PHP 5.4', '64bit Amazon Linux 2014.09 v1.0.8 running PHP 5.5', '64bit Amazon Linux 2014.09 v1.0.8 running PHP 5.4', '64bit Amazon Linux 2014.03 v1.1.0 running PHP 5.5', '32bit Amazon Linux 2014.03 v1.1.0 running PHP 5.5', '64bit Amazon Linux 2014.03 v1.1.0 running PHP 5.4', '32bit Amazon Linux 2014.03 v1.1.0 running PHP 5.4', '64bit Amazon Linux 2014.03 v1.0.9 running PHP 5.5', '32bit Amazon Linux 2014.03 v1.0.9 running PHP 5.5', '64bit Amazon Linux 2014.03 v1.0.9 running PHP 5.4', '32bit Amazon Linux 2014.03 v1.0.9 running PHP 5.4', '64bit Amazon Linux 2014.03 v1.0.7 running PHP 5.5', '32bit Amazon Linux 2014.03 v1.0.7 running PHP 5.5', '64bit Amazon Linux 2014.03 v1.0.7 running PHP 5.4', '32bit Amazon Linux 2014.03 v1.0.7 running PHP 5.4', '64bit Amazon Linux 2014.03 v1.0.4 running PHP 5.5', '64bit Amazon Linux 2014.03 v1.0.4 running PHP 5.4', '64bit Amazon Linux 2014.03 v1.0.3 running PHP 5.5', '64bit Amazon Linux 2014.03 v1.0.3 running PHP 5.4', '32bit Amazon Linux 2014.03 v1.0.3 running PHP 5.5', '32bit Amazon Linux 2014.03 v1.0.3 running PHP 5.4', '32bit Amazon Linux running PHP 5.3', '64bit Amazon Linux running PHP 5.3', '64bit Amazon Linux 2014.09 v1.2.0 running Node.js', '32bit Amazon Linux 2014.09 v1.2.0 running Node.js', '64bit Amazon Linux 2014.09 v1.0.8 running Node.js', '64bit Amazon Linux 2014.03 v1.1.0 running Node.js', '32bit Amazon Linux 2014.03 v1.1.0 running Node.js', '64bit Amazon Linux 2014.03 v1.0.7 running Node.js', '32bit Amazon Linux 2014.03 v1.0.7 running Node.js', '64bit Windows Server 2008 R2 running IIS 7.5', '64bit Windows Server 2012 running IIS 8', '64bit Windows Server 2012 R2 running IIS 8.5', '64bit Windows Server Core 2012 R2 running IIS 8.5', '64bit Amazon Linux 2014.09 v1.2.0 running Tomcat 8 Java 8', '64bit Amazon Linux 2014.09 v1.2.0 running Tomcat 7 Java 7', '32bit Amazon Linux 2014.09 v1.2.0 running Tomcat 7 Java 7', '64bit Amazon Linux 2014.09 v1.2.0 running Tomcat 7 Java 6', '32bit Amazon Linux 2014.09 v1.2.0 running Tomcat 7 Java 6', '64bit Amazon Linux 2014.09 v1.0.0 running Tomcat 8 Java 8', '64bit Amazon Linux 2014.09 v1.0.9 running Tomcat 7 Java 7', '64bit Amazon Linux 2014.09 v1.0.9 running Tomcat 7 Java 6', '64bit Amazon Linux 2014.09 v1.0.8 running Tomcat 7 Java 7', '64bit Amazon Linux 2014.09 v1.0.8 running Tomcat 7 Java 6', '64bit Amazon Linux 2014.03 v1.1.0 running Tomcat 7 Java 7', '32bit Amazon Linux 2014.03 v1.1.0 running Tomcat 7 Java 7', '64bit Amazon Linux 2014.03 v1.1.0 running Tomcat 7 Java 6', '32bit Amazon Linux 2014.03 v1.1.0 running Tomcat 7 Java 6', '64bit Amazon Linux 2014.03 v1.0.9 running Tomcat 7 Java 7', '32bit Amazon Linux 2014.03 v1.0.9 running Tomcat 7 Java 7', '64bit Amazon Linux 2014.03 v1.0.9 running Tomcat 7 Java 6', '32bit Amazon Linux 2014.03 v1.0.9 running Tomcat 7 Java 6', '64bit Amazon Linux 2014.03 v1.0.7 running Tomcat 7 Java 7', '32bit Amazon Linux 2014.03 v1.0.7 running Tomcat 7 Java 7', '64bit Amazon Linux 2014.03 v1.0.7 running Tomcat 7 Java 6', '32bit Amazon Linux 2014.03 v1.0.7 running Tomcat 7 Java 6', '64bit Amazon Linux 2014.03 v1.0.4 running Tomcat 7 Java 7', '64bit Amazon Linux 2014.03 v1.0.4 running Tomcat 7 Java 6', '32bit Amazon Linux running Tomcat 7', '64bit Amazon Linux running Tomcat 7', '32bit Amazon Linux running Tomcat 6', '64bit Amazon Linux running Tomcat 6', '64bit Amazon Linux 2014.09 v1.2.0 running Python 2.7', '32bit Amazon Linux 2014.09 v1.2.0 running Python 2.7', '64bit Amazon Linux 2014.09 v1.2.0 running Python', '32bit Amazon Linux 2014.09 v1.2.0 running Python', '64bit Amazon Linux 2014.09 v1.1.0 running Python 2.7', '64bit Amazon Linux 2014.09 v1.1.0 running Python', '64bit Amazon Linux 2014.09 v1.0.9 running Python 2.7', '64bit Amazon Linux 2014.09 v1.0.9 running Python', '64bit Amazon Linux 2014.03 v1.1.0 running Python 2.7', '32bit Amazon Linux 2014.03 v1.1.0 running Python 2.7', '64bit Amazon Linux 2014.03 v1.1.0 running Python', '32bit Amazon Linux 2014.03 v1.1.0 running Python', '64bit Amazon Linux 2014.03 v1.0.9 running Python 2.7', '32bit Amazon Linux 2014.03 v1.0.9 running Python 2.7', '64bit Amazon Linux 2014.03 v1.0.9 running Python', '32bit Amazon Linux 2014.03 v1.0.9 running Python', '64bit Amazon Linux 2014.03 v1.0.7 running Python 2.7', '32bit Amazon Linux 2014.03 v1.0.7 running Python 2.7', '64bit Amazon Linux 2014.03 v1.0.7 running Python', '32bit Amazon Linux 2014.03 v1.0.7 running Python', '64bit Amazon Linux 2014.03 v1.0.4 running Python 2.7', '64bit Amazon Linux 2014.03 v1.0.4 running Python', '64bit Amazon Linux 2014.03 v1.0.3 running Python 2.7', '32bit Amazon Linux 2014.03 v1.0.3 running Python 2.7', '64bit Amazon Linux 2014.03 v1.0.3 running Python', '32bit Amazon Linux 2014.03 v1.0.3 running Python', '32bit Amazon Linux running Python', '64bit Amazon Linux running Python', '64bit Amazon Linux 2014.09 v1.2.0 running Ruby 2.1 (Puma)', '64bit Amazon Linux 2014.09 v1.2.0 running Ruby 2.1 (Passenger Standalone)', '64bit Amazon Linux 2014.09 v1.2.0 running Ruby 2.0 (Puma)', '64bit Amazon Linux 2014.09 v1.2.0 running Ruby 2.0 (Passenger Standalone)', '64bit Amazon Linux 2014.09 v1.2.0 running Ruby 1.9.3', '32bit Amazon Linux 2014.09 v1.2.0 running Ruby 1.9.3', '64bit Amazon Linux 2014.09 v1.0.9 running Ruby 2.1 (Puma)', '64bit Amazon Linux 2014.09 v1.0.9 running Ruby 2.1 (Passenger Standalone)', '64bit Amazon Linux 2014.09 v1.0.9 running Ruby 2.0 (Puma)', '64bit Amazon Linux 2014.09 v1.0.9 running Ruby 2.0 (Passenger Standalone)', '64bit Amazon Linux 2014.09 v1.0.9 running Ruby 1.9.3', '64bit Amazon Linux 2014.03 v1.1.0 running Ruby 2.1 (Passenger Standalone)', '64bit Amazon Linux 2014.03 v1.1.0 running Ruby 2.1 (Puma)', '64bit Amazon Linux 2014.03 v1.1.0 running Ruby 2.0 (Passenger Standalone)', '64bit Amazon Linux 2014.03 v1.1.0 running Ruby 2.0 (Puma)', '64bit Amazon Linux 2014.03 v1.1.0 running Ruby 1.9.3', '32bit Amazon Linux 2014.03 v1.1.0 running Ruby 1.9.3', '64bit Amazon Linux 2014.03 v1.0.9 running Ruby 2.1 (Puma)', '64bit Amazon Linux 2014.03 v1.0.9 running Ruby 2.1 (Passenger Standalone)', '64bit Amazon Linux 2014.03 v1.0.9 running Ruby 2.0 (Puma)', '64bit Amazon Linux 2014.03 v1.0.9 running Ruby 2.0 (Passenger Standalone)', '64bit Amazon Linux 2014.03 v1.0.9 running Ruby 1.9.3', '32bit Amazon Linux 2014.03 v1.0.9 running Ruby 1.9.3', '64bit Amazon Linux 2014.03 v1.0.7 running Ruby 2.1 (Puma)', '64bit Amazon Linux 2014.03 v1.0.7 running Ruby 2.1 (Passenger Standalone)', '64bit Amazon Linux 2014.03 v1.0.7 running Ruby 2.0 (Puma)', '64bit Amazon Linux 2014.03 v1.0.7 running Ruby 2.0 (Passenger Standalone)', '64bit Amazon Linux 2014.03 v1.0.7 running Ruby 1.9.3', '32bit Amazon Linux 2014.03 v1.0.7 running Ruby 1.9.3', '64bit Amazon Linux 2014.03 v1.0.0 running Ruby 2.1 (Puma)', '64bit Amazon Linux 2014.03 v1.0.0 running Ruby 2.1 (Passenger Standalone)', '64bit Amazon Linux 2014.03 v1.0.5 running Ruby 2.0 (Puma)', '64bit Amazon Linux 2014.03 v1.0.4 running Ruby 2.0 (Puma)', '64bit Amazon Linux 2014.03 v1.0.4 running Ruby 2.0 (Passenger Standalone)', '64bit Amazon Linux 2014.03 v1.0.3 running Ruby 2.0 (Passenger Standalone)', '64bit Amazon Linux 2014.09 v1.2.0 running Docker 1.3.3', '64bit Amazon Linux 2014.09 v1.0.9 running Docker 1.2.0', '64bit Amazon Linux 2014.09 v1.0.8 running Docker 1.2.0', '64bit Amazon Linux 2014.03 v1.0.9 running Docker 1.0.0', '64bit Amazon Linux 2014.03 v1.0.7 running Docker 1.0.0', '64bit Debian jessie v1.2.0 running GlassFish 4.1 Java 8 (Preconfigured - Docker)', '64bit Debian jessie v1.2.0 running GlassFish 4.0 Java 7 (Preconfigured - Docker)', '64bit Debian jessie v1.0.0 running GlassFish 4.1 Java 8 (Preconfigured - Docker)', '64bit Debian jessie v1.0.0 running GlassFish 4.0 Java 7 (Preconfigured - Docker)', '64bit Debian jessie v1.2.0 running Python 3.4 (Preconfigured - Docker)', '64bit Debian jessie v1.0.0 running Python 3.4 (Preconfigured - Docker)', '64bit Debian jessie v1.2.0 running Go 1.4 (Preconfigured - Docker)', '64bit Debian jessie v1.2.0 running Go 1.3 (Preconfigured - Docker)'], 'ResponseMetadata': {'HTTPStatusCode': 200, 'RequestId': '6f767a9a-c6a0-11e4-8956-c1c4d272c950'}, u'SolutionStackDetails': [{u'PermittedFileTypes': ['zip'], u'SolutionStackName': '64bit Amazon Linux 2014.09 v1.2.0 running PHP 5.5'}, {u'PermittedFileTypes': ['zip'], u'SolutionStackName': '32bit Amazon Linux 2014.09 v1.2.0 running PHP 5.5'}, {u'PermittedFileTypes': ['zip'], u'SolutionStackName': '64bit Amazon Linux 2014.09 v1.2.0 running PHP 5.4'}, {u'PermittedFileTypes': ['zip'], u'SolutionStackName': '32bit Amazon Linux 2014.09 v1.2.0 running PHP 5.4'}, {u'PermittedFileTypes': ['zip'], u'SolutionStackName': '64bit Amazon Linux 2014.09 v1.1.0 running PHP 5.5'}, {u'PermittedFileTypes': ['zip'], u'SolutionStackName': '64bit Amazon Linux 2014.09 v1.1.0 running PHP 5.4'}, {u'PermittedFileTypes': ['zip'], u'SolutionStackName': '64bit Amazon Linux 2014.09 v1.0.9 running PHP 5.5'}, {u'PermittedFileTypes': ['zip'], u'SolutionStackName': '64bit Amazon Linux 2014.09 v1.0.9 running PHP 5.4'}, {u'PermittedFileTypes': ['zip'], u'SolutionStackName': '64bit Amazon Linux 2014.09 v1.0.8 running PHP 5.5'}, {u'PermittedFileTypes': ['zip'], u'SolutionStackName': '64bit Amazon Linux 2014.09 v1.0.8 running PHP 5.4'}, {u'PermittedFileTypes': ['zip'], u'SolutionStackName': '64bit Amazon Linux 2014.03 v1.1.0 running PHP 5.5'}, {u'PermittedFileTypes': ['zip'], u'SolutionStackName': '32bit Amazon Linux 2014.03 v1.1.0 running PHP 5.5'}, {u'PermittedFileTypes': ['zip'], u'SolutionStackName': '64bit Amazon Linux 2014.03 v1.1.0 running PHP 5.4'}, {u'PermittedFileTypes': ['zip'], u'SolutionStackName': '32bit Amazon Linux 2014.03 v1.1.0 running PHP 5.4'}, {u'PermittedFileTypes': ['zip'], u'SolutionStackName': '64bit Amazon Linux 2014.03 v1.0.9 running PHP 5.5'}, {u'PermittedFileTypes': ['zip'], u'SolutionStackName': '32bit Amazon Linux 2014.03 v1.0.9 running PHP 5.5'}, {u'PermittedFileTypes': ['zip'], u'SolutionStackName': '64bit Amazon Linux 2014.03 v1.0.9 running PHP 5.4'}, {u'PermittedFileTypes': ['zip'], u'SolutionStackName': '32bit Amazon Linux 2014.03 v1.0.9 running PHP 5.4'}, {u'PermittedFileTypes': ['zip'], u'SolutionStackName': '64bit Amazon Linux 2014.03 v1.0.7 running PHP 5.5'}, {u'PermittedFileTypes': ['zip'], u'SolutionStackName': '32bit Amazon Linux 2014.03 v1.0.7 running PHP 5.5'}, {u'PermittedFileTypes': ['zip'], u'SolutionStackName': '64bit Amazon Linux 2014.03 v1.0.7 running PHP 5.4'}, {u'PermittedFileTypes': ['zip'], u'SolutionStackName': '32bit Amazon Linux 2014.03 v1.0.7 running PHP 5.4'}, {u'PermittedFileTypes': ['zip'], u'SolutionStackName': '64bit Amazon Linux 2014.03 v1.0.4 running PHP 5.5'}, {u'PermittedFileTypes': ['zip'], u'SolutionStackName': '64bit Amazon Linux 2014.03 v1.0.4 running PHP 5.4'}, {u'PermittedFileTypes': ['zip'], u'SolutionStackName': '64bit Amazon Linux 2014.03 v1.0.3 running PHP 5.5'}, {u'PermittedFileTypes': ['zip'], u'SolutionStackName': '64bit Amazon Linux 2014.03 v1.0.3 running PHP 5.4'}, {u'PermittedFileTypes': ['zip'], u'SolutionStackName': '32bit Amazon Linux 2014.03 v1.0.3 running PHP 5.5'}, {u'PermittedFileTypes': ['zip'], u'SolutionStackName': '32bit Amazon Linux 2014.03 v1.0.3 running PHP 5.4'}, {u'PermittedFileTypes': ['zip'], u'SolutionStackName': '32bit Amazon Linux running PHP 5.3'}, {u'PermittedFileTypes': ['zip'], u'SolutionStackName': '64bit Amazon Linux running PHP 5.3'}, {u'PermittedFileTypes': ['zip'], u'SolutionStackName': '64bit Amazon Linux 2014.09 v1.2.0 running Node.js'}, {u'PermittedFileTypes': ['zip'], u'SolutionStackName': '32bit Amazon Linux 2014.09 v1.2.0 running Node.js'}, {u'PermittedFileTypes': ['zip'], u'SolutionStackName': '64bit Amazon Linux 2014.09 v1.0.8 running Node.js'}, {u'PermittedFileTypes': ['zip'], u'SolutionStackName': '64bit Amazon Linux 2014.03 v1.1.0 running Node.js'}, {u'PermittedFileTypes': ['zip'], u'SolutionStackName': '32bit Amazon Linux 2014.03 v1.1.0 running Node.js'}, {u'PermittedFileTypes': ['zip'], u'SolutionStackName': '64bit Amazon Linux 2014.03 v1.0.7 running Node.js'}, {u'PermittedFileTypes': ['zip'], u'SolutionStackName': '32bit Amazon Linux 2014.03 v1.0.7 running Node.js'}, {u'PermittedFileTypes': ['zip'], u'SolutionStackName': '64bit Windows Server 2008 R2 running IIS 7.5'}, {u'PermittedFileTypes': ['zip'], u'SolutionStackName': '64bit Windows Server 2012 running IIS 8'}, {u'PermittedFileTypes': ['zip'], u'SolutionStackName': '64bit Windows Server 2012 R2 running IIS 8.5'}, {u'PermittedFileTypes': ['zip'], u'SolutionStackName': '64bit Windows Server Core 2012 R2 running IIS 8.5'}, {u'PermittedFileTypes': ['zip', 'war'], u'SolutionStackName': '64bit Amazon Linux 2014.09 v1.2.0 running Tomcat 8 Java 8'}, {u'PermittedFileTypes': ['zip', 'war'], u'SolutionStackName': '64bit Amazon Linux 2014.09 v1.2.0 running Tomcat 7 Java 7'}, {u'PermittedFileTypes': ['zip', 'war'], u'SolutionStackName': '32bit Amazon Linux 2014.09 v1.2.0 running Tomcat 7 Java 7'}, {u'PermittedFileTypes': ['zip', 'war'], u'SolutionStackName': '64bit Amazon Linux 2014.09 v1.2.0 running Tomcat 7 Java 6'}, {u'PermittedFileTypes': ['zip', 'war'], u'SolutionStackName': '32bit Amazon Linux 2014.09 v1.2.0 running Tomcat 7 Java 6'}, {u'PermittedFileTypes': ['zip', 'war'], u'SolutionStackName': '64bit Amazon Linux 2014.09 v1.0.0 running Tomcat 8 Java 8'}, {u'PermittedFileTypes': ['zip', 'war'], u'SolutionStackName': '64bit Amazon Linux 2014.09 v1.0.9 running Tomcat 7 Java 7'}, {u'PermittedFileTypes': ['zip', 'war'], u'SolutionStackName': '64bit Amazon Linux 2014.09 v1.0.9 running Tomcat 7 Java 6'}, {u'PermittedFileTypes': ['zip', 'war'], u'SolutionStackName': '64bit Amazon Linux 2014.09 v1.0.8 running Tomcat 7 Java 7'}, {u'PermittedFileTypes': ['zip', 'war'], u'SolutionStackName': '64bit Amazon Linux 2014.09 v1.0.8 running Tomcat 7 Java 6'}, {u'PermittedFileTypes': ['zip', 'war'], u'SolutionStackName': '64bit Amazon Linux 2014.03 v1.1.0 running Tomcat 7 Java 7'}, {u'PermittedFileTypes': ['zip', 'war'], u'SolutionStackName': '32bit Amazon Linux 2014.03 v1.1.0 running Tomcat 7 Java 7'}, {u'PermittedFileTypes': ['zip', 'war'], u'SolutionStackName': '64bit Amazon Linux 2014.03 v1.1.0 running Tomcat 7 Java 6'}, {u'PermittedFileTypes': ['zip', 'war'], u'SolutionStackName': '32bit Amazon Linux 2014.03 v1.1.0 running Tomcat 7 Java 6'}, {u'PermittedFileTypes': ['zip', 'war'], u'SolutionStackName': '64bit Amazon Linux 2014.03 v1.0.9 running Tomcat 7 Java 7'}, {u'PermittedFileTypes': ['zip', 'war'], u'SolutionStackName': '32bit Amazon Linux 2014.03 v1.0.9 running Tomcat 7 Java 7'}, {u'PermittedFileTypes': ['zip', 'war'], u'SolutionStackName': '64bit Amazon Linux 2014.03 v1.0.9 running Tomcat 7 Java 6'}, {u'PermittedFileTypes': ['zip', 'war'], u'SolutionStackName': '32bit Amazon Linux 2014.03 v1.0.9 running Tomcat 7 Java 6'}, {u'PermittedFileTypes': ['zip', 'war'], u'SolutionStackName': '64bit Amazon Linux 2014.03 v1.0.7 running Tomcat 7 Java 7'}, {u'PermittedFileTypes': ['zip', 'war'], u'SolutionStackName': '32bit Amazon Linux 2014.03 v1.0.7 running Tomcat 7 Java 7'}, {u'PermittedFileTypes': ['zip', 'war'], u'SolutionStackName': '64bit Amazon Linux 2014.03 v1.0.7 running Tomcat 7 Java 6'}, {u'PermittedFileTypes': ['zip', 'war'], u'SolutionStackName': '32bit Amazon Linux 2014.03 v1.0.7 running Tomcat 7 Java 6'}, {u'PermittedFileTypes': ['war', 'zip'], u'SolutionStackName': '64bit Amazon Linux 2014.03 v1.0.4 running Tomcat 7 Java 7'}, {u'PermittedFileTypes': ['war', 'zip'], u'SolutionStackName': '64bit Amazon Linux 2014.03 v1.0.4 running Tomcat 7 Java 6'}, {u'PermittedFileTypes': ['war', 'zip'], u'SolutionStackName': '32bit Amazon Linux running Tomcat 7'}, {u'PermittedFileTypes': ['war', 'zip'], u'SolutionStackName': '64bit Amazon Linux running Tomcat 7'}, {u'PermittedFileTypes': ['war', 'zip'], u'SolutionStackName': '32bit Amazon Linux running Tomcat 6'}, {u'PermittedFileTypes': ['war', 'zip'], u'SolutionStackName': '64bit Amazon Linux running Tomcat 6'}, {u'PermittedFileTypes': ['zip'], u'SolutionStackName': '64bit Amazon Linux 2014.09 v1.2.0 running Python 2.7'}, {u'PermittedFileTypes': ['zip'], u'SolutionStackName': '32bit Amazon Linux 2014.09 v1.2.0 running Python 2.7'}, {u'PermittedFileTypes': ['zip'], u'SolutionStackName': '64bit Amazon Linux 2014.09 v1.2.0 running Python'}, {u'PermittedFileTypes': ['zip'], u'SolutionStackName': '32bit Amazon Linux 2014.09 v1.2.0 running Python'}, {u'PermittedFileTypes': ['zip'], u'SolutionStackName': '64bit Amazon Linux 2014.09 v1.1.0 running Python 2.7'}, {u'PermittedFileTypes': ['zip'], u'SolutionStackName': '64bit Amazon Linux 2014.09 v1.1.0 running Python'}, {u'PermittedFileTypes': ['zip'], u'SolutionStackName': '64bit Amazon Linux 2014.09 v1.0.9 running Python 2.7'}, {u'PermittedFileTypes': ['zip'], u'SolutionStackName': '64bit Amazon Linux 2014.09 v1.0.9 running Python'}, {u'PermittedFileTypes': ['zip'], u'SolutionStackName': '64bit Amazon Linux 2014.03 v1.1.0 running Python 2.7'}, {u'PermittedFileTypes': ['zip'], u'SolutionStackName': '32bit Amazon Linux 2014.03 v1.1.0 running Python 2.7'}, {u'PermittedFileTypes': ['zip'], u'SolutionStackName': '64bit Amazon Linux 2014.03 v1.1.0 running Python'}, {u'PermittedFileTypes': ['zip'], u'SolutionStackName': '32bit Amazon Linux 2014.03 v1.1.0 running Python'}, {u'PermittedFileTypes': ['zip'], u'SolutionStackName': '64bit Amazon Linux 2014.03 v1.0.9 running Python 2.7'}, {u'PermittedFileTypes': ['zip'], u'SolutionStackName': '32bit Amazon Linux 2014.03 v1.0.9 running Python 2.7'}, {u'PermittedFileTypes': ['zip'], u'SolutionStackName': '64bit Amazon Linux 2014.03 v1.0.9 running Python'}, {u'PermittedFileTypes': ['zip'], u'SolutionStackName': '32bit Amazon Linux 2014.03 v1.0.9 running Python'}, {u'PermittedFileTypes': ['zip'], u'SolutionStackName': '64bit Amazon Linux 2014.03 v1.0.7 running Python 2.7'}, {u'PermittedFileTypes': ['zip'], u'SolutionStackName': '32bit Amazon Linux 2014.03 v1.0.7 running Python 2.7'}, {u'PermittedFileTypes': ['zip'], u'SolutionStackName': '64bit Amazon Linux 2014.03 v1.0.7 running Python'}, {u'PermittedFileTypes': ['zip'], u'SolutionStackName': '32bit Amazon Linux 2014.03 v1.0.7 running Python'}, {u'PermittedFileTypes': ['zip'], u'SolutionStackName': '64bit Amazon Linux 2014.03 v1.0.4 running Python 2.7'}, {u'PermittedFileTypes': ['zip'], u'SolutionStackName': '64bit Amazon Linux 2014.03 v1.0.4 running Python'}, {u'PermittedFileTypes': ['zip'], u'SolutionStackName': '64bit Amazon Linux 2014.03 v1.0.3 running Python 2.7'}, {u'PermittedFileTypes': ['zip'], u'SolutionStackName': '32bit Amazon Linux 2014.03 v1.0.3 running Python 2.7'}, {u'PermittedFileTypes': ['zip'], u'SolutionStackName': '64bit Amazon Linux 2014.03 v1.0.3 running Python'}, {u'PermittedFileTypes': ['zip'], u'SolutionStackName': '32bit Amazon Linux 2014.03 v1.0.3 running Python'}, {u'PermittedFileTypes': ['zip'], u'SolutionStackName': '32bit Amazon Linux running Python'}, {u'PermittedFileTypes': ['zip'], u'SolutionStackName': '64bit Amazon Linux running Python'}, {u'PermittedFileTypes': ['zip'], u'SolutionStackName': '64bit Amazon Linux 2014.09 v1.2.0 running Ruby 2.1 (Puma)'}, {u'PermittedFileTypes': ['zip'], u'SolutionStackName': '64bit Amazon Linux 2014.09 v1.2.0 running Ruby 2.1 (Passenger Standalone)'}, {u'PermittedFileTypes': ['zip'], u'SolutionStackName': '64bit Amazon Linux 2014.09 v1.2.0 running Ruby 2.0 (Puma)'}, {u'PermittedFileTypes': ['zip'], u'SolutionStackName': '64bit Amazon Linux 2014.09 v1.2.0 running Ruby 2.0 (Passenger Standalone)'}, {u'PermittedFileTypes': ['zip'], u'SolutionStackName': '64bit Amazon Linux 2014.09 v1.2.0 running Ruby 1.9.3'}, {u'PermittedFileTypes': ['zip'], u'SolutionStackName': '32bit Amazon Linux 2014.09 v1.2.0 running Ruby 1.9.3'}, {u'PermittedFileTypes': ['zip'], u'SolutionStackName': '64bit Amazon Linux 2014.09 v1.0.9 running Ruby 2.1 (Puma)'}, {u'PermittedFileTypes': ['zip'], u'SolutionStackName': '64bit Amazon Linux 2014.09 v1.0.9 running Ruby 2.1 (Passenger Standalone)'}, {u'PermittedFileTypes': ['zip'], u'SolutionStackName': '64bit Amazon Linux 2014.09 v1.0.9 running Ruby 2.0 (Puma)'}, {u'PermittedFileTypes': ['zip'], u'SolutionStackName': '64bit Amazon Linux 2014.09 v1.0.9 running Ruby 2.0 (Passenger Standalone)'}, {u'PermittedFileTypes': ['zip'], u'SolutionStackName': '64bit Amazon Linux 2014.09 v1.0.9 running Ruby 1.9.3'}, {u'PermittedFileTypes': ['zip'], u'SolutionStackName': '64bit Amazon Linux 2014.03 v1.1.0 running Ruby 2.1 (Passenger Standalone)'}, {u'PermittedFileTypes': ['zip'], u'SolutionStackName': '64bit Amazon Linux 2014.03 v1.1.0 running Ruby 2.1 (Puma)'}, {u'PermittedFileTypes': ['zip'], u'SolutionStackName': '64bit Amazon Linux 2014.03 v1.1.0 running Ruby 2.0 (Passenger Standalone)'}, {u'PermittedFileTypes': ['zip'], u'SolutionStackName': '64bit Amazon Linux 2014.03 v1.1.0 running Ruby 2.0 (Puma)'}, {u'PermittedFileTypes': ['zip'], u'SolutionStackName': '64bit Amazon Linux 2014.03 v1.1.0 running Ruby 1.9.3'}, {u'PermittedFileTypes': ['zip'], u'SolutionStackName': '32bit Amazon Linux 2014.03 v1.1.0 running Ruby 1.9.3'}, {u'PermittedFileTypes': ['zip'], u'SolutionStackName': '64bit Amazon Linux 2014.03 v1.0.9 running Ruby 2.1 (Puma)'}, {u'PermittedFileTypes': ['zip'], u'SolutionStackName': '64bit Amazon Linux 2014.03 v1.0.9 running Ruby 2.1 (Passenger Standalone)'}, {u'PermittedFileTypes': ['zip'], u'SolutionStackName': '64bit Amazon Linux 2014.03 v1.0.9 running Ruby 2.0 (Puma)'}, {u'PermittedFileTypes': ['zip'], u'SolutionStackName': '64bit Amazon Linux 2014.03 v1.0.9 running Ruby 2.0 (Passenger Standalone)'}, {u'PermittedFileTypes': ['zip'], u'SolutionStackName': '64bit Amazon Linux 2014.03 v1.0.9 running Ruby 1.9.3'}, {u'PermittedFileTypes': ['zip'], u'SolutionStackName': '32bit Amazon Linux 2014.03 v1.0.9 running Ruby 1.9.3'}, {u'PermittedFileTypes': ['zip'], u'SolutionStackName': '64bit Amazon Linux 2014.03 v1.0.7 running Ruby 2.1 (Puma)'}, {u'PermittedFileTypes': ['zip'], u'SolutionStackName': '64bit Amazon Linux 2014.03 v1.0.7 running Ruby 2.1 (Passenger Standalone)'}, {u'PermittedFileTypes': ['zip'], u'SolutionStackName': '64bit Amazon Linux 2014.03 v1.0.7 running Ruby 2.0 (Puma)'}, {u'PermittedFileTypes': ['zip'], u'SolutionStackName': '64bit Amazon Linux 2014.03 v1.0.7 running Ruby 2.0 (Passenger Standalone)'}, {u'PermittedFileTypes': ['zip'], u'SolutionStackName': '64bit Amazon Linux 2014.03 v1.0.7 running Ruby 1.9.3'}, {u'PermittedFileTypes': ['zip'], u'SolutionStackName': '32bit Amazon Linux 2014.03 v1.0.7 running Ruby 1.9.3'}, {u'PermittedFileTypes': ['zip'], u'SolutionStackName': '64bit Amazon Linux 2014.03 v1.0.0 running Ruby 2.1 (Puma)'}, {u'PermittedFileTypes': ['zip'], u'SolutionStackName': '64bit Amazon Linux 2014.03 v1.0.0 running Ruby 2.1 (Passenger Standalone)'}, {u'PermittedFileTypes': ['war', 'zip'], u'SolutionStackName': '64bit Amazon Linux 2014.03 v1.0.5 running Ruby 2.0 (Puma)'}, {u'PermittedFileTypes': ['war', 'zip'], u'SolutionStackName': '64bit Amazon Linux 2014.03 v1.0.4 running Ruby 2.0 (Puma)'}, {u'PermittedFileTypes': ['war', 'zip'], u'SolutionStackName': '64bit Amazon Linux 2014.03 v1.0.4 running Ruby 2.0 (Passenger Standalone)'}, {u'PermittedFileTypes': ['war', 'zip'], u'SolutionStackName': '64bit Amazon Linux 2014.03 v1.0.3 running Ruby 2.0 (Passenger Standalone)'}, {u'PermittedFileTypes': [], u'SolutionStackName': '64bit Amazon Linux 2014.09 v1.2.0 running Docker 1.3.3'}, {u'PermittedFileTypes': [], u'SolutionStackName': '64bit Amazon Linux 2014.09 v1.0.9 running Docker 1.2.0'}, {u'PermittedFileTypes': [], u'SolutionStackName': '64bit Amazon Linux 2014.09 v1.0.8 running Docker 1.2.0'}, {u'PermittedFileTypes': [], u'SolutionStackName': '64bit Amazon Linux 2014.03 v1.0.9 running Docker 1.0.0'}, {u'PermittedFileTypes': [], u'SolutionStackName': '64bit Amazon Linux 2014.03 v1.0.7 running Docker 1.0.0'}, {u'PermittedFileTypes': ['zip', 'war', 'ear'], u'SolutionStackName': '64bit Debian jessie v1.2.0 running GlassFish 4.1 Java 8 (Preconfigured - Docker)'}, {u'PermittedFileTypes': ['zip', 'war', 'ear'], u'SolutionStackName': '64bit Debian jessie v1.2.0 running GlassFish 4.0 Java 7 (Preconfigured - Docker)'}, {u'PermittedFileTypes': ['zip'], u'SolutionStackName': '64bit Debian jessie v1.0.0 running GlassFish 4.1 Java 8 (Preconfigured - Docker)'}, {u'PermittedFileTypes': ['zip'], u'SolutionStackName': '64bit Debian jessie v1.0.0 running GlassFish 4.0 Java 7 (Preconfigured - Docker)'}, {u'PermittedFileTypes': ['zip'], u'SolutionStackName': '64bit Debian jessie v1.2.0 running Python 3.4 (Preconfigured - Docker)'}, {u'PermittedFileTypes': ['zip'], u'SolutionStackName': '64bit Debian jessie v1.0.0 running Python 3.4 (Preconfigured - Docker)'}, {u'PermittedFileTypes': ['zip'], u'SolutionStackName': '64bit Debian jessie v1.2.0 running Go 1.4 (Preconfigured - Docker)'}, {u'PermittedFileTypes': ['zip'], u'SolutionStackName': '64bit Debian jessie v1.2.0 running Go 1.3 (Preconfigured - Docker)'}]
        })

    def DescribeEvents(self):
        return Http(200), standard_events()

    def UpdateEnvironment(self):
        return Http(200), standard_update_environment()

    def DescribeEnvironments(self):
        return Http(200), stadard_describe_environments()


class MockS3(MockService):
    def get_object(self):
        pass


def replace_option_setting(namespace, option_name, new_value, option_settings):
    for setting in option_settings:
        if setting['Namespace'] == namespace \
                and setting['OptionName'] == option_name:
            setting['Value'] = new_value


def stadard_describe_environments():
    return dict(
        ResponseMetadata={'HTTPStatusCode': 200,
                          'RequestId':
                              '3f979fef-c775-11e4-84bf-d7f83bbc1d71'},
        Environments=[
            {u'ApplicationName': 'myEBCLItest',
             u'EnvironmentName': 'single-env',
             u'VersionLabel': '1_1_1', u'Status': 'Ready',
             u'Description': 'Environment created from the '
                             'EB CLI using "eb create"',
             u'EnvironmentId': 'e-b8msckgkmc',
             u'EndpointURL': '99.99.99.99',
             u'SolutionStackName': '64bit Amazon Linux '
                                   '2014.09 v1.2.0 running '
                                   'Python 2.7',
             u'CNAME':
                 'single-env124141adw.elasticbeanstalk.com',
             u'Health': 'Green',
             u'Tier': {u'Version': ' ', u'Type': 'Standard',
                       u'Name': 'WebServer'},
             u'AbortableOperationInProgress': False,
             u'DateUpdated': datetime.datetime(2015, 3, 7, 0,
                                               27, 7, 343000,
                                               tzinfo=tzutc()),
             u'DateCreated': datetime.datetime(2015, 3, 5,
                                               20, 2, 13,
                                               210000,
                                               tzinfo=tzutc())},
            {u'ApplicationName': 'myEBCLItest',
             u'EnvironmentName': 'my-env',
             u'VersionLabel': 'a926', u'Status': 'Ready',
             u'Description': 'Environment created from the '
                             'EB CLI using "eb create"',
             u'EnvironmentId': 'e-xxmxq9dyju',
             u'EndpointURL':
                 'awseb-e-x-AWSEBLoa-1B7U4N0QJJOCF-1944394517.us-west-2.elb.amazonaws.com',
             u'SolutionStackName': '64bit Amazon Linux '
                                   '2014.09 v1.2.0 running '
                                   'Python 2.7',
             u'CNAME': 'my-env-f8wj8tawyq.elasticbeanstalk.com',
             u'Health': 'Green',
             u'AbortableOperationInProgress': False,
             u'Tier': {u'Version': ' ', u'Type': 'Standard',
                       u'Name': 'WebServer'},
             u'DateUpdated': datetime.datetime(2015, 3, 5,
                                               20, 22, 11,
                                               786000,
                                               tzinfo=tzutc()),
             u'DateCreated': datetime.datetime(2015, 3, 5,
                                               19, 56, 20,
                                               893000,
                                               tzinfo=tzutc())},
            ])


def standard_update_environment():
    return dict(ApplicationName='myEBCLItest',
                EnvironmentName='my-env',
                VersionLabel='1_1_1', Status='Updating',
                Description='Environment created from the EB CLI using "eb '
                            'create"',
                ResponseMetadata={'HTTPStatusCode': 200,
                                  'RequestId':
                                      'aaa'},
                EnvironmentId='e-3m2pm6k53v',
                SolutionStackName='64bit Amazon Linux 2014.09 v1.2.0 running '
                                  'Python 2.7',
                Health='Grey',
                Tier={u'Version': ' ', u'Type': 'SQS/HTTP', u'Name': 'Worker'},
                DateUpdated=datetime.datetime(2015, 3, 10, 17, 2, 55, 643000,
                                              tzinfo=tzutc()),
                DateCreated=datetime.datetime(2015, 3, 7, 6, 34, 29, 836000,
                                              tzinfo=tzutc()))

def standard_events():
    return dict(
        Events=[{u'ApplicationName': 'myEBCLItest',
                 u'EnvironmentName': 'my-env',
                 u'Severity': 'INFO',
                 u'RequestId': 'aaa',
                 u'Message': 'Environment update completed '
                             'successfully.',
                 u'EventDate': datetime.datetime(2015, 3, 10, 16, 4,
                                                 16, 704000,
                                                 tzinfo=tzutc())},
                {u'ApplicationName': 'myEBCLItest',
                 u'EnvironmentName': 'my-env',
                 u'Severity': 'INFO',
                 u'RequestId': '0a93e8ae-c73f-11e4-8956-c1c4d272c950',
                 u'Message': 'Successfully deployed new configuration to environment.',
                 u'EventDate': datetime.datetime(2015, 3, 10, 16, 4,
                                                 16, 648000,
                                                 tzinfo=tzutc())}],
        ResponseMetadata={'HTTPStatusCode': 200,
                          'RequestId': '1acd3370-c73f-11e4-80cd-074970c6fc64'})


def standard_describe_configuration_settings():
    return dict(ConfigurationSettings=[
        {u'ApplicationName': 'myApp', u'EnvironmentName': 'my-env',
         u'Description': 'Environment created from the EB CLI using "eb create"',
         u'DeploymentStatus': 'deployed',
         u'SolutionStackName': '64bit Amazon Linux 2014.09 v1.2.0 running Python 2.7',
         u'OptionSettings':
             [{u'OptionName': 'AWS_SECRET_KEY',
               u'Namespace': 'aws:elasticbeanstalk:application:environment',
               u'Value': None}, {u'OptionName': 'AppSource',
                                 u'Namespace': 'aws:cloudformation:template:parameter',
                                 u'Value': 'http://s3-us-west-2.amazonaws.com/elasticbeanstalk-samples-us-west-2/basicapp.zip'},
              {u'OptionName': 'AWS_ACCESS_KEY_ID',
               u'Namespace': 'aws:elasticbeanstalk:application:environment',
               u'Value': None}, {u'OptionName': '/static/',
                                 u'Namespace': 'aws:elasticbeanstalk:container:python:staticfiles',
                                 u'Value': 'static/'},
              {u'OptionName': 'WSGIPath',
               u'Namespace': 'aws:elasticbeanstalk:container:python',
               u'Value': 'application.py'},
              {u'OptionName': 'PARAM1',
               u'Namespace': 'aws:elasticbeanstalk:application:environment',
               u'Value': None}, {u'OptionName': 'PARAM2',
                                 u'Namespace': 'aws:elasticbeanstalk:application:environment',
                                 u'Value': None},
              {u'OptionName': 'InstancePort',
               u'Namespace': 'aws:cloudformation:template:parameter',
               u'Value': '80'}, {u'OptionName': 'PARAM4',
                                 u'Namespace': 'aws:elasticbeanstalk:application:environment',
                                 u'Value': None},
              {u'OptionName': 'PARAM3',
               u'Namespace': 'aws:elasticbeanstalk:application:environment',
               u'Value': None}, {u'OptionName': 'NumProcesses',
                                 u'Namespace': 'aws:elasticbeanstalk:container:python',
                                 u'Value': '1'},
              {u'OptionName': 'EnvironmentVariables',
               u'Namespace': 'aws:cloudformation:template:parameter',
               u'Value': 'PARAM3=,PARAM4=,PARAM1=,PARAM2=,PARAM5=,AWS_SECRET_KEY=,AWS_ACCESS_KEY_ID='},
              {u'OptionName': 'PARAM5',
               u'Namespace': 'aws:elasticbeanstalk:application:environment',
               u'Value': None}, {u'OptionName': 'HooksPkgUrl',
                                 u'Namespace': 'aws:cloudformation:template:parameter',
                                 u'Value': 'https://s3-us-west-2.amazonaws.com/elasticbeanstalk-env-resources-us-west-2/stalks/eb_python_3.11.1/lib/hooks.tar.gz'},
              {u'OptionName': 'LogPublicationControl',
               u'Namespace': 'aws:elasticbeanstalk:hostmanager',
               u'Value': 'false'}, {u'OptionName': 'StaticFiles',
                                    u'Namespace': 'aws:elasticbeanstalk:container:python',
                                    u'Value': '/static/=static/'},
              {u'OptionName': 'InstanceType',
               u'Namespace': 'aws:autoscaling:launchconfiguration',
               u'Value': 't1.micro'}, {u'OptionName': 'NumThreads',
                                       u'Namespace': 'aws:elasticbeanstalk:container:python',
                                       u'Value': '15'},
              {u'OptionName': 'IamInstanceProfile',
               u'Namespace': 'aws:autoscaling:launchconfiguration',
               u'Value': 'aws-elasticbeanstalk-ec2-role',
               u'ResourceName': 'AWSEBAutoScalingLaunchConfiguration'},
              {u'OptionName': 'ImageId',
               u'Namespace': 'aws:autoscaling:launchconfiguration',
               u'Value': 'ami-55a7ea65',
               u'ResourceName': 'AWSEBAutoScalingLaunchConfiguration'},
              {u'OptionName': 'MonitoringInterval',
               u'Namespace': 'aws:autoscaling:launchconfiguration',
               u'Value': '5 minute',
               u'ResourceName': 'AWSEBAutoScalingLaunchConfiguration'},
              {u'OptionName': 'SecurityGroups',
               u'Namespace': 'aws:autoscaling:launchconfiguration',
               u'Value': 'awseb-e-b8msckgkmc-stack-AWSEBSecurityGroup-15909GGD48235',
               u'ResourceName': 'AWSEBAutoScalingLaunchConfiguration'},
              {u'OptionName': 'EC2KeyName',
               u'Namespace': 'aws:autoscaling:launchconfiguration',
               u'Value': 'aws',
               u'ResourceName': 'AWSEBAutoScalingLaunchConfiguration'},
              {u'OptionName': 'AssociatePublicIpAddress',
               u'Namespace': 'aws:ec2:vpc',
               u'ResourceName': 'AWSEBAutoScalingLaunchConfiguration'},
              {u'OptionName': 'RootVolumeIOPS',
               u'Namespace': 'aws:autoscaling:launchconfiguration',
               u'ResourceName': 'AWSEBAutoScalingLaunchConfiguration'},
              {u'OptionName': 'BlockDeviceMappings',
               u'Namespace': 'aws:autoscaling:launchconfiguration',
               u'ResourceName': 'AWSEBAutoScalingLaunchConfiguration'},
              {u'OptionName': 'RootVolumeType',
               u'Namespace': 'aws:autoscaling:launchconfiguration',
               u'ResourceName': 'AWSEBAutoScalingLaunchConfiguration'},
              {u'OptionName': 'RootVolumeSize',
               u'Namespace': 'aws:autoscaling:launchconfiguration',
               u'ResourceName': 'AWSEBAutoScalingLaunchConfiguration'},
              {u'OptionName': 'MaxSize',
               u'Namespace': 'aws:autoscaling:asg', u'Value': '1',
               u'ResourceName': 'AWSEBAutoScalingGroup'},
              {u'OptionName': 'Cooldown',
               u'Namespace': 'aws:autoscaling:asg', u'Value': '360',
               u'ResourceName': 'AWSEBAutoScalingGroup'},
              {u'OptionName': 'MinSize',
               u'Namespace': 'aws:autoscaling:asg', u'Value': '1',
               u'ResourceName': 'AWSEBAutoScalingGroup'},
              {u'OptionName': 'Subnets',
               u'Namespace': 'aws:ec2:vpc',
               u'ResourceName': 'AWSEBAutoScalingGroup'},
              {u'OptionName': 'RollingUpdateEnabled',
               u'Namespace': 'aws:autoscaling:updatepolicy:rollingupdate',
               u'Value': 'false',
               u'ResourceName': 'AWSEBAutoScalingGroup'},
              {u'OptionName': 'Availability Zones',
               u'Namespace': 'aws:autoscaling:asg', u'Value': 'Any',
               u'ResourceName': 'AWSEBAutoScalingGroup'},
              {u'OptionName': 'MinInstancesInService',
               u'Namespace': 'aws:autoscaling:updatepolicy:rollingupdate',
               u'ResourceName': 'AWSEBAutoScalingGroup'},
              {u'OptionName': 'Timeout',
               u'Namespace': 'aws:autoscaling:updatepolicy:rollingupdate',
               u'Value': 'PT30M',
               u'ResourceName': 'AWSEBAutoScalingGroup'},
              {u'OptionName': 'RollingUpdateType',
               u'Namespace': 'aws:autoscaling:updatepolicy:rollingupdate',
               u'Value': 'Time',
               u'ResourceName': 'AWSEBAutoScalingGroup'},
              {u'OptionName': 'PauseTime',
               u'Namespace': 'aws:autoscaling:updatepolicy:rollingupdate',
               u'ResourceName': 'AWSEBAutoScalingGroup'},
              {u'OptionName': 'MaxBatchSize',
               u'Namespace': 'aws:autoscaling:updatepolicy:rollingupdate',
               u'ResourceName': 'AWSEBAutoScalingGroup'},
              {u'OptionName': 'Custom Availability Zones',
               u'Namespace': 'aws:autoscaling:asg', u'Value': None,
               u'ResourceName': 'AWSEBAutoScalingGroup'},
              {u'OptionName': 'VPCId', u'Namespace': 'aws:ec2:vpc',
               u'ResourceName': 'AWSEBSecurityGroup'},
              {u'OptionName': 'RollbackLaunchOnFailure',
               u'Namespace': 'aws:elasticbeanstalk:control',
               u'Value': 'false'}, {u'OptionName': 'LaunchTimeout',
                                    u'Namespace': 'aws:elasticbeanstalk:control',
                                    u'Value': '0'},
              {u'OptionName': 'DefaultSSHPort',
               u'Namespace': 'aws:elasticbeanstalk:control',
               u'Value': '22'}, {u'OptionName': 'EnvironmentType',
                                 u'Namespace': 'aws:elasticbeanstalk:environment',
                                 u'Value': 'LoadBalanced'},
              {u'OptionName': 'LaunchType',
               u'Namespace': 'aws:elasticbeanstalk:control',
               u'Value': 'Migration'}, {
                  u'OptionName': 'Automatically Terminate Unhealthy Instances',
                  u'Namespace': 'aws:elasticbeanstalk:monitoring',
                  u'Value': 'true'},
              {u'OptionName': 'Notification Topic Name',
               u'Namespace': 'aws:elasticbeanstalk:sns:topics'},
              {u'OptionName': 'Timeout',
               u'Namespace': 'aws:elasticbeanstalk:command',
               u'Value': '600'},
              {u'OptionName': 'Notification Endpoint',
               u'Namespace': 'aws:elasticbeanstalk:sns:topics'},
              {u'OptionName': 'BatchSizeType',
               u'Namespace': 'aws:elasticbeanstalk:command',
               u'Value': 'Percentage'},
              {u'OptionName': 'Application Healthcheck URL',
               u'Namespace': 'aws:elasticbeanstalk:application',
               u'Value': None},
              {u'OptionName': 'SSHSourceRestriction',
               u'Namespace': 'aws:autoscaling:launchconfiguration',
               u'Value': 'tcp,22,22,0.0.0.0/0'},
              {u'OptionName': 'Notification Topic ARN',
               u'Namespace': 'aws:elasticbeanstalk:sns:topics'},
              {u'OptionName': 'BatchSize',
               u'Namespace': 'aws:elasticbeanstalk:command',
               u'Value': '30'},
              {u'OptionName': 'Notification Protocol',
               u'Namespace': 'aws:elasticbeanstalk:sns:topics',
               u'Value': 'email'}],
         u'Tier': {u'Version': ' ', u'Type': 'Standard', u'Name': 'WebServer'},
         u'DateUpdated': datetime.datetime(2015, 3, 9, 21, 8, 29, tzinfo=tzutc()),
         u'DateCreated': datetime.datetime(2015, 3, 5, 20, 2, 12,
                                           tzinfo=tzutc())}],
                ResponseMetadata=dict(
                    HTTPStatusCode=200, RequestId='aaa'))