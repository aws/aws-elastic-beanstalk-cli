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



ENVIRONMENT_VAR_NAMESPACE = 'aws:elasticbeanstalk:application:environment'
CLOUDFORMATION_TEMPLATE = 'aws:cloudformation:template:parameter'
DATABASE_NAMESPACE = 'aws:rds:dbinstance'


def collect_changes(api_model, usr_model):
    """
    Grabs all things in the usr_model that are different and
   returns just the changes
    :param api_model: Model from api with Namespace keys
    :param usr_model: User model, key-value style
    :return: api_model
    """

    api_model = remove_unwanted_settings(api_model)

    changes = []
    remove = []

    option_settings = api_model['OptionSettings']
    usr_options = usr_model['settings']
    for setting in option_settings:
        # Compare value for given optionName
        namespace = setting['Namespace']
        key = setting['OptionName']

        try:
            usr_value = usr_options[namespace][key]
        except KeyError:
            # user removed setting. We want to add to remove
            remove.append({'Namespace': namespace, 'OptionName': key})

        # If they dont match, take the user value
        if 'Value' in setting:
            if setting['Value'] != usr_value:
                setting['Value'] = usr_value
                if usr_value:
                    changes.append(setting)
                else:
                    remove.append({'Namespace': namespace, 'OptionName': key})
        else:
            if usr_value is not None:
                setting['Value'] = usr_value
                changes.append(setting)

    return changes, remove


def convert_api_to_usr_model(api_model):
    """
    Convert an api model with Namespaces to a User model as a key-value system
    Remove unwanted entries
    :param api_model:  Api model of environment
    :return: a user model
    """
    api_model = remove_unwanted_settings(api_model)
    usr_model = dict()
    # Grab only data we care about
    _get_key('ApplicationName', usr_model, api_model)
    _get_key('EnvironmentName', usr_model, api_model)
    _get_key('DateUpdated', usr_model, api_model)
    usr_model['settings'] = dict()
    usr_model_settings = usr_model['settings']

    for setting in api_model['OptionSettings']:
        namespace = setting['Namespace']

        if namespace not in usr_model_settings:
            #create it
            usr_model_settings[namespace] = dict()

        key = setting['OptionName']
        if 'Value' in setting:
            value = setting['Value']
        else:
            value = None

        usr_model_settings[namespace][key] = value

    return usr_model


def remove_unwanted_settings(api_model):
    option_settings = api_model['OptionSettings']
    api_model['OptionSettings'] = [
        setting for setting in option_settings if
            setting['Namespace'] != ENVIRONMENT_VAR_NAMESPACE and
            setting['Namespace'] != CLOUDFORMATION_TEMPLATE and
            not (setting['Namespace'] == DATABASE_NAMESPACE
                and (setting['OptionName'] == 'DBEngineVersion' or
                     setting['OptionName'] == 'DBUser' or
                     setting['OptionName'] == 'DBEngine' or
                     setting['OptionName'] == 'DBPassword'))

    ]
    return api_model


def _get_key(KeyName, usr_model, api_model):
    usr_model[KeyName] = api_model[KeyName]