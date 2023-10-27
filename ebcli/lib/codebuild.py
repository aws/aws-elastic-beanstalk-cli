# Copyright 2016 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You
# may not use this file except in compliance with the License. A copy of
# the License is located at
#
#     http://aws.amazon.com/apache2.0/
#
# or in the "license" file accompanying this file. This file is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF
# ANY KIND, either express or implied. See the License for the specific
# language governing permissions and limitations under the License.

import re

from cement.utils.misc import minimal_logger

from ebcli.lib import aws
from ebcli.core import io
from ebcli.objects.exceptions import ServiceError
from botocore.exceptions import EndpointConnectionError

LOG = minimal_logger(__name__)


def _make_api_call(operation_name, **operation_options):
    try:
        result = aws.make_api_call('codebuild', operation_name, **operation_options)
    except ServiceError as ex:
        if ex.code == 'AccessDeniedException':
            io.echo(
                "EB CLI does not have the right permissions to access CodeBuild.\n"
                "To learn more, see Docs: https://docs-aws.amazon.com/codebuild/"
                "latest/userguide/auth-and-access-control-permissions-reference.html"
            )
        raise ex
    except EndpointConnectionError:
        LOG.debug(
            "Caught endpoint timeout for CodeBuild."
            " We are assuming this is because they are not supported in that region yet."
        )
        raise ServiceError("Elastic Beanstalk does not support AWS CodeBuild in this region.")
    return result


def batch_get_builds(ids):
    params = dict(ids=ids)
    result = _make_api_call('batch_get_builds', **params)
    return result


