# Copyright 2018 Amazon.com, Inc. or its affiliates. All Rights Reserved.
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
INSTANCE_TAIL_LOGS_RESPONSE = """-------------------------------------
/var/log/awslogs.log
-------------------------------------
{'skipped_events_count': 0, 'first_event': {'timestamp': 1522962583519, 'start_position': 559799L, 'end_position': 560017L}, 'fallback_events_count': 0, 'last_event': {'timestamp': 1522962583519, 'start_position': 559799L, 'end_position': 560017L}, 'source_id': '77b026040b93055eb448bdc0b59e446f', 'num_of_events': 1, 'batch_size_in_bytes': 243}



-------------------------------------
/var/log/httpd/error_log
-------------------------------------
[Thu Apr 05 19:54:23.624780 2018] [mpm_prefork:warn] [pid 3470] AH00167: long lost child came home! (pid 3088)



-------------------------------------
/var/log/httpd/access_log
-------------------------------------
172.31.69.153 (94.208.192.103) - - [05/Apr/2018:20:57:55 +0000] "HEAD /pma/ HTTP/1.1" 404 - "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36"



-------------------------------------
/var/log/eb-activity.log
-------------------------------------
  + chown -R webapp:webapp /var/app/ondeck
[2018-04-05T19:54:21.630Z] INFO  [3555]  - [Application update app-180406_044630@3/AppDeployStage0/AppDeployPreHook/02_setup_envvars.sh] : Starting activity...


-------------------------------------
/tmp/sample-app.log
-------------------------------------
2018-04-05 20:52:51 Received message: \\xe2\\x96\\x88\\xe2



-------------------------------------
/var/log/eb-commandprocessor.log
-------------------------------------
[2018-04-05T19:45:05.526Z] INFO  [2853]  : Running 2 of 2 actions: AppDeployPostHook..."""


REQUEST_ENVIRONMENT_INFO_RESPONSE = {
    "EnvironmentInfo": [
        {
            "InfoType": "tail",
            "Ec2InstanceId": "i-024a31a441247971d",
            "SampleTimestamp": "2018-04-06T01:05:43.875Z",
            "Message": "https://elasticbeanstalk-us-east-1-123123123123.s3.amazonaws.com"
        },
        {
            "InfoType": "tail",
            "Ec2InstanceId": "i-0dce0f6c5e2d5fa48",
            "SampleTimestamp": "2018-04-06T01:05:43.993Z",
            "Message": "https://elasticbeanstalk-us-east-1-123123123123.s3.amazonaws.com"
        },
        {
            "InfoType": "tail",
            "Ec2InstanceId": "i-090689581e5afcfc6",
            "SampleTimestamp": "2018-04-06T01:05:43.721Z",
            "Message": "https://elasticbeanstalk-us-east-1-123123123123.s3.amazonaws.com"
        },
        {
            "InfoType": "tail",
            "Ec2InstanceId": "i-053efe7c102d0a540",
            "SampleTimestamp": "2018-04-06T01:05:43.900Z",
            "Message": "https://elasticbeanstalk-us-east-1-123123123123.s3.amazonaws.com"
        }
    ]
}
