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
import unittest
import mock

from ebcli.operations import shared_lb_ops

from .. import mock_responses


class TestSharedLBOps(unittest.TestCase):

    @mock.patch('ebcli.operations.shared_lb_ops.io.get_boolean_response')
    def test_get_shared_lb_from_customer__interactive_is_disabled(
            self,
            get_boolean_response_mock,
    ):
        elb_type = "application"
        interactive = False
        platform = None

        get_boolean_response_mock.assert_not_called()
        self.assertFalse(shared_lb_ops.get_shared_lb_from_customer(interactive, elb_type, platform))

    @mock.patch('ebcli.operations.shared_lb_ops.io.get_boolean_response')
    def test_get_shared_lb_from_customer__not_application_load_balancer(
        self,
        get_boolean_response_mock
    ):
        elb_type = "classic"
        interactive = True
        platform = None

        get_boolean_response_mock.assert_not_called()
        self.assertFalse(shared_lb_ops.get_shared_lb_from_customer(interactive, elb_type, platform))

    @mock.patch('ebcli.operations.shared_lb_ops.io.get_boolean_response')
    @mock.patch('ebcli.operations.shared_lb_ops.elasticbeanstalk.list_application_load_balancers')
    def test_get_shared_lb_from_customer__test_for_shared_lb_request_with_no(
            self,
            list_application_load_balancers_mock,
            get_boolean_response_mock,
    ):
        get_boolean_response_mock.return_value = False
        interactive = True
        elb_type = "application"
        platform = None

        list_application_load_balancers_mock.assert_not_called()
        self.assertFalse(shared_lb_ops.get_shared_lb_from_customer(interactive, elb_type, platform))

    @mock.patch('ebcli.operations.shared_lb_ops.io.get_boolean_response')
    @mock.patch('ebcli.operations.shared_lb_ops.elasticbeanstalk.list_application_load_balancers')
    @mock.patch('ebcli.operations.shared_lb_ops.io.echo')
    @mock.patch('ebcli.operations.shared_lb_ops.utils.prompt_for_index_in_list')
    def test_get_shared_lb_from_customer(
        self,
        prompt_for_index_in_list_mock,
        echo_mock,
        list_application_load_balancers_mock,
        get_boolean_response_mock
    ):
        platform = 'arn:aws:elasticbeanstalk:us-east-1::platform/Python 3.6 running on 64bit Amazon Linux/2.9.12'
        vpc = None
        interactive = True
        elb_type = 'application'
        api_response = ['arn:aws:elasticloadbalancing:us-east-1:881508045124:loadbalancer/app/alb-1/72074d479748b405', 'arn:aws:elasticloadbalancing:us-east-1:881508045124:loadbalancer/app/alb-2/5a957e362e1339a9', 'arn:aws:elasticloadbalancing:us-east-1:881508045124:loadbalancer/app/alb-3/3dfc9ab663f79319', 'arn:aws:elasticloadbalancing:us-east-1:881508045124:loadbalancer/app/alb-4/5791574adb5d39c4']
        alb_list_display_labels = ['alb-1 - arn:aws:elasticloadbalancing:us-east-1:881508045124:loadbalancer/app/alb-1/72074d479748b405', 'alb-2 - arn:aws:elasticloadbalancing:us-east-1:881508045124:loadbalancer/app/alb-2/5a957e362e1339a9', 'alb-3 - arn:aws:elasticloadbalancing:us-east-1:881508045124:loadbalancer/app/alb-3/3dfc9ab663f79319', 'alb-4 - arn:aws:elasticloadbalancing:us-east-1:881508045124:loadbalancer/app/alb-4/5791574adb5d39c4']

        expected_result = 'arn:aws:elasticloadbalancing:us-east-1:881508045124:loadbalancer/app/alb-1/72074d479748b405'

        list_application_load_balancers_mock.return_value = api_response
        get_boolean_response_mock.return_value = True
        prompt_for_index_in_list_mock.return_value = 0

        result = shared_lb_ops.get_shared_lb_from_customer(interactive,elb_type,platform,vpc)

        get_boolean_response_mock.assert_called_once_with(text='Your account has one or more sharable load balancers. Would you like your new environment to use a shared load balancer?', default=False)
        list_application_load_balancers_mock.assert_called_once_with(platform, vpc)
        echo_mock.assert_called_once_with('Select a shared load balancer')
        prompt_for_index_in_list_mock.assert_called_once_with(alb_list_display_labels, default=1)

        self.assertEqual(
                expected_result,
                result
            )

    @mock.patch('ebcli.operations.shared_lb_ops.io.get_boolean_response')
    @mock.patch('ebcli.operations.shared_lb_ops.elasticbeanstalk.list_application_load_balancers')
    @mock.patch('ebcli.operations.shared_lb_ops.io.echo')
    @mock.patch('ebcli.operations.shared_lb_ops.utils.prompt_for_index_in_list')
    def test_get_shared_lb_from_customer__with_vpc(
        self,
        prompt_for_index_in_list_mock,
        echo_mock,
        list_application_load_balancers_mock,
        get_boolean_response_mock
    ):
        platform = 'arn:aws:elasticbeanstalk:us-east-1::platform/Python 3.6 running on 64bit Amazon Linux/2.9.12'
        vpc = {'id': 'vpc-00252f9da55164b47', 'ec2subnets': 'subnet-018b695a5badc7ec7,subnet-07ce18248accbe5c9'}
        interactive = True
        elb_type ='application'
        alb_list_display_labels = ['alb-vpc1 - arn:aws:elasticloadbalancing:us-east-1:881508045124:loadbalancer/app/alb-vpc1/a2f730eefb8aab29', 'alb-vpc2 - arn:aws:elasticloadbalancing:us-east-1:881508045124:loadbalancer/app/alb-vpc2/43ca57d4b9462ba6']
        api_response = ['arn:aws:elasticloadbalancing:us-east-1:881508045124:loadbalancer/app/alb-vpc1/a2f730eefb8aab29', 'arn:aws:elasticloadbalancing:us-east-1:881508045124:loadbalancer/app/alb-vpc2/43ca57d4b9462ba6']

        expected_result = 'arn:aws:elasticloadbalancing:us-east-1:881508045124:loadbalancer/app/alb-vpc1/a2f730eefb8aab29'

        list_application_load_balancers_mock.return_value = api_response
        get_boolean_response_mock.return_value = True

        prompt_for_index_in_list_mock.return_value = 0

        result = shared_lb_ops.get_shared_lb_from_customer(interactive,elb_type,platform,vpc)

        get_boolean_response_mock.assert_called_once_with(text='Your account has one or more sharable load balancers. Would you like your new environment to use a shared load balancer?', default=False)
        list_application_load_balancers_mock.assert_called_once_with(platform, vpc)
        echo_mock.assert_called_once_with('Select a shared load balancer')
        prompt_for_index_in_list_mock.assert_called_once_with(alb_list_display_labels, default=1)

        self.assertEqual(
                expected_result,
                result
            )

    @mock.patch('ebcli.operations.shared_lb_ops.elbv2.get_listeners_for_load_balancer')
    @mock.patch('ebcli.operations.shared_lb_ops.utils.prompt_for_item_in_list')
    def test_get_shared_lb_port_from_customer__interactive_is_disabled(
            self,
            prompt_for_item_in_list_mock,
            get_listeners_for_load_balancer_mock
    ):
        interactive = False
        selected_elb = 'arn:aws:elasticloadbalancing:us-east-1:881508045124:loadbalancer/app/alb-2/5a957e362e1339a9'

        prompt_for_item_in_list_mock.assert_not_called()
        get_listeners_for_load_balancer_mock.assert_not_called()

        self.assertFalse(shared_lb_ops.get_shared_lb_port_from_customer(interactive, selected_elb))

    @mock.patch('ebcli.operations.shared_lb_ops.elbv2.get_listeners_for_load_balancer')
    @mock.patch('ebcli.operations.shared_lb_ops.utils.prompt_for_item_in_list')
    def test_get_shared_lb_port_from_customer__load_balancer_is_not_provided(
            self,
            prompt_for_item_in_list_mock,
            get_listeners_for_load_balancer_mock
    ):
        interactive = True
        selected_elb = None

        prompt_for_item_in_list_mock.assert_not_called()
        get_listeners_for_load_balancer_mock.assert_not_called()

        self.assertFalse(shared_lb_ops.get_shared_lb_port_from_customer(interactive, selected_elb))

    @mock.patch('ebcli.operations.shared_lb_ops.elbv2.get_listeners_for_load_balancer')
    @mock.patch('ebcli.operations.shared_lb_ops.utils.prompt_for_item_in_list')
    def test_get_shared_lb_port_from_customer_success(
        self,
        prompt_for_item_in_list_mock,
        get_listeners_for_load_balancer_mock
    ):
        interactive = True
        selected_elb = 'arn:aws:elasticloadbalancing:us-east-1:881508045124:loadbalancer/app/alb-2/5a957e362e1339a9'
        expected_result = 80
        listener_list = [100, 80]
        listener_list.sort()

        get_listeners_for_load_balancer_mock.return_value = mock_responses.GET_LISTENERS_FOR_LOAD_BALANCER_RESPONSE[0]
        prompt_for_item_in_list_mock.return_value = 80

        result = shared_lb_ops.get_shared_lb_port_from_customer(interactive,selected_elb)

        get_listeners_for_load_balancer_mock.assert_called_once_with(selected_elb)
        prompt_for_item_in_list_mock.assert_called_once_with(listener_list, default=1)

        self.assertEqual(
            expected_result,
            result
        )

    @mock.patch('ebcli.operations.shared_lb_ops.elbv2.get_listeners_for_load_balancer')
    @mock.patch('ebcli.operations.shared_lb_ops.utils.prompt_for_item_in_list')
    def test_get_shared_lb_port_from_customer__no_listeners_found(
        self,
        prompt_for_item_in_list_mock,
        get_listeners_for_load_balancer_mock
    ):
        get_listeners_for_load_balancer_mock.return_value = {
            'Listeners': [],
            'ResponseMetadata': {'RequestId': '4828d8b0-e9d1-44ce-8366-3e2f02d2723c', 'HTTPStatusCode': 200, 'date': 'Wed, 08 Jul 2020 23:54:29 GMT', 'RetryAttempts': 0}
        }
        selected_lb = 'arn:aws:elasticloadbalancing:us-east-1:881508045124:loadbalancer/app/alb-4/5791574adb5d39c4'
        interactive = True
        with self.assertRaises(shared_lb_ops.NotFoundError) as context_manager:
            shared_lb_ops.get_shared_lb_port_from_customer(interactive, selected_lb)

        self.assertEqual(
            'The selected load balancer has no listeners. This prevents routing requests to your environment instances. Use EC2 to add a listener to your load balancer.',
            str(context_manager.exception)
        )

    @mock.patch('ebcli.operations.shared_lb_ops.elbv2.get_listeners_for_load_balancer')
    @mock.patch('ebcli.operations.shared_lb_ops.utils.prompt_for_item_in_list')
    def test_get_shared_lb_port_from_customer__one_listener(
        self,
        prompt_for_item_in_list_mock,
        get_listeners_for_load_balancer_mock
    ):
        interactive = True
        selected_elb = 'arn:aws:elasticloadbalancing:us-east-1:881508045124:loadbalancer/app/alb-3/3dfc9ab663f79319'
        expected_result = 80
        listener_list = [80]

        get_listeners_for_load_balancer_mock.return_value = mock_responses.GET_LISTENERS_FOR_LOAD_BALANCER_RESPONSE_2[0]
        prompt_for_item_in_list_mock.assert_not_called()

        result = shared_lb_ops.get_shared_lb_port_from_customer(interactive,selected_elb)

        get_listeners_for_load_balancer_mock.assert_called_once_with(selected_elb)

        self.assertEqual(
            expected_result,
            result
        )

    @mock.patch('ebcli.operations.shared_lb_ops.elbv2.describe_load_balancers')
    def test_get_load_balancer_arn_from_load_balancer_name(
        self,
        describe_load_balancers_mock
    ):
        load_balancer_name = 'alb-1'
        expected_result = 'arn:aws:elasticloadbalancing:us-east-1:881508045124:loadbalancer/app/alb-1/72074d479748b405'

        describe_load_balancers_mock.return_value = mock_responses.DESCRIBE_LOAD_BALANCERS_RESPONSE[0]
        result = shared_lb_ops.get_load_balancer_arn_from_load_balancer_name(load_balancer_name)

        describe_load_balancers_mock.assert_called_once_with([load_balancer_name])

        self.assertEqual(
            expected_result,
            result
        )

    @mock.patch('ebcli.operations.shared_lb_ops.get_load_balancer_arn_from_load_balancer_name')
    def test_validate_shared_lb_for_non_interactive__with_load_balancer_name(
        self,
        get_load_balancer_arn_from_load_balancer_name_mock,
    ):
        shared_lb = 'alb-1'
        expected_result = 'arn:aws:elasticloadbalancing:us-east-1:881508045124:loadbalancer/app/alb-1/72074d479748b405'

        get_load_balancer_arn_from_load_balancer_name_mock.return_value = 'arn:aws:elasticloadbalancing:us-east-1:881508045124:loadbalancer/app/alb-1/72074d479748b405'

        result = shared_lb_ops.validate_shared_lb_for_non_interactive(shared_lb)
        get_load_balancer_arn_from_load_balancer_name_mock.assert_called_once_with(shared_lb)

        self.assertEqual(
            result,
            expected_result
        )

    @mock.patch('ebcli.operations.shared_lb_ops.get_load_balancer_arn_from_load_balancer_name')
    def test_validate_shared_lb_for_non_interactive__with_load_balancer_arn(
        self,
        get_load_balancer_arn_from_load_balancer_name_mock,
    ):
        shared_lb = 'arn:aws:elasticloadbalancing:us-east-1:881508045124:loadbalancer/app/alb-1/72074d479748b405'
        expected_result = 'arn:aws:elasticloadbalancing:us-east-1:881508045124:loadbalancer/app/alb-1/72074d479748b405'

        result = shared_lb_ops.validate_shared_lb_for_non_interactive(shared_lb)
        get_load_balancer_arn_from_load_balancer_name_mock.assert_not_called()

        self.assertEqual(
            result,
            expected_result
        )