def get_supplementary_images():
    """
    This method extracts images from SUPPLEMENTARY_IMAGES that match a specific description pattern.
    The pattern should be adjusted based on the actual descriptions in SUPPLEMENTARY_IMAGES.
    :return: array of image dictionaries
    """
    
    regex_search_version = r"AWS ElasticBeanstalk - (.*) Running on ([^v]+)(v?[0-9]+\.[0-9]+(\.[0-9]+)?)?"
    SUPPLEMENTARY_IMAGES = {
        "platforms": [
        {
            "languages": [
                {
                    "images": [
                        {
                            "versions": ["aws/codebuild/amazonlinux2-aarch64-standard:2.0"],
                            "name": "aws/codebuild/amazonlinux2-aarch64-standard:2.0-php-7.3",
                            "description": "AWS ElasticBeanstalk - PHP 7.3 Running on Amazon Linux 2 AArch64"
                        },
                        {
                            "versions": ["aws/codebuild/amazonlinux2-aarch64-standard:2.0"],
                            "name": "aws/codebuild/amazonlinux2-aarch64-standard:2.0-php-7.4",
                            "description": "AWS ElasticBeanstalk - PHP 7.4 Running on Amazon Linux 2 AArch64"
                        },
                        {
                            "versions": ["aws/codebuild/amazonlinux2-x86_64-standard:4.0"],
                            "name": "aws/codebuild/amazonlinux2-x86_64-standard:4.0-php-8.1",
                            "description": "AWS ElasticBeanstalk - PHP 8.1 Running on Amazon Linux 2 x86_64"
                        },
                        {
                            "versions": ["aws/codebuild/amazonlinux2-aarch64-standard:3.0"],
                            "name": "aws/codebuild/amazonlinux2-aarch64-standard:3.0-php-8.1",
                            "description": "AWS ElasticBeanstalk - PHP 8.1 Running on Amazon Linux 2 AArch64"
                        },
                        {
                           "versions": ["aws/codebuild/amazonlinux2-x86_64-standard:5.0"],
                            "name": "aws/codebuild/amazonlinux2-x86_64-standard:5.0-php-8.2",
                            "description": "AWS ElasticBeanstalk - PHP 8.2 Running on Amazon Linux 2 x86_64"
                        },
                        {
                            "versions": ["aws/codebuild/windows-base:2019-1.0"],
                            "name": "aws/codebuild/windows-base:2019-1.0-php-7.4.7",
                            "description": "AWS ElasticBeanstalk - PHP 7.4.7 Running on Windows Base 2019"
                        },
                        {
                            "versions": ["aws/codebuild/windows-base:2019-2.0"],
                            "name": "aws/codebuild/windows-base:2019-2.0-php-8.1.6",
                            "description": "AWS ElasticBeanstalk - PHP 8.1.6 Running on Windows Base 2019"
                        }
                    ],
                    "language":"PHP"
                },
                {
                    "images": [
                        {
                            "versions": ["aws/codebuild/amazonlinux2-aarch64-standard:2.0"],
                            "name": "aws/codebuild/amazonlinux2-aarch64-standard:2.0-dotnet-3.1",
                            "description": "AWS ElasticBeanstalk - .NET Core 3.1 Running on Amazon Linux 2 AArch64"
                        },
                        {
                            "versions": ["aws/codebuild/ubuntu-standard:5.0"],
                            "name": "aws/codebuild/ubuntu-standard:5.0-dotnet-3.1",
                            "description": "AWS ElasticBeanstalk - .NET Core 3.1 Running on Ubuntu"
                        },
                        {
                            "versions": ["aws/codebuild/ubuntu-standard:5.0"],
                            "name": "aws/codebuild/ubuntu-standard:5.0-dotnet-5.0",
                            "description": "AWS ElasticBeanstalk - .NET Core 5.0 Running on Ubuntu"
                        },
                        {
                            "versions": ["aws/codebuild/amazonlinux2-x86_64-standard:4.0"],
                            "name": "aws/codebuild/amazonlinux2-x86_64-standard:4.0-dotnet-6.0",
                            "description": "AWS ElasticBeanstalk - .NET Core 6.0 Running on Amazon Linux 2 x86_64"
                        },
                        {
                            "versions": ["aws/codebuild/amazonlinux2-x86_64-standard:5.0"],
                            "name": "aws/codebuild/amazonlinux2-x86_64-standard:5.0-dotnet-6.0",
                            "description": "AWS ElasticBeanstalk - .NET Core 6.0 Running on Amazon Linux 2 x86_64"
                        },
                        {
                            "versions": ["aws/codebuild/amazonlinux2-aarch64-standard:3.0"],
                            "name": "aws/codebuild/amazonlinux2-aarch64-standard:3.0-dotnet-6.0",
                            "description": "AWS ElasticBeanstalk - .NET Core 6.0 Running on Amazon Linux 2 AArch64"
                        },
                        {
                            "versions": ["aws/codebuild/ubuntu-standard:6.0"],
                            "name": "aws/codebuild/ubuntu-standard:6.0-dotnet-6.0",
                            "description": "AWS ElasticBeanstalk - .NET Core 6.0 Running on Ubuntu"
                        },
                        {
                            "versions": ["aws/codebuild/ubuntu-standard:7.0"],
                            "name": "aws/codebuild/ubuntu-standard:7.0-dotnet-6.0",
                            "description": "AWS ElasticBeanstalk - .NET Core 6.0 Running on Ubuntu"
                        }
                    ],
                    "language": "DOTNET"
                }
            ],
            "platform": "AMAZON_LINUX_2"
        },
        {
            "languages": [
                {
                    "images": [
                        {
                            "versions": ["aws/codebuild/windows-base:2019-1.0"],
                            "name": "aws/codebuild/windows-base:2019-1.0-php-7.4.7",
                            "description": "AWS ElasticBeanstalk - PHP 7.4.7 Running on Windows Base 2019"
                        },
                        {
                            "versions": ["aws/codebuild/windows-base:2019-2.0"],
                            "name": "aws/codebuild/windows-base:2019-2.0-php-8.1.6",
                            "description": "AWS ElasticBeanstalk - PHP 8.1.6 Running on Windows Base 2019"
                        }
                    ],
                    "language":"PHP"
                },
                {
                    "images": [
                        {
                            "versions": ["aws/codebuild/ubuntu-standard:5.0"],
                            "name": "aws/codebuild/ubuntu-standard:5.0-dotnet-3.1",
                            "description": "AWS ElasticBeanstalk - .NET Core 3.1 Running on Ubuntu"
                        },
                        {
                            "versions": ["aws/codebuild/ubuntu-standard:5.0"],
                            "name": "aws/codebuild/ubuntu-standard:5.0-dotnet-5.0",
                            "description": "AWS ElasticBeanstalk - .NET Core 5.0 Running on Ubuntu"
                        },
                        {
                            "versions": ["aws/codebuild/ubuntu-standard:6.0"],
                            "name": "aws/codebuild/ubuntu-standard:6.0-dotnet-6.0",
                            "description": "AWS ElasticBeanstalk - .NET Core 6.0 Running on Ubuntu"
                        },
                        {
                            "versions": ["aws/codebuild/ubuntu-standard:7.0"],
                            "name": "aws/codebuild/ubuntu-standard:7.0-dotnet-6.0",
                            "description": "AWS ElasticBeanstalk - .NET Core 6.0 Running on Ubuntu"
                        }
                    ],
                    "language": "DOTNET"
                }
            ],
            "platform": "UBUNTU"
        },
        ]
        }
    supplementary_beanstalk_images = []
    
    for platform in SUPPLEMENTARY_IMAGES['platforms']:
        for language in platform['languages']:
            languages_by_platform_version = {}
            
            for image in language['images']:
                matches = re.search(regex_search_version, image['description'])
                
                if matches:
                    software_version = matches.group(1).strip()
                    platform_type = matches.group(2).strip()
                    platform_version = matches.group(3)
                    if platform_version:
                        platform_version = int(platform_version.replace("v", "").replace(".", ""))
                    else:
                        platform_version = 0  # Default if no version is found

                    
                    image['description'] = f"{software_version} on {platform_type}"

                    # Append the image to the correct array with the Platform version as the key
                    if platform_version in languages_by_platform_version.keys():
                        current_value = languages_by_platform_version[platform_version]
                        current_value.append(image)
                    else:
                        current_value = [image]
                    
                    languages_by_platform_version[platform_version] = current_value

            # Add the image dictionaries of the highest available platform version for the current language
            if languages_by_platform_version:
                supplementary_beanstalk_images += languages_by_platform_version[max(languages_by_platform_version.keys())]

   
    return supplementary_beanstalk_images
 
def list_curated_environment_images():
    """
    This raw method will get all curated images managed by CodeBuild. We will
    return an array of image dictionaries of the most recent Beanstalk platform
    version available. So in the end what will be returned is a single image for
    each available platform from CodeBuild.
    :return: array of image dictionaries
    """
    
    regex_search_version = "AWS ElasticBeanstalk - (.*)v([0-9]+\.[0-9]+\.[0-9]+)"
    
    
    result = result = _make_api_call('list_curated_environment_images')
    
    
    

    beanstalk_images = []
    for platform in result['platforms']:
        for language in platform['languages']:
            languages_by_platform_version = {}
            for image in language['images']:
                if 'ElasticBeanstalk' in image['description']:
                    matches = re.search(regex_search_version, image['description'])

                    # Get the Platform version for the current image
                    current_version = int(matches.group(2).replace(".", ""))

                    # Set the description to something nicer than the full description from CodeBuild
                    image['description'] = matches.group(1)

                    # Append the image to the correct array with the Platform version as the key
                    if current_version in languages_by_platform_version.keys():
                        current_value = languages_by_platform_version[current_version]
                        current_value.append(image)
                    else:
                        current_value = [image]
                    languages_by_platform_version[current_version] = current_value

            # Add the image dictionaries of the highest available platform version for the current language
            if languages_by_platform_version:
                beanstalk_images += languages_by_platform_version[max(languages_by_platform_version.keys())]
                bean=beanstalk_images   
    supp1=get_supplementary_images()
    transformed_supp = []
    for entry in supp1:
        transformed_entry = {
        'name': entry['name'],
        'description': entry['description'],
        'versions': entry['versions']
    }
        transformed_supp.append(transformed_entry)
    bean.extend(transformed_supp)
    
    return bean
