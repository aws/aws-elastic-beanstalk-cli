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
import datetime
from dateutil import tz


DESCRIBE_DB_ENGINE_VERSIONS_RESPONSE = {
    "DBEngineVersions": [
        {
            'Engine': 'aurora-mysql',
            'EngineVersion': '5.7.12',
            'DBEngineDescription': 'Aurora MySQL'
        },
        {
            'Engine': 'aurora-postgresql',
            'EngineVersion': '9.6.3',
            'DBEngineDescription': 'Aurora (PostgreSQL)'
        },
        {
            'Engine': 'aurora-postgresql',
            'EngineVersion': '9.6.6',
            'DBEngineDescription': 'Aurora (PostgreSQL)'
        },
        {
            'Engine': 'mariadb',
            'EngineVersion': '10.0.17',
            'DBEngineDescription': 'MariaDB Community Edition'
        },
        {
            'Engine': 'mariadb',
            'EngineVersion': '10.0.24',
            'DBEngineDescription': 'MariaDB Community Edition'
        },
        {
            'Engine': 'mariadb',
            'EngineVersion': '10.0.28',
            'DBEngineDescription': 'MariaDB Community Edition'
        },
        {
            'Engine': 'mariadb',
            'EngineVersion': '10.0.31',
            'DBEngineDescription': 'MariaDB Community Edition'
        },
        {
            'Engine': 'mariadb',
            'EngineVersion': '10.0.32',
            'DBEngineDescription': 'MariaDB Community Edition'
        },
        {
            'Engine': 'mariadb',
            'EngineVersion': '10.0.34',
            'DBEngineDescription': 'MariaDB Community Edition'
        },
        {
            'Engine': 'mariadb',
            'EngineVersion': '10.1.14',
            'DBEngineDescription': 'MariaDB Community Edition'
        },
        {
            'Engine': 'mariadb',
            'EngineVersion': '10.1.19',
            'DBEngineDescription': 'MariaDB Community Edition'
        },
        {
            'Engine': 'mariadb',
            'EngineVersion': '10.1.23',
            'DBEngineDescription': 'MariaDB Community Edition'
        },
        {
            'Engine': 'mariadb',
            'EngineVersion': '10.1.26',
            'DBEngineDescription': 'MariaDB Community Edition'
        },
        {
            'Engine': 'mariadb',
            'EngineVersion': '10.1.31',
            'DBEngineDescription': 'MariaDB Community Edition'
        },
        {
            'Engine': 'mariadb',
            'EngineVersion': '10.2.11',
            'DBEngineDescription': 'MariaDB Community Edition'
        },
        {
            'Engine': 'mariadb',
            'EngineVersion': '10.2.12',
            'DBEngineDescription': 'MariaDB Community Edition'
        },
        {
            'Engine': 'mysql',
            'EngineVersion': '5.5.46',
            'DBEngineDescription': 'MySQL Community Edition'
        },
        {
            'Engine': 'mysql',
            'EngineVersion': '5.5.53',
            'DBEngineDescription': 'MySQL Community Edition'
        },
        {
            'Engine': 'mysql',
            'EngineVersion': '5.5.54',
            'DBEngineDescription': 'MySQL Community Edition'
        },
        {
            'Engine': 'mysql',
            'EngineVersion': '5.5.57',
            'DBEngineDescription': 'MySQL Community Edition'
        },
        {
            'Engine': 'mysql',
            'EngineVersion': '5.5.59',
            'DBEngineDescription': 'MySQL Community Edition'
        },
        {
            'Engine': 'mysql',
            'EngineVersion': '5.6.27',
            'DBEngineDescription': 'MySQL Community Edition'
        },
        {
            'Engine': 'mysql',
            'EngineVersion': '5.6.29',
            'DBEngineDescription': 'MySQL Community Edition'
        },
        {
            'Engine': 'mysql',
            'EngineVersion': '5.6.34',
            'DBEngineDescription': 'MySQL Community Edition'
        },
        {
            'Engine': 'mysql',
            'EngineVersion': '5.6.35',
            'DBEngineDescription': 'MySQL Community Edition'
        },
        {
            'Engine': 'mysql',
            'EngineVersion': '5.6.37',
            'DBEngineDescription': 'MySQL Community Edition'
        },
        {
            'Engine': 'mysql',
            'EngineVersion': '5.6.39',
            'DBEngineDescription': 'MySQL Community Edition'
        },
        {
            'Engine': 'mysql',
            'EngineVersion': '5.7.16',
            'DBEngineDescription': 'MySQL Community Edition'
        },
        {
            'Engine': 'mysql',
            'EngineVersion': '5.7.17',
            'DBEngineDescription': 'MySQL Community Edition'
        },
        {
            'Engine': 'mysql',
            'EngineVersion': '5.7.19',
            'DBEngineDescription': 'MySQL Community Edition'
        },
        {
            'Engine': 'mysql',
            'EngineVersion': '5.7.21',
            'DBEngineDescription': 'MySQL Community Edition'
        },
        {
            'Engine': 'oracle-ee',
            'EngineVersion': '11.2.0.4.v1',
            'DBEngineDescription': 'Oracle Database Enterprise Edition'
        },
        {
            'Engine': 'oracle-ee',
            'EngineVersion': '11.2.0.4.v3',
            'DBEngineDescription': 'Oracle Database Enterprise Edition'
        },
        {
            'Engine': 'oracle-ee',
            'EngineVersion': '11.2.0.4.v4',
            'DBEngineDescription': 'Oracle Database Enterprise Edition'
        },
        {
            'Engine': 'oracle-ee',
            'EngineVersion': '11.2.0.4.v5',
            'DBEngineDescription': 'Oracle Database Enterprise Edition'
        },
        {
            'Engine': 'oracle-ee',
            'EngineVersion': '11.2.0.4.v6',
            'DBEngineDescription': 'Oracle Database Enterprise Edition'
        },
        {
            'Engine': 'oracle-ee',
            'EngineVersion': '11.2.0.4.v7',
            'DBEngineDescription': 'Oracle Database Enterprise Edition'
        },
        {
            'Engine': 'oracle-ee',
            'EngineVersion': '11.2.0.4.v8',
            'DBEngineDescription': 'Oracle Database Enterprise Edition'
        },
        {
            'Engine': 'oracle-ee',
            'EngineVersion': '11.2.0.4.v9',
            'DBEngineDescription': 'Oracle Database Enterprise Edition'
        },
        {
            'Engine': 'oracle-ee',
            'EngineVersion': '11.2.0.4.v10',
            'DBEngineDescription': 'Oracle Database Enterprise Edition'
        },
        {
            'Engine': 'oracle-ee',
            'EngineVersion': '11.2.0.4.v11',
            'DBEngineDescription': 'Oracle Database Enterprise Edition'
        },
        {
            'Engine': 'oracle-ee',
            'EngineVersion': '11.2.0.4.v12',
            'DBEngineDescription': 'Oracle Database Enterprise Edition'
        },
        {
            'Engine': 'oracle-ee',
            'EngineVersion': '11.2.0.4.v13',
            'DBEngineDescription': 'Oracle Database Enterprise Edition'
        },
        {
            'Engine': 'oracle-ee',
            'EngineVersion': '11.2.0.4.v14',
            'DBEngineDescription': 'Oracle Database Enterprise Edition'
        },
        {
            'Engine': 'oracle-ee',
            'EngineVersion': '11.2.0.4.v15',
            'DBEngineDescription': 'Oracle Database Enterprise Edition'
        },
        {
            'Engine': 'oracle-ee',
            'EngineVersion': '12.1.0.2.v1',
            'DBEngineDescription': 'Oracle Database Enterprise Edition'
        },
        {
            'Engine': 'oracle-ee',
            'EngineVersion': '12.1.0.2.v2',
            'DBEngineDescription': 'Oracle Database Enterprise Edition'
        },
        {
            'Engine': 'oracle-ee',
            'EngineVersion': '12.1.0.2.v3',
            'DBEngineDescription': 'Oracle Database Enterprise Edition'
        },
        {
            'Engine': 'oracle-ee',
            'EngineVersion': '12.1.0.2.v4',
            'DBEngineDescription': 'Oracle Database Enterprise Edition'
        },
        {
            'Engine': 'oracle-ee',
            'EngineVersion': '12.1.0.2.v5',
            'DBEngineDescription': 'Oracle Database Enterprise Edition'
        },
        {
            'Engine': 'oracle-ee',
            'EngineVersion': '12.1.0.2.v6',
            'DBEngineDescription': 'Oracle Database Enterprise Edition'
        },
        {
            'Engine': 'oracle-ee',
            'EngineVersion': '12.1.0.2.v7',
            'DBEngineDescription': 'Oracle Database Enterprise Edition'
        },
        {
            'Engine': 'oracle-ee',
            'EngineVersion': '12.1.0.2.v8',
            'DBEngineDescription': 'Oracle Database Enterprise Edition'
        },
        {
            'Engine': 'oracle-ee',
            'EngineVersion': '12.1.0.2.v9',
            'DBEngineDescription': 'Oracle Database Enterprise Edition'
        },
        {
            'Engine': 'oracle-ee',
            'EngineVersion': '12.1.0.2.v10',
            'DBEngineDescription': 'Oracle Database Enterprise Edition'
        },
        {
            'Engine': 'oracle-ee',
            'EngineVersion': '12.1.0.2.v11',
            'DBEngineDescription': 'Oracle Database Enterprise Edition'
        },
        {
            'Engine': 'aurora',
            'EngineVersion': '5.6.10a',
            'DBEngineDescription': 'Aurora'
        },
        {
            'Engine': 'postgres',
            'EngineVersion': '9.3.12',
            'DBEngineDescription': 'PostgreSQL'
        },
        {
            'Engine': 'postgres',
            'EngineVersion': '9.3.14',
            'DBEngineDescription': 'PostgreSQL'
        },
        {
            'Engine': 'postgres',
            'EngineVersion': '9.3.16',
            'DBEngineDescription': 'PostgreSQL'
        },
        {
            'Engine': 'postgres',
            'EngineVersion': '9.3.17',
            'DBEngineDescription': 'PostgreSQL'
        },
        {
            'Engine': 'postgres',
            'EngineVersion': '9.3.19',
            'DBEngineDescription': 'PostgreSQL'
        },
        {
            'Engine': 'postgres',
            'EngineVersion': '9.3.20',
            'DBEngineDescription': 'PostgreSQL'
        },
        {
            'Engine': 'postgres',
            'EngineVersion': '9.3.22',
            'DBEngineDescription': 'PostgreSQL'
        },
        {
            'Engine': 'postgres',
            'EngineVersion': '9.4.7',
            'DBEngineDescription': 'PostgreSQL'
        },
        {
            'Engine': 'postgres',
            'EngineVersion': '9.4.9',
            'DBEngineDescription': 'PostgreSQL'
        },
        {
            'Engine': 'postgres',
            'EngineVersion': '9.4.11',
            'DBEngineDescription': 'PostgreSQL'
        },
        {
            'Engine': 'postgres',
            'EngineVersion': '9.4.12',
            'DBEngineDescription': 'PostgreSQL'
        },
        {
            'Engine': 'postgres',
            'EngineVersion': '9.4.14',
            'DBEngineDescription': 'PostgreSQL'
        },
        {
            'Engine': 'postgres',
            'EngineVersion': '9.4.15',
            'DBEngineDescription': 'PostgreSQL'
        },
        {
            'Engine': 'postgres',
            'EngineVersion': '9.4.17',
            'DBEngineDescription': 'PostgreSQL'
        },
        {
            'Engine': 'postgres',
            'EngineVersion': '9.5.2',
            'DBEngineDescription': 'PostgreSQL'
        },
        {
            'Engine': 'postgres',
            'EngineVersion': '9.5.4',
            'DBEngineDescription': 'PostgreSQL'
        },
        {
            'Engine': 'postgres',
            'EngineVersion': '9.5.6',
            'DBEngineDescription': 'PostgreSQL'
        },
        {
            'Engine': 'postgres',
            'EngineVersion': '9.5.7',
            'DBEngineDescription': 'PostgreSQL'
        },
        {
            'Engine': 'postgres',
            'EngineVersion': '9.5.9',
            'DBEngineDescription': 'PostgreSQL'
        },
        {
            'Engine': 'postgres',
            'EngineVersion': '9.5.10',
            'DBEngineDescription': 'PostgreSQL'
        },
        {
            'Engine': 'postgres',
            'EngineVersion': '9.5.12',
            'DBEngineDescription': 'PostgreSQL'
        },
        {
            'Engine': 'postgres',
            'EngineVersion': '9.6.1',
            'DBEngineDescription': 'PostgreSQL'
        },
        {
            'Engine': 'postgres',
            'EngineVersion': '9.6.2',
            'DBEngineDescription': 'PostgreSQL'
        },
        {
            'Engine': 'postgres',
            'EngineVersion': '9.6.3',
            'DBEngineDescription': 'PostgreSQL'
        },
        {
            'Engine': 'postgres',
            'EngineVersion': '9.6.5',
            'DBEngineDescription': 'PostgreSQL'
        },
        {
            'Engine': 'postgres',
            'EngineVersion': '9.6.6',
            'DBEngineDescription': 'PostgreSQL'
        },
        {
            'Engine': 'postgres',
            'EngineVersion': '9.6.8',
            'DBEngineDescription': 'PostgreSQL'
        },
        {
            'Engine': 'postgres',
            'EngineVersion': '10.1',
            'DBEngineDescription': 'PostgreSQL'
        },
        {
            'Engine': 'postgres',
            'EngineVersion': '10.3',
            'DBEngineDescription': 'PostgreSQL'
        },
        {
            'Engine': 'sqlserver-ee',
            'EngineVersion': '10.50.6000.34.v1',
            'DBEngineDescription': 'Microsoft SQL Server Enterprise Edition'
        },
        {
            'Engine': 'sqlserver-ee',
            'EngineVersion': '10.50.6529.0.v1',
            'DBEngineDescription': 'Microsoft SQL Server Enterprise Edition'
        },
        {
            'Engine': 'sqlserver-ee',
            'EngineVersion': '10.50.6560.0.v1',
            'DBEngineDescription': 'Microsoft SQL Server Enterprise Edition'
        },
        {
            'Engine': 'sqlserver-ee',
            'EngineVersion': '11.00.5058.0.v1',
            'DBEngineDescription': 'Microsoft SQL Server Enterprise Edition'
        },
        {
            'Engine': 'sqlserver-ee',
            'EngineVersion': '11.00.6020.0.v1',
            'DBEngineDescription': 'Microsoft SQL Server Enterprise Edition'
        },
        {
            'Engine': 'sqlserver-ee',
            'EngineVersion': '11.00.6594.0.v1',
            'DBEngineDescription': 'Microsoft SQL Server Enterprise Edition'
        },
        {
            'Engine': 'sqlserver-ee',
            'EngineVersion': '11.00.7462.6.v1',
            'DBEngineDescription': 'Microsoft SQL Server Enterprise Edition'
        },
        {
            'Engine': 'sqlserver-ee',
            'EngineVersion': '12.00.5000.0.v1',
            'DBEngineDescription': 'Microsoft SQL Server Enterprise Edition'
        },
        {
            'Engine': 'sqlserver-ee',
            'EngineVersion': '12.00.5546.0.v1',
            'DBEngineDescription': 'Microsoft SQL Server Enterprise Edition'
        },
        {
            'Engine': 'sqlserver-ee',
            'EngineVersion': '12.00.5571.0.v1',
            'DBEngineDescription': 'Microsoft SQL Server Enterprise Edition'
        },
        {
            'Engine': 'sqlserver-ee',
            'EngineVersion': '13.00.2164.0.v1',
            'DBEngineDescription': 'Microsoft SQL Server Enterprise Edition'
        },
        {
            'Engine': 'sqlserver-ee',
            'EngineVersion': '13.00.4422.0.v1',
            'DBEngineDescription': 'Microsoft SQL Server Enterprise Edition'
        },
        {
            'Engine': 'sqlserver-ee',
            'EngineVersion': '13.00.4451.0.v1',
            'DBEngineDescription': 'Microsoft SQL Server Enterprise Edition'
        },
        {
            'Engine': 'sqlserver-ee',
            'EngineVersion': '13.00.4466.4.v1',
            'DBEngineDescription': 'Microsoft SQL Server Enterprise Edition'
        },
        {
            'Engine': 'sqlserver-ee',
            'EngineVersion': '14.00.1000.169.v1',
            'DBEngineDescription': 'Microsoft SQL Server Enterprise Edition'
        },
        {
            'Engine': 'sqlserver-ee',
            'EngineVersion': '14.00.3015.40.v1',
            'DBEngineDescription': 'Microsoft SQL Server Enterprise Edition'
        },
        {
            'Engine': 'sqlserver-ex',
            'EngineVersion': '10.50.6000.34.v1',
            'DBEngineDescription': 'Microsoft SQL Server Express Edition'
        },
        {
            'Engine': 'sqlserver-ex',
            'EngineVersion': '10.50.6529.0.v1',
            'DBEngineDescription': 'Microsoft SQL Server Express Edition'
        },
        {
            'Engine': 'sqlserver-ex',
            'EngineVersion': '10.50.6560.0.v1',
            'DBEngineDescription': 'Microsoft SQL Server Express Edition'
        },
        {
            'Engine': 'sqlserver-ex',
            'EngineVersion': '11.00.5058.0.v1',
            'DBEngineDescription': 'Microsoft SQL Server Express Edition'
        },
        {
            'Engine': 'sqlserver-ex',
            'EngineVersion': '11.00.6020.0.v1',
            'DBEngineDescription': 'Microsoft SQL Server Express Edition'
        },
        {
            'Engine': 'sqlserver-ex',
            'EngineVersion': '11.00.6594.0.v1',
            'DBEngineDescription': 'Microsoft SQL Server Express Edition'
        },
        {
            'Engine': 'sqlserver-ex',
            'EngineVersion': '11.00.7462.6.v1',
            'DBEngineDescription': 'Microsoft SQL Server Express Edition'
        },
        {
            'Engine': 'sqlserver-ex',
            'EngineVersion': '12.00.4422.0.v1',
            'DBEngineDescription': 'Microsoft SQL Server Express Edition'
        },
        {
            'Engine': 'sqlserver-ex',
            'EngineVersion': '12.00.5000.0.v1',
            'DBEngineDescription': 'Microsoft SQL Server Express Edition'
        },
        {
            'Engine': 'sqlserver-ex',
            'EngineVersion': '12.00.5546.0.v1',
            'DBEngineDescription': 'Microsoft SQL Server Express Edition'
        },
        {
            'Engine': 'sqlserver-ex',
            'EngineVersion': '12.00.5571.0.v1',
            'DBEngineDescription': 'Microsoft SQL Server Express Edition'
        },
        {
            'Engine': 'sqlserver-ex',
            'EngineVersion': '13.00.2164.0.v1',
            'DBEngineDescription': 'Microsoft SQL Server Express Edition'
        },
        {
            'Engine': 'sqlserver-ex',
            'EngineVersion': '13.00.4422.0.v1',
            'DBEngineDescription': 'Microsoft SQL Server Express Edition'
        },
        {
            'Engine': 'sqlserver-ex',
            'EngineVersion': '13.00.4451.0.v1',
            'DBEngineDescription': 'Microsoft SQL Server Express Edition'
        },
        {
            'Engine': 'sqlserver-ex',
            'EngineVersion': '13.00.4466.4.v1',
            'DBEngineDescription': 'Microsoft SQL Server Express Edition'
        },
        {
            'Engine': 'sqlserver-ex',
            'EngineVersion': '14.00.1000.169.v1',
            'DBEngineDescription': 'Microsoft SQL Server Express Edition'
        },
        {
            'Engine': 'sqlserver-ex',
            'EngineVersion': '14.00.3015.40.v1',
            'DBEngineDescription': 'Microsoft SQL Server Express Edition'
        },
        {
            'Engine': 'sqlserver-se',
            'EngineVersion': '10.50.6000.34.v1',
            'DBEngineDescription': 'Microsoft SQL Server Standard Edition'
        },
        {
            'Engine': 'sqlserver-se',
            'EngineVersion': '10.50.6529.0.v1',
            'DBEngineDescription': 'Microsoft SQL Server Standard Edition'
        },
        {
            'Engine': 'sqlserver-se',
            'EngineVersion': '10.50.6560.0.v1',
            'DBEngineDescription': 'Microsoft SQL Server Standard Edition'
        },
        {
            'Engine': 'sqlserver-se',
            'EngineVersion': '11.00.5058.0.v1',
            'DBEngineDescription': 'Microsoft SQL Server Standard Edition'
        },
        {
            'Engine': 'sqlserver-se',
            'EngineVersion': '11.00.6020.0.v1',
            'DBEngineDescription': 'Microsoft SQL Server Standard Edition'
        },
        {
            'Engine': 'sqlserver-se',
            'EngineVersion': '11.00.6594.0.v1',
            'DBEngineDescription': 'Microsoft SQL Server Standard Edition'
        },
        {
            'Engine': 'sqlserver-se',
            'EngineVersion': '11.00.7462.6.v1',
            'DBEngineDescription': 'Microsoft SQL Server Standard Edition'
        },
        {
            'Engine': 'sqlserver-se',
            'EngineVersion': '12.00.4422.0.v1',
            'DBEngineDescription': 'Microsoft SQL Server Standard Edition'
        },
        {
            'Engine': 'sqlserver-se',
            'EngineVersion': '12.00.5000.0.v1',
            'DBEngineDescription': 'Microsoft SQL Server Standard Edition'
        },
        {
            'Engine': 'sqlserver-se',
            'EngineVersion': '12.00.5546.0.v1',
            'DBEngineDescription': 'Microsoft SQL Server Standard Edition'
        },
        {
            'Engine': 'sqlserver-se',
            'EngineVersion': '12.00.5571.0.v1',
            'DBEngineDescription': 'Microsoft SQL Server Standard Edition'
        },
        {
            'Engine': 'sqlserver-se',
            'EngineVersion': '13.00.2164.0.v1',
            'DBEngineDescription': 'Microsoft SQL Server Standard Edition'
        },
        {
            'Engine': 'sqlserver-se',
            'EngineVersion': '13.00.4422.0.v1',
            'DBEngineDescription': 'Microsoft SQL Server Standard Edition'
        },
        {
            'Engine': 'sqlserver-se',
            'EngineVersion': '13.00.4451.0.v1',
            'DBEngineDescription': 'Microsoft SQL Server Standard Edition'
        },
        {
            'Engine': 'sqlserver-se',
            'EngineVersion': '13.00.4466.4.v1',
            'DBEngineDescription': 'Microsoft SQL Server Standard Edition'
        },
        {
            'Engine': 'sqlserver-se',
            'EngineVersion': '14.00.1000.169.v1',
            'DBEngineDescription': 'Microsoft SQL Server Standard Edition'
        },
        {
            'Engine': 'sqlserver-se',
            'EngineVersion': '14.00.3015.40.v1',
            'DBEngineDescription': 'Microsoft SQL Server Standard Edition'
        },
        {
            'Engine': 'sqlserver-web',
            'EngineVersion': '10.50.6000.34.v1',
            'DBEngineDescription': 'Microsoft SQL Server Web Edition'
        },
        {
            'Engine': 'sqlserver-web',
            'EngineVersion': '10.50.6529.0.v1',
            'DBEngineDescription': 'Microsoft SQL Server Web Edition'
        },
        {
            'Engine': 'sqlserver-web',
            'EngineVersion': '10.50.6560.0.v1',
            'DBEngineDescription': 'Microsoft SQL Server Web Edition'
        },
        {
            'Engine': 'sqlserver-web',
            'EngineVersion': '11.00.5058.0.v1',
            'DBEngineDescription': 'Microsoft SQL Server Web Edition'
        },
        {
            'Engine': 'sqlserver-web',
            'EngineVersion': '11.00.6020.0.v1',
            'DBEngineDescription': 'Microsoft SQL Server Web Edition'
        },
        {
            'Engine': 'sqlserver-web',
            'EngineVersion': '11.00.6594.0.v1',
            'DBEngineDescription': 'Microsoft SQL Server Web Edition'
        },
        {
            'Engine': 'sqlserver-web',
            'EngineVersion': '11.00.7462.6.v1',
            'DBEngineDescription': 'Microsoft SQL Server Web Edition'
        },
        {
            'Engine': 'sqlserver-web',
            'EngineVersion': '12.00.4422.0.v1',
            'DBEngineDescription': 'Microsoft SQL Server Web Edition'
        },
        {
            'Engine': 'sqlserver-web',
            'EngineVersion': '12.00.5000.0.v1',
            'DBEngineDescription': 'Microsoft SQL Server Web Edition'
        },
        {
            'Engine': 'sqlserver-web',
            'EngineVersion': '12.00.5546.0.v1',
            'DBEngineDescription': 'Microsoft SQL Server Web Edition'
        },
        {
            'Engine': 'sqlserver-web',
            'EngineVersion': '12.00.5571.0.v1',
            'DBEngineDescription': 'Microsoft SQL Server Web Edition'
        },
        {
            'Engine': 'sqlserver-web',
            'EngineVersion': '13.00.2164.0.v1',
            'DBEngineDescription': 'Microsoft SQL Server Web Edition'
        },
        {
            'Engine': 'sqlserver-web',
            'EngineVersion': '13.00.4422.0.v1',
            'DBEngineDescription': 'Microsoft SQL Server Web Edition'
        },
        {
            'Engine': 'sqlserver-web',
            'EngineVersion': '13.00.4451.0.v1',
            'DBEngineDescription': 'Microsoft SQL Server Web Edition'
        },
        {
            'Engine': 'sqlserver-web',
            'EngineVersion': '13.00.4466.4.v1',
            'DBEngineDescription': 'Microsoft SQL Server Web Edition'
        },
        {
            'Engine': 'sqlserver-web',
            'EngineVersion': '14.00.1000.169.v1',
            'DBEngineDescription': 'Microsoft SQL Server Web Edition'
        },
        {
            'Engine': 'sqlserver-web',
            'EngineVersion': '14.00.3015.40.v1',
            'DBEngineDescription': 'Microsoft SQL Server Web Edition'
        }
    ]
}


RDS_DESCRIBE_CONFIGURATION_OPTIONS_RESPONSE = {
    'Options': [
        {
            'ChangeSeverity': 'Unknown',
            'DefaultValue': '5',
            'Description': 'The allocated storage size specified in gigabytes.',
            'MaxLength': None,
            'MaxValue': 1024,
            'MinValue': 5,
            'Name': 'DBAllocatedStorage',
            'Namespace': 'aws:rds:dbinstance',
            'Regex': None,
            'UserDefined': False,
            'ValueOptions': None,
            'ValueType': 'Scalar'
        },
        {
            'ChangeSeverity': 'RestartEnvironment',
            'DefaultValue': 'enhanced',
            'Description': None,
            'MaxLength': None,
            'MaxValue': None,
            'MinValue': None,
            'Name': 'SystemType',
            'Namespace': 'aws:elasticbeanstalk:healthreporting:system',
            'Regex': None,
            'UserDefined': False,
            'ValueOptions': [
                'enhanced'
            ],
            'ValueType': 'Scalar'
        },
        {
            'ChangeSeverity': 'NoInterruption',
            'DefaultValue': None,
            'Description': 'The time in UTC for this schedule to start. For example, 2014-11-20T00:00:00Z.',
            'MaxLength': None,
            'MaxValue': None,
            'MinValue': None,
            'Name': 'StartTime',
            'Namespace': 'aws:autoscaling:scheduledaction',
            'Regex': None,
            'UserDefined': False,
            'ValueOptions': None,
            'ValueType': 'Scalar'
        },
        {
            'ChangeSeverity': 'NoInterruption',
            'DefaultValue': None,
            'Description': 'The time in UTC when recurring future actions will start. You specify the start time by following the Unix cron syntax format.',
            'MaxLength': None,
            'MaxValue': None,
            'MinValue': None,
            'Name': 'Recurrence',
            'Namespace': 'aws:autoscaling:scheduledaction',
            'Regex': None,
            'UserDefined': False,
            'ValueOptions': None,
            'ValueType': 'Scalar'
        },
        {
            'ChangeSeverity': 'NoInterruption',
            'DefaultValue': None,
            'Description': 'The maximum number of Amazon EC2 instances in the Auto Scaling group.',
            'MaxLength': None,
            'MaxValue': 10000,
            'MinValue': 0,
            'Name': 'MaxSize',
            'Namespace': 'aws:autoscaling:scheduledaction',
            'Regex': None,
            'UserDefined': False,
            'ValueOptions': None,
            'ValueType': 'Scalar'
        },
        {
            'ChangeSeverity': 'NoInterruption',
            'DefaultValue': 'email',
            'Description': 'The protocol to use when subscribing the Notification Endpoint to an SNS topic for Elastic Beanstalk event notifications.',
            'MaxLength': None,
            'MaxValue': None,
            'MinValue': None,
            'Name': 'Notification Protocol',
            'Namespace': 'aws:elasticbeanstalk:sns:topics',
            'Regex': None,
            'UserDefined': False,
            'ValueOptions': [
                'http',
                'https',
                'email',
                'email-json',
                'sqs'
            ],
            'ValueType': 'Scalar'
        },
        {
            'ChangeSeverity': 'Unknown',
            'DefaultValue': 'Snapshot',
            'Description': 'Decides whether to delete, snapshot or retain the DB instance on environment termination',
            'MaxLength': None,
            'MaxValue': None,
            'MinValue': None,
            'Name': 'DBDeletionPolicy',
            'Namespace': 'aws:rds:dbinstance',
            'Regex': None,
            'UserDefined': False,
            'ValueOptions': [
                'Delete',
                'Snapshot',
                'Retain'
            ],
            'ValueType': 'Scalar'
        },
        {
            'ChangeSeverity': 'NoInterruption',
            'DefaultValue': None,
            'Description': 'The endpoint to subscribe to an SNS topic for Elastic Beanstalk event notifications.',
            'MaxLength': None,
            'MaxValue': None,
            'MinValue': None,
            'Name': 'Notification Endpoint',
            'Namespace': 'aws:elasticbeanstalk:sns:topics',
            'Regex': None,
            'UserDefined': False,
            'ValueOptions': None,
            'ValueType': 'Scalar'
        },
        {
            'ChangeSeverity': 'Unknown',
            'DefaultValue': 'MySQL',
            'Description': 'The name of the database engine to be used for this instance.',
            'MaxLength': None,
            'MaxValue': None,
            'MinValue': None,
            'Name': 'DBEngine',
            'Namespace': 'aws:rds:dbinstance',
            'Regex': None,
            'UserDefined': False,
            'ValueOptions': [
                'mysql',
                'oracle-se1',
                'postgres',
                'sqlserver-ex',
                'sqlserver-web',
                'sqlserver-se',
                'mariadb'
            ],
            'ValueType': 'Scalar'
        },
        {
            'ChangeSeverity': 'Unknown',
            'DefaultValue': 'standard',
            'Description': 'The storage type associated with DB instance.',
            'MaxLength': None,
            'MaxValue': None,
            'MinValue': None,
            'Name': 'DBStorageType',
            'Namespace': 'aws:rds:dbinstance',
            'Regex': None,
            'UserDefined': False,
            'ValueOptions': [
                'gp2',
                'io1',
                'standard'
            ],
            'ValueType': 'Scalar'
        },
        {
            'ChangeSeverity': 'RestartDatabase',
            'DefaultValue': 'ebroot',
            'Description': 'The name of master user for the client DB Instance.',
            'MaxLength': 128,
            'MaxValue': None,
            'MinValue': None,
            'Name': 'DBUser',
            'Namespace': 'aws:rds:dbinstance',
            'Regex': {
                'Label': 'Regex pattern: [a-zA-Z][a-zA-Z0-9]*',
                'Pattern': '[a-zA-Z][a-zA-Z0-9]*'
            },
            'UserDefined': False,
            'ValueOptions': None,
            'ValueType': 'Scalar'
        },
        {
            'ChangeSeverity': 'NoInterruption',
            'DefaultValue': None,
            'Description': 'The minimum number of Amazon EC2 instances in the Auto Scaling group.',
            'MaxLength': None,
            'MaxValue': 10000,
            'MinValue': 0,
            'Name': 'MinSize',
            'Namespace': 'aws:autoscaling:scheduledaction',
            'Regex': None,
            'UserDefined': False,
            'ValueOptions': None,
            'ValueType': 'Scalar'
        },
        {
            'ChangeSeverity': 'NoInterruption',
            'DefaultValue': None,
            'Description': 'The number of Amazon EC2 instances that should be running in the Auto Scaling group.',
            'MaxLength': None,
            'MaxValue': 10000,
            'MinValue': 0,
            'Name': 'DesiredCapacity',
            'Namespace': 'aws:autoscaling:scheduledaction',
            'Regex': None,
            'UserDefined': False,
            'ValueOptions': None,
            'ValueType': 'Scalar'
        },
        {
            'ChangeSeverity': 'NoInterruption',
            'DefaultValue': 'false',
            'Description': "If it is set to true the scheduled action will be suspended and won't take any effect.",
            'MaxLength': None,
            'MaxValue': None,
            'MinValue': None,
            'Name': 'Suspend',
            'Namespace': 'aws:autoscaling:scheduledaction',
            'Regex': None,
            'UserDefined': False,
            'ValueOptions': None,
            'ValueType': 'Boolean'
        },
        {
            'ChangeSeverity': 'Unknown',
            'DefaultValue': None,
            'Description': 'Sets template parameter value.',
            'MaxLength': None,
            'MaxValue': None,
            'MinValue': None,
            'Name': '*',
            'Namespace': 'aws:cloudformation:template:parameter',
            'Regex': None,
            'UserDefined': False,
            'ValueOptions': None,
            'ValueType': 'Scalar'
        },
        {
            'ChangeSeverity': 'NoInterruption',
            'DefaultValue': None,
            'Description': 'The arn of an existing SNS Topic to use for Elastic Beanstalk event notifications.',
            'MaxLength': None,
            'MaxValue': None,
            'MinValue': None,
            'Name': 'Notification Topic ARN',
            'Namespace': 'aws:elasticbeanstalk:sns:topics',
            'Regex': None,
            'UserDefined': False,
            'ValueOptions': None,
            'ValueType': 'Scalar'
        },
        {
            'ChangeSeverity': 'NoInterruption',
            'DefaultValue': None,
            'Description': 'The name of the notification topic to create for Elastic Beanstalk event notifications.',
            'MaxLength': None,
            'MaxValue': None,
            'MinValue': None,
            'Name': 'Notification Topic Name',
            'Namespace': 'aws:elasticbeanstalk:sns:topics',
            'Regex': None,
            'UserDefined': False,
            'ValueOptions': None,
            'ValueType': 'Scalar'
        },
        {
            'ChangeSeverity': 'Unknown',
            'DefaultValue': '1',
            'Description': 'The number of days for which automatic backups are retained.',
            'MaxLength': None,
            'MaxValue': 35,
            'MinValue': 0,
            'Name': 'DBBackupRetentionPeriod',
            'Namespace': 'aws:rds:dbinstance',
            'Regex': None,
            'UserDefined': False,
            'ValueOptions': None,
            'ValueType': 'Scalar'
        },
        {
            'ChangeSeverity': 'RestartEnvironment',
            'DefaultValue': None,
            'Description': 'Specify an S3 location with a set of eb extensions.',
            'MaxLength': 1024,
            'MaxValue': None,
            'MinValue': None,
            'Name': 'ExternalExtensionsS3Key',
            'Namespace': 'aws:elasticbeanstalk:environment',
            'Regex': None,
            'UserDefined': False,
            'ValueOptions': None,
            'ValueType': 'Scalar'
        },
        {
            'ChangeSeverity': 'RestartDatabase',
            'DefaultValue': None,
            'Description': 'The identifier for the DB snapshot to restore from.',
            'MaxLength': 256,
            'MaxValue': None,
            'MinValue': None,
            'Name': 'DBSnapshotIdentifier',
            'Namespace': 'aws:rds:dbinstance',
            'Regex': {
                'Label': 'Regex pattern: [a-zA-Z]([a-zA-Z0-9]*(-[a-zA-Z0-9])?)*',
                'Pattern': '[a-zA-Z]([a-zA-Z0-9]*(-[a-zA-Z0-9])?)*'
            },
            'UserDefined': False,
            'ValueOptions': None,
            'ValueType': 'Scalar'
        },
        {
            'ChangeSeverity': 'RestartEnvironment',
            'DefaultValue': None,
            'Description': 'Specify an S3 location with a set of eb extensions.',
            'MaxLength': 255,
            'MaxValue': None,
            'MinValue': None,
            'Name': 'ExternalExtensionsS3Bucket',
            'Namespace': 'aws:elasticbeanstalk:environment',
            'Regex': None,
            'UserDefined': False,
            'ValueOptions': None,
            'ValueType': 'Scalar'
        },
        {
            'ChangeSeverity': 'Unknown',
            'DefaultValue': None,
            'Description': 'Sets template resource property value.',
            'MaxLength': None,
            'MaxValue': None,
            'MinValue': None,
            'Name': '*',
            'Namespace': 'aws:cloudformation:template:resource:property',
            'Regex': None,
            'UserDefined': False,
            'ValueOptions': None,
            'ValueType': 'Scalar'
        },
        {
            'ChangeSeverity': 'Unknown',
            'DefaultValue': None,
            'Description': 'The name of master user password for the client DB Instance.',
            'MaxLength': 128,
            'MaxValue': None,
            'MinValue': None,
            'Name': 'DBPassword',
            'Namespace': 'aws:rds:dbinstance',
            'Regex': {
                'Label': 'Regex pattern: [^(\\/@)]*',
                'Pattern': '[^(\\/@)]*'
            },
            'UserDefined': False,
            'ValueOptions': None,
            'ValueType': 'Scalar'
        },
        {
            'ChangeSeverity': 'Unknown',
            'DefaultValue': None,
            'Description': 'The read replica identifiers associated with RDS DB instance.',
            'MaxLength': None,
            'MaxValue': None,
            'MinValue': None,
            'Name': 'ReadReplicaIdentifiers',
            'Namespace': 'aws:rds:dbinstance',
            'Regex': {
                'Label': 'Regex pattern: [0-9a-zA-Z]+(,[0-9a-zA-Z]+)*',
                'Pattern': '[0-9a-zA-Z]+(,[0-9a-zA-Z]+)*'
            },
            'UserDefined': False,
            'ValueOptions': None,
            'ValueType': 'Scalar'
        },
        {
            'ChangeSeverity': 'NoInterruption',
            'DefaultValue': None,
            'Description': 'Used by Elastic Beanstalk to perform asynchronized jobs to maintain your environments.',
            'MaxLength': 500,
            'MaxValue': None,
            'MinValue': None,
            'Name': 'ServiceRole',
            'Namespace': 'aws:elasticbeanstalk:environment',
            'Regex': None,
            'UserDefined': False,
            'ValueOptions': None,
            'ValueType': 'Scalar'
        },
        {
            'ChangeSeverity': 'RestartDatabase',
            'DefaultValue': 'false',
            'Description': 'Create a multi-AZ Amazon RDS database instance.',
            'MaxLength': None,
            'MaxValue': None,
            'MinValue': None,
            'Name': 'MultiAZDatabase',
            'Namespace': 'aws:rds:dbinstance',
            'Regex': None,
            'UserDefined': False,
            'ValueOptions': None,
            'ValueType': 'Boolean'
        },
        {
            'ChangeSeverity': 'NoInterruption',
            'DefaultValue': None,
            'Description': 'The time in UTC for this schedule to end. For example, 2014-11-20T01:00:00Z.',
            'MaxLength': None,
            'MaxValue': None,
            'MinValue': None,
            'Name': 'EndTime',
            'Namespace': 'aws:autoscaling:scheduledaction',
            'Regex': None,
            'UserDefined': False,
            'ValueOptions': None,
            'ValueType': 'Scalar'
        },
        {
            'ChangeSeverity': 'Unknown',
            'DefaultValue': '5.6.39',
            'Description': 'The version number of the database engine to use.',
            'MaxLength': None,
            'MaxValue': None,
            'MinValue': None,
            'Name': 'DBEngineVersion',
            'Namespace': 'aws:rds:dbinstance',
            'Regex': {
                'Label': 'Regex pattern: [a-zA-Z0-9\\.]*',
                'Pattern': '[a-zA-Z0-9\\.]*'
            },
            'UserDefined': False,
            'ValueOptions': [
                '5.5.46',
                '5.5.53',
                '5.5.54',
                '5.5.57',
                '5.5.59',
                '5.6.27',
                '5.6.29',
                '5.6.34',
                '5.6.35',
                '5.6.37',
                '5.6.39',
                '5.7.16',
                '5.7.17',
                '5.7.19',
                '5.7.21'
            ],
            'ValueType': 'Scalar'
        },
        {
            'ChangeSeverity': 'Unknown',
            'DefaultValue': 'db.t2.micro',
            'Description': 'The database instance type.',
            'MaxLength': None,
            'MaxValue': None,
            'MinValue': None,
            'Name': 'DBInstanceClass',
            'Namespace': 'aws:rds:dbinstance',
            'Regex': None,
            'UserDefined': False,
            'ValueOptions': [
                'db.m1.large',
                'db.m1.medium',
                'db.m1.small',
                'db.m1.xlarge',
                'db.m2.2xlarge',
                'db.m2.4xlarge',
                'db.m2.xlarge',
                'db.m3.2xlarge',
                'db.m3.large',
                'db.m3.medium',
                'db.m3.xlarge',
                'db.m4.10xlarge',
                'db.m4.16xlarge',
                'db.m4.2xlarge',
                'db.m4.4xlarge',
                'db.m4.large',
                'db.m4.xlarge',
                'db.r3.2xlarge',
                'db.r3.4xlarge',
                'db.r3.8xlarge',
                'db.r3.large',
                'db.r3.xlarge',
                'db.r4.16xlarge',
                'db.r4.2xlarge',
                'db.r4.4xlarge',
                'db.r4.8xlarge',
                'db.r4.large',
                'db.r4.xlarge',
                'db.t2.2xlarge',
                'db.t2.large',
                'db.t2.medium',
                'db.t2.micro',
                'db.t2.small',
                'db.t2.xlarge'
            ],
            'ValueType': 'Scalar'
        }
    ],
    'PlatformArn': None,
    'SolutionStackName': None,
    'Tier': {
        'Name': 'WebServer',
        'Type': 'Standard',
        'Version': '1.0'
    }
}


DESCRIBE_VPCS_RESPONSE = {
    'Vpcs': [
        {
            'VpcId': 'vpc-0b94a86c',
            'IsDefault': True,
        },
        {
            'VpcId': 'vpc-a30db3c5',
            'IsDefault': False,
        },
        {
            'VpcId': 'vpc-eb1e688d',
            'IsDefault': False,
        }
    ]
}


DESCRIBE_SUBNETS_RESPONSE = {
    'Subnets': [
        {
            'AvailabilityZone': 'us-west-2a',
            'SubnetId': 'subnet-90e8a0f7',
            'VpcId': 'vpc-0b94a86c',
        },
        {
            'AvailabilityZone': 'us-west-2c',
            'SubnetId': 'subnet-2f6f9d74',
            'VpcId': 'vpc-0b94a86c',
        },
        {
            'AvailabilityZone': 'us-west-2b',
            'SubnetId': 'subnet-3cc4a775',
            'VpcId': 'vpc-0b94a86c',
        },
        {
            'AvailabilityZone': 'us-west-2a',
            'SubnetId': 'subnet-0129ad67',
            'VpcId': 'vpc-eb1e688d',
        }
    ]
}


DESCRIBE_SECURITY_GROUPS_RESPONSE = {
    "SecurityGroups": [
        {
            "Description": "launch-wizard-13 created 2017-12-10T22:59:54.589-08:00",
            "GroupName": "launch-wizard-13",
            "IpPermissions": [
                {
                    "FromPort": 22,
                    "IpProtocol": "tcp",
                    "IpRanges": [
                        {
                            "CidrIp": "0.0.0.0/0"
                        }
                    ],
                    "Ipv6Ranges": [],
                    "PrefixListIds": [],
                    "ToPort": 22,
                    "UserIdGroupPairs": []
                }
            ],
            "OwnerId": "123123123123",
            "GroupId": "sg-013d807d",
            "IpPermissionsEgress": [
                {
                    "IpProtocol": "-1",
                    "IpRanges": [
                        {
                            "CidrIp": "0.0.0.0/0"
                        }
                    ],
                    "Ipv6Ranges": [],
                    "PrefixListIds": [],
                    "UserIdGroupPairs": []
                }
            ],
            "VpcId": "vpc-0b94a86c"
        },
        {
            "Description": "allows inbound traffic",
            "GroupName": "awsmac",
            "IpPermissions": [
                {
                    "FromPort": 8443,
                    "IpProtocol": "tcp",
                    "IpRanges": [
                        {
                            "CidrIp": "13.248.16.0/25"
                        },
                        {
                            "CidrIp": "13.248.18.0/23"
                        },
                        {
                            "CidrIp": "27.0.3.144/29"
                        },
                        {
                            "CidrIp": "27.0.3.152/29"
                        },
                        {
                            "CidrIp": "52.119.144.0/25"
                        },
                    ],
                    "Ipv6Ranges": [],
                    "PrefixListIds": [],
                    "ToPort": 8443,
                    "UserIdGroupPairs": []
                }
            ],
            'GroupId': 'sg-013d807e',
            "VpcId": "vpc-0b94a86c"
        },
        {
            "Description": "launch-wizard-1 created 2017-05-30T17:31:40.541-07:00",
            "GroupName": "launch-wizard-1",
            "IpPermissions": [
                {
                    "FromPort": 3389,
                    "IpProtocol": "tcp",
                    "IpRanges": [
                        {
                            "CidrIp": "0.0.0.0/0"
                        }
                    ],
                    "Ipv6Ranges": [],
                    "PrefixListIds": [],
                    "ToPort": 3389,
                    "UserIdGroupPairs": []
                }
            ],
            "OwnerId": "123123123123",
            "GroupId": "sg-fd6f4986",
            "IpPermissionsEgress": [
                {
                    "IpProtocol": "-1",
                    "IpRanges": [
                        {
                            "CidrIp": "0.0.0.0/0"
                        }
                    ],
                    "Ipv6Ranges": [],
                    "PrefixListIds": [],
                    "UserIdGroupPairs": []
                }
            ],
            'VpcId': 'vpc-eb1e688d',
        }
    ]
}


DESCRIBE_KEY_PAIRS_RESPONSE = {
    'KeyPairs': [
        {
            'KeyName': 'key_pair_1',
            'KeyFingerprint': '77:77:77:77:77:77:77:77:77:77:77:77:77:77:77:77:77:77:77:77'
        },
        {
            'KeyName': 'key_pair_2',
            'KeyFingerprint': '77:77:77:77:77:77:77:77:77:77:77:77:77:77:77:77:77:77:77:77'
        }
    ]
}


DESCRIBE_ENVIRONMENT_RESOURCES_RESPONSE = {
    'EnvironmentResources': {
        'LaunchConfigurations': [
            {
                'Name': 'awseb-e-zitmqcrygu-stack-AWSEBAutoScalingLaunchConfiguration'
            }
        ],
        'AutoScalingGroups': [
            {
                'Name': 'awseb-e-zitmqcrygu-stack-AWSEBAutoScalingGroup'
            }
        ],
        'Triggers': [],
        'Instances': [
            {
                'Id': 'i-23452345346456566'
            },
            {
                'Id': 'i-21312312312312312'
            }
        ],
        'LoadBalancers': [
            {
                'Name': 'awseb-e-z-AWSEBLoa-SOME-LOAD-BALANCER'
            }
        ],
        'EnvironmentName': 'my-environment'
    }
}


DESCRIBE_ENVIRONMENT_RESOURCES_RESPONSE__SINGLE_INSTANCE_ENVIRONMENT = {
    "EnvironmentResources": {
        "EnvironmentName": "vpc-tests-single",
        "AutoScalingGroups": [
            {
                "Name": "awseb-e-cdad3hm9nv-stack-AWSEBAutoScalingGroup-12KTBJ0N99705"
            }
        ],
        "Instances": [
            {
                "Id": "i-05faf37b6c7b904d7"
            }
        ],
        "LaunchConfigurations": [
            {
                "Name": "awseb-e-cdad3hm9nv-stack-AWSEBAutoScalingLaunchConfiguration-MWZFM5O5VNW6"
            }
        ],
        "LoadBalancers": [],
        "Triggers": [],
        "Queues": []
    }
}


DESCRIBE_ENVIRONMENT_RESOURCES_RESPONSE__ELBV2_ENVIRONMENT = {
    "EnvironmentResources": {
        "EnvironmentName": "vpc-tests-network",
        "AutoScalingGroups": [
            {
                "Name": "awseb-e-pqmmgvbwiw-stack-AWSEBAutoScalingGroup-19TXU0OXRUSAP"
            }
        ],
        "Instances": [
            {
                "Id": "i-01641763db1c0cb47"
            }
        ],
        "LaunchConfigurations": [
            {
                "Name": "awseb-e-pqmmgvbwiw-stack-AWSEBAutoScalingLaunchConfiguration-1HG7B5KKYJTC4"
            }
        ],
        "LoadBalancers": [
            {
                "Name": "arn:aws:elasticloadbalancing:us-west-2:123123123123:loadbalancer/net/awseb-AWSEB-1SCRDNB3JJ0K1/01e95fc8160f13cf"
            }
        ],
        "Triggers": [],
        "Queues": []
    }
}


DESCRIBE_EVENTS_RESPONSE = {
    'Events': [
        {
            'EventDate': '2018-03-12T22:14:14.292Z',
            'Message': 'Deleting SNS topic for environment my-environment.',
            'ApplicationName': 'application-name',
            'EnvironmentName': 'my-environment',
            'RequestId': '23141234-134adsfasdf-12341234',
            'Severity': 'INFO'
        },
        {
            'EventDate': '2018-03-12T22:14:11.740Z',
            'Message': 'Using elasticbeanstalk-us-west-2-123123123123 as Amazon S3 storage bucket for environment data.',
            'ApplicationName': 'application-name',
            'EnvironmentName': 'my-environment',
            'RequestId': '23141234-134adsfasdf-12341234',
            'Severity': 'INFO'
        },
        {
            'EventDate': '2018-03-12T22:14:10.897Z',
            'Message': 'createEnvironment is starting.',
            'ApplicationName': 'application-name',
            'EnvironmentName': 'my-environment',
            'RequestId': '23141234-134adsfasdf-12341234',
            'Severity': 'INFO'
        },
        {
            'EventDate': '2018-03-12T22:14:09.357Z',
            'Message': 'createApplicationVersion completed successfully.',
            'ApplicationName': 'application-name',
            'VersionLabel': 'app-180313_071408',
            'RequestId': '23141234-134adsfasdf-12341234',
            'Severity': 'INFO'
        },
        {
            'EventDate': '2018-03-12T22:14:09.269Z',
            'Message': 'Created new Application Version: app-180313_071408',
            'ApplicationName': 'application-name',
            'VersionLabel': 'app-180313_071408',
            'RequestId': '23141234-134adsfasdf-12341234',
            'Severity': 'INFO'
        },
        {
            'EventDate': '2018-03-12T22:14:09.216Z',
            'Message': 'createApplicationVersion is starting.',
            'ApplicationName': 'application-name',
            'VersionLabel': 'app-180313_071408',
            'RequestId': '23141234-134adsfasdf-12341234',
            'Severity': 'INFO'
        },
        {
            'EventDate': '2018-03-12T22:13:31.747Z',
            'Message': 'createApplication completed successfully.',
            'ApplicationName': 'application-name',
            'RequestId': '23141234-134adsfasdf-12341234',
            'Severity': 'INFO'
        },
        {
            'EventDate': '2018-03-12T22:13:31.695Z',
            'Message': 'Created new Application: application-name',
            'ApplicationName': 'application-name',
            'RequestId': '23141234-134adsfasdf-12341234',
            'Severity': 'INFO'
        },
        {
            'EventDate': '2018-03-12T22:13:31.511Z',
            'Message': 'createApplication is starting.',
            'ApplicationName': 'application-name',
            'RequestId': '23141234-134adsfasdf-12341234',
            'Severity': 'INFO'
        }
    ]
}


CREATE_ENVIRONMENT_DESCRIBE_EVENTS = {
    'Events': [
        {
            'EventDate': datetime.datetime(2018, 7, 19, 21, 50, 21, 623000, tzinfo=tz.tzutc()),
            'Message': 'Successfully launched environment: eb-locust-example-windows-server-dev',
            'ApplicationName': 'eb-locust-example-windows-server',
            'EnvironmentName': 'eb-locust-example-windows-server-dev',
            'RequestId': 'a28c2685-b6a0-4785-82bf-45de6451bd01',
            'Severity': 'INFO'
        },
        {
            'EventDate': datetime.datetime(2018, 7, 19, 21, 50, 0, 909000, tzinfo=tz.tzutc()),
            'Message': 'Environment health has transitioned from Pending to Ok. Initialization completed 26 seconds ago and took 5 minutes.',
            'ApplicationName': 'eb-locust-example-windows-server',
            'EnvironmentName': 'eb-locust-example-windows-server-dev',
            'Severity': 'INFO'
        },
        {
            'EventDate': datetime.datetime(2018, 7, 19, 21, 49, 10, tzinfo=tz.tzutc()),
            'Message': "Nginx configuration detected in the '.ebextensions/nginx' directory. AWS Elastic Beanstalk will no longer manage the Nginx configuration for this environment.",
            'ApplicationName': 'eb-locust-example-windows-server',
            'EnvironmentName': 'eb-locust-example-windows-server-dev',
            'RequestId': 'a28c2685-b6a0-4785-82bf-45de6451bd01',
            'Severity': 'INFO'
        },
        {
            'EventDate': datetime.datetime(2018, 7, 19, 21, 46, 20, 148000, tzinfo=tz.tzutc()),
            'Message': 'Created Load Balancer listener named: arn:aws:elasticloadbalancing:us-west-2:123123123123:listener/app/awseb-AWSEB-1U4TIRMMNUG89/c00caf9caf7ea40a/290a651181682b7c',
            'ApplicationName': 'eb-locust-example-windows-server',
            'EnvironmentName': 'eb-locust-example-windows-server-dev',
            'RequestId': 'a28c2685-b6a0-4785-82bf-45de6451bd01',
            'Severity': 'INFO'
        },
        {
            'EventDate': datetime.datetime(2018, 7, 19, 21, 46, 20, 85000, tzinfo=tz.tzutc()),
            'Message': 'Created load balancer named: arn:aws:elasticloadbalancing:us-west-2:123123123123:loadbalancer/app/awseb-AWSEB-1U4TIRMMNUG89/c00caf9caf7ea40a',
            'ApplicationName': 'eb-locust-example-windows-server',
            'EnvironmentName': 'eb-locust-example-windows-server-dev',
            'RequestId': 'a28c2685-b6a0-4785-82bf-45de6451bd01',
            'Severity': 'INFO'
        },
        {
            'EventDate': datetime.datetime(2018, 7, 19, 21, 46, 1, 177000, tzinfo=tz.tzutc()),
            'Message': 'Added instance [i-015ccf443ebbdca74] to your environment.',
            'ApplicationName': 'eb-locust-example-windows-server',
            'EnvironmentName': 'eb-locust-example-windows-server-dev',
            'Severity': 'INFO'
        },
        {
            'EventDate': datetime.datetime(2018, 7, 19, 21, 45, 46, 426000, tzinfo=tz.tzutc()),
            'Message': 'Created CloudWatch alarm named: awseb-e-3vui9m2zcq-stack-AWSEBCloudwatchAlarmLow-9678TTC8356T',
            'ApplicationName': 'eb-locust-example-windows-server',
            'EnvironmentName': 'eb-locust-example-windows-server-dev',
            'RequestId': 'a28c2685-b6a0-4785-82bf-45de6451bd01',
            'Severity': 'INFO'
        },
        {
            'EventDate': datetime.datetime(2018, 7, 19, 21, 45, 46, 386000, tzinfo=tz.tzutc()),
            'Message': 'Created CloudWatch alarm named: awseb-e-3vui9m2zcq-stack-AWSEBCloudwatchAlarmHigh-1EIGCE53U06YR',
            'ApplicationName': 'eb-locust-example-windows-server',
            'EnvironmentName': 'eb-locust-example-windows-server-dev',
            'RequestId': 'a28c2685-b6a0-4785-82bf-45de6451bd01',
            'Severity': 'INFO'
        },
        {
            'EventDate': datetime.datetime(2018, 7, 19, 21, 45, 46, 348000, tzinfo=tz.tzutc()),
            'Message': 'Created Auto Scaling group policy named: arn:aws:autoscaling:us-west-2:123123123123:scalingPolicy:886beef6-ee91-49f9-b2b5-a404aa1614fa:autoScalingGroupName/awseb-e-3vui9m2zcq-stack-AWSEBAutoScalingGroup-4P5RVB6OO8NU:policyName/awseb-e-3vui9m2zcq-stack-AWSEBAutoScalingScaleDownPolicy-1HFFV6G3V1BZT',
            'ApplicationName': 'eb-locust-example-windows-server',
            'EnvironmentName': 'eb-locust-example-windows-server-dev',
            'RequestId': 'a28c2685-b6a0-4785-82bf-45de6451bd01',
            'Severity': 'INFO'
        },
        {
            'EventDate': datetime.datetime(2018, 7, 19, 21, 45, 46, 297000, tzinfo=tz.tzutc()),
            'Message': 'Created Auto Scaling group policy named: arn:aws:autoscaling:us-west-2:123123123123:scalingPolicy:9e57739d-32bc-47ba-a6b0-792e26b0c66d:autoScalingGroupName/awseb-e-3vui9m2zcq-stack-AWSEBAutoScalingGroup-4P5RVB6OO8NU:policyName/awseb-e-3vui9m2zcq-stack-AWSEBAutoScalingScaleUpPolicy-TFZ49ZB7D9HF',
            'ApplicationName': 'eb-locust-example-windows-server',
            'EnvironmentName': 'eb-locust-example-windows-server-dev',
            'RequestId': 'a28c2685-b6a0-4785-82bf-45de6451bd01',
            'Severity': 'INFO'
        },
        {
            'EventDate': datetime.datetime(2018, 7, 19, 21, 45, 30, 896000, tzinfo=tz.tzutc()),
            'Message': 'Waiting for EC2 instances to launch. This may take a few minutes.',
            'ApplicationName': 'eb-locust-example-windows-server',
            'EnvironmentName': 'eb-locust-example-windows-server-dev',
            'RequestId': 'a28c2685-b6a0-4785-82bf-45de6451bd01',
            'Severity': 'INFO'
        },
        {
            'EventDate': datetime.datetime(2018, 7, 19, 21, 45, 30, 854000, tzinfo=tz.tzutc()),
            'Message': 'Created Auto Scaling group named: awseb-e-3vui9m2zcq-stack-AWSEBAutoScalingGroup-4P5RVB6OO8NU',
            'ApplicationName': 'eb-locust-example-windows-server',
            'EnvironmentName': 'eb-locust-example-windows-server-dev',
            'RequestId': 'a28c2685-b6a0-4785-82bf-45de6451bd01',
            'Severity': 'INFO'
        },
        {
            'EventDate': datetime.datetime(2018, 7, 19, 21, 44, 13, 347000, tzinfo=tz.tzutc()),
            'Message': 'Created Auto Scaling launch configuration named: awseb-e-3vui9m2zcq-stack-AWSEBAutoScalingLaunchConfiguration-1AYJSODC9NCQ0',
            'ApplicationName': 'eb-locust-example-windows-server',
            'EnvironmentName': 'eb-locust-example-windows-server-dev',
            'RequestId': 'a28c2685-b6a0-4785-82bf-45de6451bd01',
            'Severity': 'INFO'
        },
        {
            'EventDate': datetime.datetime(2018, 7, 19, 21, 44, 13, 297000, tzinfo=tz.tzutc()),
            'Message': 'Created security group named: awseb-e-3vui9m2zcq-stack-AWSEBSecurityGroup-7S6YT48ATB9X',
            'ApplicationName': 'eb-locust-example-windows-server',
            'EnvironmentName': 'eb-locust-example-windows-server-dev',
            'RequestId': 'a28c2685-b6a0-4785-82bf-45de6451bd01',
            'Severity': 'INFO'
        },
        {
            'EventDate': datetime.datetime(2018, 7, 19, 21, 44, 13, 239000, tzinfo=tz.tzutc()),
            'Message': 'Created security group named: sg-dc0062ac',
            'ApplicationName': 'eb-locust-example-windows-server',
            'EnvironmentName': 'eb-locust-example-windows-server-dev',
            'RequestId': 'a28c2685-b6a0-4785-82bf-45de6451bd01',
            'Severity': 'INFO'
        },
        {
            'EventDate': datetime.datetime(2018, 7, 19, 21, 44, 13, 174000, tzinfo=tz.tzutc()),
            'Message': 'Created target group named: arn:aws:elasticloadbalancing:us-west-2:123123123123:targetgroup/awseb-AWSEB-1PK9GSYN2ELIT/8cea89f8126bd593',
            'ApplicationName': 'eb-locust-example-windows-server',
            'EnvironmentName': 'eb-locust-example-windows-server-dev',
            'RequestId': 'a28c2685-b6a0-4785-82bf-45de6451bd01',
            'Severity': 'INFO'
        },
        {
            'EventDate': datetime.datetime(2018, 7, 19, 21, 44, 1, 266000, tzinfo=tz.tzutc()),
            'Message': 'Environment health has transitioned to Pending. Initialization in progress (running for 3 seconds). There are no instances.',
            'ApplicationName': 'eb-locust-example-windows-server',
            'EnvironmentName': 'eb-locust-example-windows-server-dev',
            'Severity': 'INFO'
        },
        {
            'EventDate': datetime.datetime(2018, 7, 19, 21, 43, 51, 685000, tzinfo=tz.tzutc()),
            'Message': 'Using elasticbeanstalk-us-west-2-123123123123 as Amazon S3 storage bucket for environment data.',
            'ApplicationName': 'eb-locust-example-windows-server',
            'EnvironmentName': 'eb-locust-example-windows-server-dev',
            'RequestId': 'a28c2685-b6a0-4785-82bf-45de6451bd01',
            'Severity': 'INFO'
        },
        {
            'EventDate': datetime.datetime(2018, 7, 19, 21, 43, 50, 165000, tzinfo=tz.tzutc()),
            'Message': 'createEnvironment is starting.',
            'ApplicationName': 'eb-locust-example-windows-server',
            'EnvironmentName': 'eb-locust-example-windows-server-dev',
            'RequestId': 'a28c2685-b6a0-4785-82bf-45de6451bd01',
            'Severity': 'INFO'
        },
    ],
    'NextToken': 'MTUzMjAzMjI3MzUzNzo6MDo6MTUzMjA1NTExNjcwNg==',
    'ResponseMetadata': {
        'RequestId': '16074038-243f-4291-b0f9-4f8c0c1afdd3',
        'HTTPStatusCode': 200,
        'HTTPHeaders': {
            'content-type': 'text/xml',
            'date': 'Fri, 20 Jul 2018 02:51:55 GMT',
            'vary': 'Accept-Encoding',
            'x-amzn-requestid': '16074038-243f-4291-b0f9-4f8c0c1afdd3',
            'content-length': '48919',
            'connection': 'keep-alive'
        },
        'RetryAttempts': 0
    }
}


COMPOSE_ENVIRONMENTS_DESCRIBE_EVENTS = {
    'Events': [
        {
            'EventDate': datetime.datetime(2018, 6, 15, 19, 51, 55, 134000, tzinfo=tz.tzutc()),
            'Message': 'Successfully launched environment: environment-2',
            'ApplicationName': 'my-application',
            'EnvironmentName': 'environment-2',
            'RequestId': '2bd9b511-40bf-474e-b3da-d9e3fbd473c9',
            'Severity': 'INFO'
        },
        {
            'EventDate': datetime.datetime(2018, 6, 15, 19, 50, 58, 588000, tzinfo=tz.tzutc()),
            'Message': 'Environment health has been set to GREEN',
            'ApplicationName': 'my-application',
            'EnvironmentName': 'environment-2',
            'Severity': 'INFO'
        },
        {
            'EventDate': datetime.datetime(2018, 6, 15, 19, 49, 5, 548000, tzinfo=tz.tzutc()),
            'Message': 'Successfully launched environment: environment-1',
            'ApplicationName': 'my-application',
            'EnvironmentName': 'environment-1',
            'RequestId': '522b30dd-c255-4174-8105-2c3d65e6ba2a',
            'Severity': 'INFO'
        },
        {
            'EventDate': datetime.datetime(2018, 6, 15, 19, 48, 10, 792000, tzinfo=tz.tzutc()),
            'Message': 'Environment health has been set to GREEN',
            'ApplicationName': 'my-application',
            'EnvironmentName': 'environment-1',
            'Severity': 'INFO'
        },
        {
            'EventDate': datetime.datetime(2018, 6, 15, 19, 47, 47, 35000, tzinfo=tz.tzutc()),
            'Message': 'Created CloudWatch alarm named: awseb-e-kuqwnck4n8-stack-AWSEBCloudwatchAlarmLow-U5TAX4ZS6GDC',
            'ApplicationName': 'my-application',
            'EnvironmentName': 'environment-1',
            'RequestId': '522b30dd-c255-4174-8105-2c3d65e6ba2a',
            'Severity': 'INFO'
        },
        {
            'EventDate': datetime.datetime(2018, 6, 15, 19, 47, 46, 998000, tzinfo=tz.tzutc()),
            'Message': 'Created CloudWatch alarm named: awseb-e-kuqwnck4n8-stack-AWSEBCloudwatchAlarmHigh-2ZS6IWJ4P7J8',
            'ApplicationName': 'my-application',
            'EnvironmentName': 'environment-1',
            'RequestId': '522b30dd-c255-4174-8105-2c3d65e6ba2a',
            'Severity': 'INFO'
        },
        {
            'EventDate': datetime.datetime(2018, 6, 15, 19, 47, 46, 962000, tzinfo=tz.tzutc()),
            'Message': 'Created Auto Scaling group policy named: arn:aws:autoscaling:eu-west-1:123123123123:scalingPolicy:f283175b-46f7-4eee-909d-5caf6d9bd73e:autoScalingGroupName/awseb-e-kuqwnck4n8-stack-AWSEBAutoScalingGroup-11K53S424AJF6:policyName/awseb-e-kuqwnck4n8-stack-AWSEBAutoScalingScaleDownPolicy-E1AS0TV205OS',
            'ApplicationName': 'my-application',
            'EnvironmentName': 'environment-1',
            'RequestId': '522b30dd-c255-4174-8105-2c3d65e6ba2a',
            'Severity': 'INFO'
        },
        {
            'EventDate': datetime.datetime(2018, 6, 15, 19, 47, 46, 918000, tzinfo=tz.tzutc()),
            'Message': 'Created Auto Scaling group policy named: arn:aws:autoscaling:eu-west-1:123123123123:scalingPolicy:dd611938-d042-4a2c-8581-3b4d089ea47c:autoScalingGroupName/awseb-e-kuqwnck4n8-stack-AWSEBAutoScalingGroup-11K53S424AJF6:policyName/awseb-e-kuqwnck4n8-stack-AWSEBAutoScalingScaleUpPolicy-59A98I46PYZ',
            'ApplicationName': 'my-application',
            'EnvironmentName': 'environment-1',
            'RequestId': '522b30dd-c255-4174-8105-2c3d65e6ba2a',
            'Severity': 'INFO'
        },
        {
            'EventDate': datetime.datetime(2018, 6, 15, 19, 47, 31, 615000, tzinfo=tz.tzutc()),
            'Message': 'Waiting for EC2 instances to launch. This may take a few minutes.',
            'ApplicationName': 'my-application',
            'EnvironmentName': 'environment-1',
            'RequestId': '522b30dd-c255-4174-8105-2c3d65e6ba2a',
            'Severity': 'INFO'
        },
        {
            'EventDate': datetime.datetime(2018, 6, 15, 19, 47, 31, 575000, tzinfo=tz.tzutc()),
            'Message': 'Created Auto Scaling group named: awseb-e-kuqwnck4n8-stack-AWSEBAutoScalingGroup-11K53S424AJF6',
            'ApplicationName': 'my-application',
            'EnvironmentName': 'environment-1',
            'RequestId': '522b30dd-c255-4174-8105-2c3d65e6ba2a',
            'Severity': 'INFO'
        },
        {
            'EventDate': datetime.datetime(2018, 6, 15, 19, 47, 21, 936000, tzinfo=tz.tzutc()),
            'Message': 'Created CloudWatch alarm named: awseb-e-m43rwf82e5-stack-AWSEBCloudwatchAlarmHigh-13CM9KUNS5IXK',
            'ApplicationName': 'my-application',
            'EnvironmentName': 'environment-2',
            'RequestId': '2bd9b511-40bf-474e-b3da-d9e3fbd473c9',
            'Severity': 'INFO'
        },
        {
            'EventDate': datetime.datetime(2018, 6, 15, 19, 47, 21, 898000, tzinfo=tz.tzutc()),
            'Message': 'Created CloudWatch alarm named: awseb-e-m43rwf82e5-stack-AWSEBCloudwatchAlarmLow-NOC6BULG0II2',
            'ApplicationName': 'my-application',
            'EnvironmentName': 'environment-2',
            'RequestId': '2bd9b511-40bf-474e-b3da-d9e3fbd473c9',
            'Severity': 'INFO'
        },
        {
            'EventDate': datetime.datetime(2018, 6, 15, 19, 47, 21, 862000, tzinfo=tz.tzutc()),
            'Message': 'Created Auto Scaling group policy named: arn:aws:autoscaling:eu-west-1:123123123123:scalingPolicy:dca6aebe-7ba0-4b2e-82f2-3d5ce33bdc1b:autoScalingGroupName/awseb-e-m43rwf82e5-stack-AWSEBAutoScalingGroup-2C70XPER7IL1:policyName/awseb-e-m43rwf82e5-stack-AWSEBAutoScalingScaleUpPolicy-JB1U3RC26091',
            'ApplicationName': 'my-application',
            'EnvironmentName': 'environment-2',
            'RequestId': '2bd9b511-40bf-474e-b3da-d9e3fbd473c9',
            'Severity': 'INFO'
        },
        {
            'EventDate': datetime.datetime(2018, 6, 15, 19, 47, 21, 820000, tzinfo=tz.tzutc()),
            'Message': 'Created Auto Scaling group policy named: arn:aws:autoscaling:eu-west-1:123123123123:scalingPolicy:5ec9addd-d62c-4380-97df-6a78adcc00bf:autoScalingGroupName/awseb-e-m43rwf82e5-stack-AWSEBAutoScalingGroup-2C70XPER7IL1:policyName/awseb-e-m43rwf82e5-stack-AWSEBAutoScalingScaleDownPolicy-ZBFPONHB5OKP',
            'ApplicationName': 'my-application',
            'EnvironmentName': 'environment-2',
            'RequestId': '2bd9b511-40bf-474e-b3da-d9e3fbd473c9',
            'Severity': 'INFO'
        },
        {
            'EventDate': datetime.datetime(2018, 6, 15, 19, 47, 21, 770000, tzinfo=tz.tzutc()),
            'Message': 'Waiting for EC2 instances to launch. This may take a few minutes.',
            'ApplicationName': 'my-application',
            'EnvironmentName': 'environment-2',
            'RequestId': '2bd9b511-40bf-474e-b3da-d9e3fbd473c9',
            'Severity': 'INFO'
        },
        {
            'EventDate': datetime.datetime(2018, 6, 15, 19, 47, 21, 710000, tzinfo=tz.tzutc()),
            'Message': 'Created Auto Scaling group named: awseb-e-m43rwf82e5-stack-AWSEBAutoScalingGroup-2C70XPER7IL1',
            'ApplicationName': 'my-application',
            'EnvironmentName': 'environment-2',
            'RequestId': '2bd9b511-40bf-474e-b3da-d9e3fbd473c9',
            'Severity': 'INFO'
        },
        {
            'EventDate': datetime.datetime(2018, 6, 15, 19, 47, 9, 111000, tzinfo=tz.tzutc()),
            'Message': "Adding instance 'i-080ac1f6f68daed01' to your environment.",
            'ApplicationName': 'my-application',
            'EnvironmentName': 'environment-2',
            'Severity': 'INFO'
        },
        {
            'EventDate': datetime.datetime(2018, 6, 15, 19, 47, 9, 111000, tzinfo=tz.tzutc()),
            'Message': "Added EC2 instance 'i-080ac1f6f68daed01' to Auto Scaling Group 'awseb-e-m43rwf82e5-stack-AWSEBAutoScalingGroup-2C70XPER7IL1'.",
            'ApplicationName': 'my-application',
            'EnvironmentName': 'environment-2',
            'Severity': 'INFO'
        },
        {
            'EventDate': datetime.datetime(2018, 6, 15, 19, 47, 0, 930000, tzinfo=tz.tzutc()),
            'Message': "Added EC2 instance 'i-0994162b2dbdf8790' to Auto Scaling Group 'awseb-e-kuqwnck4n8-stack-AWSEBAutoScalingGroup-11K53S424AJF6'.",
            'ApplicationName': 'my-application',
            'EnvironmentName': 'environment-1',
            'Severity': 'INFO'
        },
        {
            'EventDate': datetime.datetime(2018, 6, 15, 19, 47, 0, 930000, tzinfo=tz.tzutc()),
            'Message': "Adding instance 'i-0994162b2dbdf8790' to your environment.",
            'ApplicationName': 'my-application',
            'EnvironmentName': 'environment-1',
            'Severity': 'INFO'
        },
        {
            'EventDate': datetime.datetime(2018, 6, 15, 19, 46, 19, 475000, tzinfo=tz.tzutc()),
            'Message': 'Created Auto Scaling launch configuration named: awseb-e-m43rwf82e5-stack-AWSEBAutoScalingLaunchConfiguration-1GDHWDRATGXLQ',
            'ApplicationName': 'my-application',
            'EnvironmentName': 'environment-2',
            'RequestId': '2bd9b511-40bf-474e-b3da-d9e3fbd473c9',
            'Severity': 'INFO'
        },
        {
            'EventDate': datetime.datetime(2018, 6, 15, 19, 46, 19, 404000, tzinfo=tz.tzutc()),
            'Message': 'Created security group named: awseb-e-m43rwf82e5-stack-AWSEBSecurityGroup-6I9U5YBPFFXJ',
            'ApplicationName': 'my-application',
            'EnvironmentName': 'environment-2',
            'RequestId': '2bd9b511-40bf-474e-b3da-d9e3fbd473c9',
            'Severity': 'INFO'
        },
        {
            'EventDate': datetime.datetime(2018, 6, 15, 19, 45, 32, 583000, tzinfo=tz.tzutc()),
            'Message': 'Created load balancer named: awseb-e-m-AWSEBLoa-19I1GLMMFDVLJ',
            'ApplicationName': 'my-application',
            'EnvironmentName': 'environment-2',
            'RequestId': '2bd9b511-40bf-474e-b3da-d9e3fbd473c9',
            'Severity': 'INFO'
        },
        {
            'EventDate': datetime.datetime(2018, 6, 15, 19, 45, 28, 5000, tzinfo=tz.tzutc()),
            'Message': 'Created Auto Scaling launch configuration named: awseb-e-kuqwnck4n8-stack-AWSEBAutoScalingLaunchConfiguration-1H04QXPJW60H5',
            'ApplicationName': 'my-application',
            'EnvironmentName': 'environment-1',
            'RequestId': '522b30dd-c255-4174-8105-2c3d65e6ba2a',
            'Severity': 'INFO'
        },
        {
            'EventDate': datetime.datetime(2018, 6, 15, 19, 45, 27, 933000, tzinfo=tz.tzutc()),
            'Message': 'Created security group named: awseb-e-kuqwnck4n8-stack-AWSEBSecurityGroup-BCO350UPOO4G',
            'ApplicationName': 'my-application',
            'EnvironmentName': 'environment-1',
            'RequestId': '522b30dd-c255-4174-8105-2c3d65e6ba2a',
            'Severity': 'INFO'
        },
        {
            'EventDate': datetime.datetime(2018, 6, 15, 19, 45, 17, 207000, tzinfo=tz.tzutc()),
            'Message': 'Created security group named: sg-4e3d1433',
            'ApplicationName': 'my-application',
            'EnvironmentName': 'environment-2',
            'RequestId': '2bd9b511-40bf-474e-b3da-d9e3fbd473c9',
            'Severity': 'INFO'
        },
        {
            'EventDate': datetime.datetime(2018, 6, 15, 19, 44, 57, 342000, tzinfo=tz.tzutc()),
            'Message': 'Using elasticbeanstalk-eu-west-1-123123123123 as Amazon S3 storage bucket for environment data.',
            'ApplicationName': 'my-application',
            'EnvironmentName': 'environment-2',
            'RequestId': '2bd9b511-40bf-474e-b3da-d9e3fbd473c9',
            'Severity': 'INFO'
        },
        {
            'EventDate': datetime.datetime(2018, 6, 15, 19, 44, 57, 230000, tzinfo=tz.tzutc()),
            'Message': 'Created load balancer named: awseb-e-k-AWSEBLoa-1UWQNX5DI2ZZT',
            'ApplicationName': 'my-application',
            'EnvironmentName': 'environment-1',
            'RequestId': '522b30dd-c255-4174-8105-2c3d65e6ba2a',
            'Severity': 'INFO'
        },
        {
            'EventDate': datetime.datetime(2018, 6, 15, 19, 44, 56, 592000, tzinfo=tz.tzutc()),
            'Message': 'createEnvironment is starting.',
            'ApplicationName': 'my-application',
            'EnvironmentName': 'environment-2',
            'RequestId': '2bd9b511-40bf-474e-b3da-d9e3fbd473c9',
            'Severity': 'INFO'
        },
        {
            'EventDate': datetime.datetime(2018, 6, 15, 19, 44, 56, 321000, tzinfo=tz.tzutc()),
            'Message': 'Created security group named: sg-29391054',
            'ApplicationName': 'my-application',
            'EnvironmentName': 'environment-1',
            'RequestId': '522b30dd-c255-4174-8105-2c3d65e6ba2a',
            'Severity': 'INFO'
        },
        {
            'EventDate': datetime.datetime(2018, 6, 15, 19, 44, 5, 531000, tzinfo=tz.tzutc()),
            'Message': 'Using elasticbeanstalk-eu-west-1-123123123123 as Amazon S3 storage bucket for environment data.',
            'ApplicationName': 'my-application',
            'EnvironmentName': 'environment-1',
            'RequestId': '522b30dd-c255-4174-8105-2c3d65e6ba2a',
            'Severity': 'INFO'
        },
        {
            'EventDate': datetime.datetime(2018, 6, 15, 19, 44, 4, 648000, tzinfo=tz.tzutc()),
            'Message': 'createEnvironment is starting.',
            'ApplicationName': 'my-application',
            'EnvironmentName': 'environment-1',
            'RequestId': '522b30dd-c255-4174-8105-2c3d65e6ba2a',
            'Severity': 'INFO'
        },
    ],
    'ResponseMetadata': {
        'RequestId': '391ae6f8-e388-4d8c-b58b-9be51b6e43cd',
        'HTTPStatusCode': 200,
        'HTTPHeaders': {
            'content-type': 'text/xml',
            'date': 'Fri, 20 Jul 2018 20:55:20 GMT',
            'vary': 'Accept-Encoding',
            'x-amzn-requestid': '391ae6f8-e388-4d8c-b58b-9be51b6e43cd',
            'content-length': '38489',
            'connection': 'keep-alive'
        },
        'RetryAttempts': 0
    }
}


DESCRIBE_ENVIRONMENTS_RESPONSE = {
    'Environments': [
        {
            'ApplicationName': 'my-application',
            'EnvironmentName': 'environment-1',
            'VersionLabel': 'Sample Application',
            'Status': 'Ready',
            'Description': 'Environment created from the EB CLI using "eb create"',
            'EnvironmentLinks': [

            ],
            'PlatformArn': 'arn:aws:elasticbeanstalk:us-west-2::platform/PHP 7.1 running on 64bit Amazon Linux/2.6.5',
            'EndpointURL': 'awseb-e-sdfsaaaasdfasdfadf4234.us-west-2.elb.amazonaws.com',
            'SolutionStackName': '64bit Amazon Linux 2017.09 v2.6.5 running PHP 7.1',
            'EnvironmentId': 'e-sfsdfsfasdads',
            'CNAME': 'environment-1.us-west-2.elasticbeanstalk.com',
            'AbortableOperationInProgress': False,
            'Tier': {
                'Version': '1.0',
                'Type': 'Standard',
                'Name': 'WebServer'
            },
            'Health': 'Green',
            'DateUpdated': datetime.datetime(2018, 3, 27, 23, 47, 41, 830000, tzinfo=tz.tzutc()),
            'DateCreated': datetime.datetime(2018, 3, 27, 23, 44, 36, 749000, tzinfo=tz.tzutc()),
            'EnvironmentArn': 'arn:aws:elasticbeanstalk:us-west-2:123123123123:environment/my-application/environment-1'
        },
        {
            'ApplicationName': 'my-application',
            'EnvironmentName': 'environment-2',
            'VersionLabel': 'Sample Application',
            'Status': 'Ready',
            'Description': 'Environment created from the EB CLI using "eb create"',
            'EnvironmentLinks': [

            ],
            'PlatformArn': 'arn:aws:elasticbeanstalk:us-west-2::platform/PHP 5.3 running on 64bit Amazon Linux/0.1.0',
            'EndpointURL': 'sdfsaaaasdfasdfadf4234.us-west-2.elb.amazonaws.com',
            'SolutionStackName': '64bit Amazon Linux running PHP 5.3',
            'EnvironmentId': 'e-sfsdfsfasdads',
            'CNAME': 'environment-2.gpcmwngwdj.us-west-2.elasticbeanstalk.com',
            'AbortableOperationInProgress': False,
            'Tier': {
                'Version': '1.0',
                'Type': 'Standard',
                'Name': 'WebServer'
            },
            'Health': 'Green',
            'DateUpdated': datetime.datetime(2018, 3, 6, 23, 31, 6, 453000, tzinfo=tz.tzutc()),
            'DateCreated': datetime.datetime(2018, 3, 6, 23, 24, 55, 525000, tzinfo=tz.tzutc()),
            'EnvironmentArn': 'arn:aws:elasticbeanstalk:us-west-2:123123123123:environment/environment-2/environment-2'
        },
        {
            'ApplicationName': 'my-application',
            'EnvironmentName': 'environment-3',
            'VersionLabel': 'Sample Application',
            'Status': 'Ready',
            'Description': 'Environment created from the EB CLI using "eb create"',
            'EnvironmentLinks': [

            ],
            'PlatformArn': 'arn:aws:elasticbeanstalk:us-west-2::platform/PHP 5.3 running on 64bit Amazon Linux/0.1.0',
            'EndpointURL': 'awseb-e-sdfsaaaasdfasdfadf4234.us-west-2.elb.amazonaws.com',
            'SolutionStackName': '64bit Amazon Linux running PHP 5.3',
            'EnvironmentId': 'e-sfsdfsfasdads',
            'CNAME': 'environment-2.gpcmwngwdj.us-west-2.elasticbeanstalk.com',
            'AbortableOperationInProgress': False,
            'Tier': {
                'Version': '1.0',
                'Type': 'Standard',
                'Name': 'WebServer'
            },
            'Health': 'Green',
            'DateUpdated': datetime.datetime(2018, 3, 6, 23, 22, 9, 697000, tzinfo=tz.tzutc()),
            'DateCreated': datetime.datetime(2018, 3, 6, 23, 16, 16, tzinfo=tz.tzutc()),
            'EnvironmentArn': 'arn:aws:elasticbeanstalk:us-west-2:123123123123:environment/my-application/environment-3'
        },
        {
            'ApplicationName': 'my-application',
            'EnvironmentName': 'environment-4',
            'VersionLabel': 'Sample Application',
            'Status': 'Ready',
            'Description': 'Environment created from the EB CLI using "eb create"',
            'EnvironmentLinks': [

            ],
            'PlatformArn': 'arn:aws:elasticbeanstalk:us-west-2::platform/PHP 5.3 running on 64bit Amazon Linux/0.1.0',
            'EndpointURL': 'awseb-e-sdffsddfgdsfgfgfasdfadf4234.us-west-2.elb.amazonaws.com',
            'SolutionStackName': '64bit Amazon Linux running PHP 5.3',
            'EnvironmentId': 'e-sfasdgadsgsdfg',
            'CNAME': 'environment-2.fghjfghjfghj.us-west-2.elasticbeanstalk.com',
            'AbortableOperationInProgress': False,
            'Tier': {
                'Version': '1.0',
                'Type': 'SQS/HTTP',
                'Name': 'Worker'
            },
            'Health': 'Green',
            'DateUpdated': datetime.datetime(2018, 3, 6, 23, 22, 9, 697000, tzinfo=tz.tzutc()),
            'DateCreated': datetime.datetime(2018, 3, 6, 23, 16, 16, tzinfo=tz.tzutc()),
            'EnvironmentArn': 'arn:aws:elasticbeanstalk:us-west-2:123123123123:environment/my-application/environment-3'
        }
    ]
}


DESCRIBE_ENVIRONMENTS_RESPONSE__SINGLE_ENVIRONMENT = {
    'Environments': [
        {
            'ApplicationName': 'my-application',
            'EnvironmentName': 'environment-1',
            'VersionLabel': 'Sample Application',
            'Status': 'Ready',
            'Description': 'Environment created from the EB CLI using "eb create"',
            'EnvironmentLinks': [

            ],
            'PlatformArn': 'arn:aws:elasticbeanstalk:us-west-2::platform/PHP 7.1 running on 64bit Amazon Linux/2.6.5',
            'EndpointURL': 'awseb-e-sdfsaaaasdfasdfadf4234.us-west-2.elb.amazonaws.com',
            'SolutionStackName': '64bit Amazon Linux 2017.09 v2.6.5 running PHP 7.1',
            'EnvironmentId': 'e-sfsdfsfasdads',
            'CNAME': 'environment-1.us-west-2.elasticbeanstalk.com',
            'AbortableOperationInProgress': False,
            'Tier': {
                'Version': '1.0',
                'Type': 'Standard',
                'Name': 'WebServer'
            },
            'Health': 'Green',
            'DateUpdated': datetime.datetime(2018, 3, 27, 23, 47, 41, 830000, tzinfo=tz.tzutc()),
            'DateCreated': datetime.datetime(2018, 3, 27, 23, 44, 36, 749000, tzinfo=tz.tzutc()),
            'EnvironmentArn': 'arn:aws:elasticbeanstalk:us-west-2:123123123123:environment/my-application/environment-1'
        }
    ]
}


DESCRIBE_APPLICATION_VERSIONS_RESPONSE = {
    "ApplicationVersions": [
        {
            "ApplicationName": "my-application",
            "VersionLabel": "version-label-1",
            "Description": "update cover page",
            "DateCreated": "2015-07-23T01:32:26.079Z",
            "DateUpdated": "2015-07-23T01:32:26.079Z",
            "SourceBundle": {
                "S3Bucket": "elasticbeanstalk-us-west-2-123123123123",
                "S3Key": "my-app/9112-stage-150723_224258.war"
            }
        },
        {
            "ApplicationName": "my-application",
            "VersionLabel": "version-label-2",
            "Description": "initial version",
            "DateCreated": "2015-07-23T22:26:10.816Z",
            "DateUpdated": "2015-07-23T22:26:10.816Z",
            "SourceBundle": {
                "S3Bucket": "elasticbeanstalk-us-west-2-123123123123",
                "S3Key": "my-app/9111-stage-150723_222618.war"
            }
        }
    ]
}


GET_TEMPLATE_RESPONSE = {
    "TemplateBody": {
        "AWSTemplateFormatVersion": "2010-09-09",
        "Outputs": {
            "BucketName": {
                "Description": "Name of S3 bucket to hold website content",
                "Value": {
                    "Ref": "S3Bucket"
                }
            }
        },
        "Description": "AWS CloudFormation Sample Template S3_Bucket: Sample template showing how to create a publicly accessible S3 bucket. **WARNING** This template creates an S3 bucket. You will be billed for the AWS resources used if you create a stack from this template.",
        "Resources": {
            "S3Bucket": {
                "Type": "AWS::S3::Bucket",
                "Properties": {
                    "AccessControl": "PublicRead"
                }
            }
        }
    }
}


DESCRIBE_STACKS_RESPONSE = {
    'Stacks': [
        {
            'StackId': 'stack_id',
            'StackName': 'stack_name',
            'Description': "my cloud formation stack",
            'Parameters': []
        }
    ]
}


DESCRIBE_STACKS_RESPONSE__2 = {
    'Stacks': [
        {
            'StackId': 'arn:aws:cloudformation:us-west-2:123123123123:stack/'
                       'sam-cfn-stack-2/13bfae60-b196-11e8-b2de-0ad5109330ec',
            'StackName': 'sam-cfn-stack-2',
            'Description': 'sam-app\nSample SAM Template for sam-app\n',
            'CreationTime': datetime.datetime(2018, 9, 6, 5, 31, 16, 951000, tzinfo=tz.tzutc()),
            'DeletionTime': datetime.datetime(2018, 9, 19, 4, 41, 12, 407000, tzinfo=tz.tzutc()),
            'LastUpdatedTime': datetime.datetime(2018, 9, 19, 4, 41, 8, 956000, tzinfo=tz.tzutc()),
            'RollbackConfiguration': {},
            'StackStatus': 'ROLLBACK_COMPLETE',
            'DisableRollback': False,
            'NotificationARNs': [],
            'Capabilities': ['CAPABILITY_IAM'],
            'Tags': [],
            'EnableTerminationProtection': False
        }
    ],
    'ResponseMetadata': {
        'RequestId': 'd7e5be6b-bc30-11e8-8808-394f6de86aea',
        'HTTPStatusCode': 200,
        'HTTPHeaders': {
            'x-amzn-requestid': 'd7e5be6b-bc30-11e8-8808-394f6de86aea',
            'content-type': 'text/xml',
            'content-length': '1229',
            'date': 'Wed, 19 Sep 2018 17:24:20 GMT'
        },
        'RetryAttempts': 0
    }
}


DESCRIBE_LOG_STREAMS_RESPONSE = {
    'logStreams': [
        {
            'lastIngestionTime': 1522104918499,
            'firstEventTimestamp': 1522104834000,
            'uploadSequenceToken': '49581045816077287818028642094834630247536380630456711345',
            'arn': 'arn:aws:logs:us-east-1:123123123123:log-group:/aws/elasticbeanstalk/env-name/environment-health.log:log-stream:archive-health-2018-03-26',
            'creationTime': 1522104860498,
            'storedBytes': 0,
            'logStreamName': 'archive-health-2018-03-26',
            'lastEventTimestamp': 1522104864000
        },
        {
            'lastIngestionTime': 1522185082040,
            'firstEventTimestamp': 1522114566000,
            'uploadSequenceToken': '495782746617210878802139966459935713174460150927741245',
            'arn': 'arn:aws:logs:us-east-1:123123123123:log-group:/aws/elasticbeanstalk/env-name/environment-health.log:log-stream:archive-health-2018-03-27',
            'creationTime': 1522114571763,
            'storedBytes': 0,
            'logStreamName': 'archive-health-2018-03-27',
            'lastEventTimestamp': 1522185066000
        },
        {
            'lastIngestionTime': 1522273517592,
            'firstEventTimestamp': 1522214971000,
            'uploadSequenceToken': '4957832466795318902173372629991138882266085318618712345',
            'arn': 'arn:aws:logs:us-east-1:123123123123:log-group:/aws/elasticbeanstalk/env-name/environment-health.log:log-stream:archive-health-2018-03-28',
            'creationTime': 1522215000673,
            'storedBytes': 0,
            'logStreamName': 'archive-health-2018-03-28',
            'lastEventTimestamp': 1522273511000
        },
    ]
}


BATCH_GET_BUILDS = {
    "builds": [
        {
            "id": "Elastic-Beanstalk-my-web-app-app-170706_000919-uUTqM:3362ef1d-584d-48c1-800a-c1c695b71562",
            "arn": "arn:aws:codebuild:us-west-2:123123123123:build/Elastic-Beanstalk-my-web-app-app-170706_000919-uUTqM:3362ef1d-584d-48c1-800a-c1c695b71562",
            "startTime": 1499299760.483,
            "endTime": 1499299762.231,
            "currentPhase": "COMPLETED",
            "buildStatus": "FAILED",
            "projectName": "Elastic-Beanstalk-my-web-app-app-170706_000919-uUTqM",
            "phases": [
                {
                    "phaseType": "SUBMITTED",
                    "phaseStatus": "SUCCEEDED",
                    "startTime": 1499299760.483,
                    "endTime": 1499299761.321,
                    "durationInSeconds": 0
                },
                {
                    "phaseType": "PROVISIONING",
                    "phaseStatus": "CLIENT_ERROR",
                    "startTime": 1499299761.321,
                    "endTime": 1499299762.231,
                    "durationInSeconds": 0,
                    "contexts": [
                        {
                            "statusCode": "ACCESS_DENIED",
                            "message": "Service role arn:aws:iam::123123123123:role/service-role/codebuild-sample_maven_project-service-role does not allow AWS CodeBuild to create Amazon CloudWatch Logs log streams for build arn:aws:codebuild:us-west-2:123123123123:build/Elastic-Beanstalk-my-web-app-app-170706_001032-OYjRZ:a4db9491-91ba-4614-b5e4-3f8d9e994a19"
                        }
                    ]
                },
                {
                    "phaseType": "COMPLETED",
                    "startTime": 1499299762.231
                }
            ],
            "source": {
                "type": "S3",
                "location": "elasticbeanstalk-us-west-2-123123123123/my-web-app/app-170706_000919.zip"
            },
            "artifacts": {
                "location": "arn:aws:s3:::elasticbeanstalk-us-west-2-123123123123/resources/my-web-app/codebuild/codebuild-app-170706_000919.zip"
            },
            "environment": {
                "type": "LINUX_CONTAINER",
                "image": "aws/codebuild/java:openjdk-8",
                "computeType": "BUILD_GENERAL1_SMALL",
                "environmentVariables": [],
                "privilegedMode": False
            },
            "timeoutInMinutes": 60,
            "buildComplete": True,
            "initiator": "some-user"
        },
        {
            "id": "Elastic-Beanstalk-my-web-app-app-170706_001032-OYjRZ:a4db9491-91ba-4614-b5e4-3f8d9e994a19",
            "arn": "arn:aws:codebuild:us-west-2:123123123123:build/Elastic-Beanstalk-my-web-app-app-170706_001032-OYjRZ:a4db9491-91ba-4614-b5e4-3f8d9e994a19",
            "startTime": 1499299833.657,
            "endTime": 1499299835.069,
            "currentPhase": "COMPLETED",
            "buildStatus": "FAILED",
            "projectName": "Elastic-Beanstalk-my-web-app-app-170706_001032-OYjRZ",
            "phases": [
                {
                    "phaseType": "SUBMITTED",
                    "phaseStatus": "SUCCEEDED",
                    "startTime": 1499299833.657,
                    "endTime": 1499299834.0,
                    "durationInSeconds": 0
                },
                {
                    "phaseType": "PROVISIONING",
                    "phaseStatus": "CLIENT_ERROR",
                    "startTime": 1499299834.0,
                    "endTime": 1499299835.069,
                    "durationInSeconds": 1,
                    "contexts": [
                        {
                            "statusCode": "ACCESS_DENIED",
                            "message": "Service role arn:aws:iam::123123123123:role/service-role/codebuild-sample_maven_project-service-role does not allow AWS CodeBuild to create Amazon CloudWatch Logs log streams for build arn:aws:codebuild:us-west-2:123123123123:build/Elastic-Beanstalk-my-web-app-app-170706_001032-OYjRZ:a4db9491-91ba-4614-b5e4-3f8d9e994a19"
                        }
                    ]
                },
                {
                    "phaseType": "COMPLETED",
                    "startTime": 1499299835.069
                }
            ],
            "source": {
                "type": "S3",
                "location": "elasticbeanstalk-us-west-2-123123123123/my-web-app/app-170706_001032.zip"
            },
            "artifacts": {
                "location": "arn:aws:s3:::elasticbeanstalk-us-west-2-123123123123/resources/my-web-app/codebuild/codebuild-app-170706_001032.zip"
            },
            "environment": {
                "type": "LINUX_CONTAINER",
                "image": "aws/codebuild/java:openjdk-8",
                "computeType": "BUILD_GENERAL1_SMALL",
                "environmentVariables": [],
                "privilegedMode": False
            },
            "timeoutInMinutes": 60,
            "buildComplete": True,
            "initiator": "some-user"
        }
    ],
    "buildsNotFound": [
        "bad-batch-id-170706_001032-OYjRZ:a4db9491-91ba-4614-b5e4-3f8d9e994a19"
    ]
}


LIST_CURATED_ENVIRONMENT_IMAGES_RESPONSE = {
    'platforms':
        [
            {
                'languages': [
                    {
                        'images': [
                            {
                                'name': 'aws/codebuild/eb-java-7-amazonlinux-64:2.1.3', 'description': 'AWS ElasticBeanstalk - Java 7 Running on Amazon Linux 64bit v2.1.3'
                            },
                            {
                                'name': 'aws/codebuild/eb-java-8-amazonlinux-64:2.1.3', 'description': 'AWS ElasticBeanstalk - Java 8 Running on Amazon Linux 64bit v2.1.3'
                            },
                            {
                                'name': 'aws/codebuild/eb-java-7-amazonlinux-64:2.1.6', 'description': 'AWS ElasticBeanstalk - Java 7 Running on Amazon Linux 64bit v2.1.6'
                            },
                            {
                                'name': 'aws/codebuild/eb-java-8-amazonlinux-64:2.1.6', 'description': 'AWS ElasticBeanstalk - Java 8 Running on Amazon Linux 64bit v2.1.6'
                            }
                        ],
                        'language': 'Java'
                    },
                    {
                        'images': [
                            {
                                'name': 'aws/codebuild/eb-go-1.5-amazonlinux-64:2.1.3', 'description': 'AWS ElasticBeanstalk - Go 1.5 Running on Amazon Linux 64bit v2.1.3'
                            },
                            {
                                'name': 'aws/codebuild/eb-go-1.5-amazonlinux-64:2.1.6', 'description': 'AWS ElasticBeanstalk - Go 1.5 Running on Amazon Linux 64bit v2.1.6'
                            }
                        ],
                        'language': 'Golang'
                    },
                    {
                        'images': [
                            {
                                'name': 'aws/codebuild/android-java-6:24.4.1', 'description': 'AWS CodeBuild - Android 24.4.1 with java 6'
                            },
                            {
                                'name': 'aws/codebuild/android-java-7:24.4.1', 'description': 'AWS CodeBuild - Android 24.4.1 with java 7'
                            },
                            {
                                'name': 'aws/codebuild/android-java-8:24.4.1', 'description': 'AWS CodeBuild - Android 24.4.1 with java 8'
                            }
                        ],
                        'language': 'Android'
                    }
                ]
            }
        ],
    'ResponseMetadata': {
        'date': 'Tue, 22 Nov 2016 21:36:19 GMT',
        'RetryAttempts': 0, 'HTTPStatusCode': 200,
        'RequestId': 'b47ba2d1-b0fb-11e6-a6a7-6fc6c5a33aee'
    }
}


LIST_REPOSITORIES_RESPONSE = {
    "repositories": [
        {
            "repositoryName": "my-repository",
            "repositoryId": "f7579e13-b83e-4027-aaef-650c0EXAMPLE",
        },
        {
            "repositoryName": "my-other-repository",
            "repositoryId": "cfc29ac4-b0cb-44dc-9990-f6f51EXAMPLE"
        }
    ]
}


LIST_BRANCHES_RESPONSE = {
    'branches': [
        'development',
        'master'
    ]
}

GET_BRANCH_RESPONSE = {
    "BranchInfo": {
        "commitID": "068f60ebd5b7d9a0ad071b8a20ccdf8178491295",
        "branchName": "master"
    }
}


GET_REPOSITORY_RESPONSE = {
    "repositoryMetadata": {
        "creationDate": 1429203623.625,
        "defaultBranch": "master",
        "repositoryName": "MyDemoRepo",
        "cloneUrlSsh": "ssh://git-codecommit.us-east-1.amazonaws.com/v1/repos/v1/repos/MyDemoRepo",
        "lastModifiedDate": 1430783812.0869999,
        "repositoryDescription": "My demonstration repository",
        "cloneUrlHttp": "https://codecommit.us-east-1.amazonaws.com/v1/repos/MyDemoRepo",
        "repositoryId": "f7579e13-b83e-4027-aaef-650c0EXAMPLE",
        "Arn": "arn:aws:codecommit:us-east-1:80398EXAMPLE:MyDemoRepo,",
        "accountId": "111111111111"
    }
}

LIST_REPOSITORIES_RESPONSE = {
    "repositories": [
        {
            "repositoryName": "my-repository",
            "repositoryId": "f7579e13-b83e-4027-aaef-650c0EXAMPLE",
        },
        {
            "repositoryName": "my-other-repository",
            "repositoryId": "cfc29ac4-b0cb-44dc-9990-f6f51EXAMPLE"
        }
    ]
}


LIST_BRANCHES_RESPONSE = {
    'branches': [
        'development',
        'master'
    ]
}

GET_BRANCH_RESPONSE = {
    "BranchInfo": {
        "commitID": "068f60ebd5b7d9a0ad071b8a20ccdf8178491295",
        "branchName": "master"
    }
}


GET_REPOSITORY_RESPONSE = {
    "repositoryMetadata": {
        "creationDate": 1429203623.625,
        "defaultBranch": "master",
        "repositoryName": "MyDemoRepo",
        "cloneUrlSsh": "ssh://git-codecommit.us-east-1.amazonaws.com/v1/repos/v1/repos/MyDemoRepo",
        "lastModifiedDate": 1430783812.0869999,
        "repositoryDescription": "My demonstration repository",
        "cloneUrlHttp": "https://codecommit.us-east-1.amazonaws.com/v1/repos/MyDemoRepo",
        "repositoryId": "f7579e13-b83e-4027-aaef-650c0EXAMPLE",
        "Arn": "arn:aws:codecommit:us-east-1:80398EXAMPLE:MyDemoRepo,",
        "accountId": "111111111111"
    }
}


DESCRIBE_ACCOUNT_ATTRIBUTES_RESPONSE__WITHOUT_DEFAULT_VPC = {
    "AccountAttributes": [
        {
            "AttributeName": "vpc-max-security-groups-per-interface",
            "AttributeValues": [
                {
                    "AttributeValue": "5"
                }
            ]
        },
        {
            "AttributeName": "max-instances",
            "AttributeValues": [
                {
                    "AttributeValue": "20"
                }
            ]
        },
        {
            "AttributeName": "supported-platforms",
            "AttributeValues": [
                {
                    "AttributeValue": "EC2"
                },
                {
                    "AttributeValue": "VPC"
                }
            ]
        },
        {
            "AttributeName": "default-vpc",
            "AttributeValues": [
                {
                    "AttributeValue": "none"
                }
            ]
        },
        {
            "AttributeName": "max-elastic-ips",
            "AttributeValues": [
                {
                    "AttributeValue": "5"
                }
            ]
        },
        {
            "AttributeName": "vpc-max-elastic-ips",
            "AttributeValues": [
                {
                    "AttributeValue": "5"
                }
            ]
        }
    ]
}


DESCRIBE_ACCOUNT_ATTRIBUTES_RESPONSE = {
    "AccountAttributes": [
        {
            "AttributeName": "vpc-max-security-groups-per-interface",
            "AttributeValues": [
                {
                    "AttributeValue": "5"
                }
            ]
        },
        {
            "AttributeName": "max-instances",
            "AttributeValues": [
                {
                    "AttributeValue": "20"
                }
            ]
        },
        {
            "AttributeName": "supported-platforms",
            "AttributeValues": [
                {
                    "AttributeValue": "EC2"
                },
                {
                    "AttributeValue": "VPC"
                }
            ]
        },
        {
            "AttributeName": "default-vpc",
            "AttributeValues": [
                {
                    "AttributeValue": "vpc-123124"
                }
            ]
        },
        {
            "AttributeName": "max-elastic-ips",
            "AttributeValues": [
                {
                    "AttributeValue": "5"
                }
            ]
        },
        {
            "AttributeName": "vpc-max-elastic-ips",
            "AttributeValues": [
                {
                    "AttributeValue": "5"
                }
            ]
        }
    ]
}


DESCRIBE_INSTANCES_RESPONSE = {
    "Reservations": [
        {
            "Groups": [],
            "Instances": [
                {
                    "AmiLaunchIndex": 0,
                    "ImageId": "ami-4e79ed36",
                    "InstanceId": "i-0bdf23424244",
                    "InstanceType": "t2.large",
                    "KeyName": "aws-eb-us-west-2",
                    "LaunchTime": "2018-05-11T19:58:03.000Z",
                    "Monitoring": {
                        "State": "disabled"
                    },
                    "Placement": {
                        "AvailabilityZone": "us-west-2b",
                        "GroupName": "",
                        "Tenancy": "default"
                    },
                    "PrivateDnsName": "ip-172-31-35-210.us-west-2.compute.internal",
                    "PrivateIpAddress": "172.31.35.210",
                    "ProductCodes": [],
                    "PublicDnsName": "ec2-54-218-96-238.us-west-2.compute.amazonaws.com",
                    "PublicIpAddress": "54.218.96.238",
                    "State": {
                        "Code": 16,
                        "Name": "running"
                    },
                    "StateTransitionReason": "",
                    "SubnetId": "subnet-3cc4a775",
                    "VpcId": "vpc-213123123",
                    "Architecture": "x86_64",
                    "BlockDeviceMappings": [
                        {
                            "DeviceName": "/dev/sda1",
                            "Ebs": {
                                "AttachTime": "2018-05-11T19:58:03.000Z",
                                "DeleteOnTermination": True,
                                "Status": "attached",
                                "VolumeId": "vol-02d476a764aaaf3b5"
                            }
                        }
                    ],
                    "ClientToken": "",
                    "EbsOptimized": False,
                    "EnaSupport": True,
                    "Hypervisor": "xen",
                    "NetworkInterfaces": [
                        {
                            "Association": {
                                "IpOwnerId": "amazon",
                                "PublicDnsName": "ec2-54-218-96-238.us-west-2.compute.amazonaws.com",
                                "PublicIp": "54.218.96.238"
                            },
                            "Attachment": {
                                "AttachTime": "2018-05-11T19:58:03.000Z",
                                "AttachmentId": "eni-attach-5ddfc3a8",
                                "DeleteOnTermination": True,
                                "DeviceIndex": 0,
                                "Status": "attached"
                            },
                            "Description": "",
                            "Groups": [
                                {
                                    "GroupName": "ubuntu-desktop",
                                    "GroupId": "sg-12312313"
                                }
                            ],
                            "Ipv6Addresses": [],
                            "MacAddress": "06:a4:a3:af:e6:d0",
                            "NetworkInterfaceId": "eni-b3d5d1ba",
                            "OwnerId": "123123123123",
                            "PrivateDnsName": "ip-172-31-35-210.us-west-2.compute.internal",
                            "PrivateIpAddress": "172.31.35.210",
                            "PrivateIpAddresses": [
                                {
                                    "Association": {
                                        "IpOwnerId": "amazon",
                                        "PublicDnsName": "ec2-54-218-96-238.us-west-2.compute.amazonaws.com",
                                        "PublicIp": "54.218.96.238"
                                    },
                                    "Primary": True,
                                    "PrivateDnsName": "ip-172-31-35-210.us-west-2.compute.internal",
                                    "PrivateIpAddress": "172.31.35.210"
                                }
                            ],
                            "SourceDestCheck": True,
                            "Status": "in-use",
                            "SubnetId": "subnet-3cc4a775",
                            "VpcId": "vpc-213123123"
                        }
                    ],
                    "RootDeviceName": "/dev/sda1",
                    "RootDeviceType": "ebs",
                    "SecurityGroups": [
                        {
                            "GroupName": "ubuntu-desktop",
                            "GroupId": "sg-12312313"
                        }
                    ],
                    "SourceDestCheck": True,
                    "Tags": [
                        {
                            "Key": "Name",
                            "Value": "ubuntu-machine"
                        }
                    ],
                    "VirtualizationType": "hvm"
                }
            ],
            "OwnerId": "123123123123",
            "ReservationId": "r-02cfb440332bf9df9"
        },
        {
            "Groups": [],
            "Instances": [
                {
                    "AmiLaunchIndex": 0,
                    "ImageId": "ami-c2c3a2a2",
                    "InstanceId": "i-0a70921e1e45a6517",
                    "InstanceType": "m4.xlarge",
                    "KeyName": "windows-aws-eb",
                    "LaunchTime": "2017-05-31T00:52:50.000Z",
                    "Monitoring": {
                        "State": "disabled"
                    },
                    "Placement": {
                        "AvailabilityZone": "us-west-2c",
                        "GroupName": "",
                        "Tenancy": "default"
                    },
                    "Platform": "windows",
                    "PrivateDnsName": "ip-172-31-0-122.us-west-2.compute.internal",
                    "PrivateIpAddress": "172.31.0.122",
                    "ProductCodes": [],
                    "PublicDnsName": "ec2-34-209-214-26.us-west-2.compute.amazonaws.com",
                    "PublicIpAddress": "34.209.214.26",
                    "State": {
                        "Code": 16,
                        "Name": "running"
                    },
                    "StateTransitionReason": "",
                    "SubnetId": "subnet-2f6f9d74",
                    "VpcId": "vpc-213123123",
                    "Architecture": "x86_64",
                    "BlockDeviceMappings": [
                        {
                            "DeviceName": "/dev/sda1",
                            "Ebs": {
                                "AttachTime": "2017-05-31T00:52:51.000Z",
                                "DeleteOnTermination": True,
                                "Status": "attached",
                                "VolumeId": "vol-030b449998df8846b"
                            }
                        }
                    ],
                    "ClientToken": "DJLqN1496191969659",
                    "EbsOptimized": True,
                    "EnaSupport": True,
                    "Hypervisor": "xen",
                    "IamInstanceProfile": {
                        "Arn": "arn:aws:iam::123123123123:instance-profile/aws-elasticbeanstalk-ec2-role",
                        "Id": "AIPAI6P3ZEQQGJWNJ4F5G"
                    },
                    "NetworkInterfaces": [
                        {
                            "Association": {
                                "IpOwnerId": "amazon",
                                "PublicDnsName": "ec2-34-209-214-26.us-west-2.compute.amazonaws.com",
                                "PublicIp": "34.209.214.26"
                            },
                            "Attachment": {
                                "AttachTime": "2017-05-31T00:52:50.000Z",
                                "AttachmentId": "eni-attach-544e2437",
                                "DeleteOnTermination": True,
                                "DeviceIndex": 0,
                                "Status": "attached"
                            },
                            "Description": "",
                            "Groups": [
                                {
                                    "GroupName": "launch-wizard-2",
                                    "GroupId": "sg-234523456"
                                }
                            ],
                            "Ipv6Addresses": [],
                            "MacAddress": "0a:fd:e7:15:ce:88",
                            "NetworkInterfaceId": "eni-b50f2aba",
                            "OwnerId": "123123123123",
                            "PrivateDnsName": "ip-172-31-0-122.us-west-2.compute.internal",
                            "PrivateIpAddress": "172.31.0.122",
                            "PrivateIpAddresses": [
                                {
                                    "Association": {
                                        "IpOwnerId": "amazon",
                                        "PublicDnsName": "ec2-34-209-214-26.us-west-2.compute.amazonaws.com",
                                        "PublicIp": "34.209.214.26"
                                    },
                                    "Primary": True,
                                    "PrivateDnsName": "ip-172-31-0-122.us-west-2.compute.internal",
                                    "PrivateIpAddress": "172.31.0.122"
                                }
                            ],
                            "SourceDestCheck": True,
                            "Status": "in-use",
                            "SubnetId": "subnet-2f6f9d74",
                            "VpcId": "vpc-213123123"
                        }
                    ],
                    "RootDeviceName": "/dev/sda1",
                    "RootDeviceType": "ebs",
                    "SecurityGroups": [
                        {
                            "GroupName": "launch-wizard-2",
                            "GroupId": "sg-234523456"
                        }
                    ],
                    "SourceDestCheck": True,
                    "Tags": [
                        {
                            "Key": "Name",
                            "Value": "windows-machine"
                        }
                    ],
                    "VirtualizationType": "hvm"
                }
            ],
            "OwnerId": "123123123123",
            "ReservationId": "r-0def3a75c3ac44334"
        },
    ]
}


CREATE_APPLICATION_VERSION_RESPONSE = {
    "ApplicationVersion": {
        "ApplicationName": "my-application",
        "VersionLabel": "v1",
        "Description": "MyAppv1",
        "DateCreated": "2015-02-03T23:01:25.412Z",
        "DateUpdated": "2015-02-03T23:01:25.412Z",
        "SourceBundle": {
            "S3Bucket": "my-bucket",
            "S3Key": "sample.war"
        }
    }
}


CREATE_APPLICATION_VERSION_RESPONSE__WITH_CODECOMMIT = {
    "ApplicationVersion": {
        "ApplicationName": "my-application",
        "VersionLabel": "v1",
        "Description": "MyAppv1",
        "DateCreated": "2015-02-03T23:01:25.412Z",
        "DateUpdated": "2015-02-03T23:01:25.412Z",
        "SourceBuildInformation": {
            "SourceType": "git",
            "SourceRepository": "my-repository",
            "SourceLocation": "532452452eeaadcbf532452452eeaadcbf"
        }
    }
}


DELETE_PLATFORM_VERSION_RESPONSE = {
    "PlatformSummary": {
        "PlatformArn": "arn:aws:elasticbeanstalk:us-west-2:123123123123:platform/zqozvhohaq-custom-platform/1.0.0",
        "PlatformOwner": "self",
        "PlatformStatus": "Deleting",
        "SupportedTierList": [],
        "SupportedAddonList": []
    }
}


LIST_CUSTOM_PLATFOM_VERSIONS_RESPONSE = {
    "PlatformSummaryList": [
        {
            "PlatformArn": "arn:aws:elasticbeanstalk:us-west-2:123123123123:platform/ajdfzejiub-custom-platform/1.0.1",
            "PlatformOwner": "self",
            "PlatformStatus": "Ready",
            "PlatformCategory": "custom",
            "OperatingSystemName": "Ubuntu",
            "OperatingSystemVersion": "16.04",
            "SupportedTierList": [
                "WebServer/Standard",
                "Worker/SQS/HTTP"
            ],
            "SupportedAddonList": [
                "Log/S3",
                "WorkerDaemon/SQSD"
            ]
        },
        {
            "PlatformArn": "arn:aws:elasticbeanstalk:us-west-2:123123123123:platform/ajdfzejiub-custom-platform/1.0.0",
            "PlatformOwner": "self",
            "PlatformStatus": "Ready",
            "PlatformCategory": "custom",
            "OperatingSystemName": "Ubuntu",
            "OperatingSystemVersion": "16.04",
            "SupportedTierList": [
                "WebServer/Standard",
                "Worker/SQS/HTTP"
            ],
            "SupportedAddonList": [
                "Log/S3",
                "WorkerDaemon/SQSD"
            ]
        },
        {
            "PlatformArn": "arn:aws:elasticbeanstalk:us-west-2:123123123123:platform/axczpaybmq-custom-platform/1.0.0",
            "PlatformOwner": "self",
            "PlatformStatus": "Failed",
            "SupportedTierList": [],
            "SupportedAddonList": []
        }
    ]
}


LIST_CUSTOM_PLATFOM_VERSIONS_RESPONSE__WITH_NEXT_TOKEN = {
    'PlatformSummaryList': LIST_CUSTOM_PLATFOM_VERSIONS_RESPONSE['PlatformSummaryList'],
    'NextToken': '123123123123123123123'
}


DESCRIBE_CUSTOM_PLATFORM_VERSION_RESPONSE = {
    "PlatformDescription": {
        "PlatformArn": "arn:aws:elasticbeanstalk:us-west-2:123123123123:platform/xutrezqmqw-custom-platform/1.0.0",
        "PlatformOwner": "self",
        "PlatformName": "xutrezqmqw-custom-platform",
        "PlatformVersion": "1.0.0",
        "PlatformStatus": "Ready",
        "DateCreated": "2018-05-14T22:57:03.896Z",
        "DateUpdated": "2018-05-14T23:09:43.799Z",
        "PlatformCategory": "custom",
        "Description": "Sample NodeJs Container.",
        "Maintainer": "<please enter your name here>",
        "OperatingSystemName": "Ubuntu",
        "OperatingSystemVersion": "16.04",
        "ProgrammingLanguages": [
            {
                "Name": "ECMAScript",
                "Version": "ECMA-262"
            }
        ],
        "Frameworks": [
            {
                "Name": "NodeJs",
                "Version": "4.4.1"
            }
        ],
        "CustomAmiList": [
            {
                "VirtualizationType": "pv",
                "ImageId": "ami-c96311b1"
            },
            {
                "VirtualizationType": "hvm",
                "ImageId": "ami-c96311b1"
            }
        ],
        "SupportedTierList": [
            "WebServer/Standard",
            "Worker/SQS/HTTP"
        ],
        "SupportedAddonList": [
            "Log/S3",
            "WorkerDaemon/SQSD"
        ]
    }
}


CREATE_APPLICATION_RESPONSE = {
    "Application": {
        "ApplicationName": "my-application",
        "ConfigurationTemplates": [],
        "DateUpdated": datetime.datetime(2018, 3, 27, 23, 47, 41, 830000, tzinfo=tz.tzutc()),
        "Description": "my-application",
        "DateCreated": datetime.datetime(2018, 3, 27, 23, 47, 41, 830000, tzinfo=tz.tzutc())
    }
}


CREATE_ENVIRONMENT_RESPONSE = {
    "ApplicationName": "my-application",
    "EnvironmentName": "environment-1",
    "VersionLabel": "v1",
    "Status": "Launching",
    "EnvironmentId": "e-izqpassy4h",
    "SolutionStackName": "arn:aws:elasticbeanstalk:us-west-2::platform/Docker running on 64bit Amazon Linux/2.1.0",
    "CNAME": "my-app.elasticbeanstalk.com",
    "Health": "Grey",
    "Tier": {
        "Type": "Standard",
        "Name": "WebServer",
        "Version": " "
    },
    "DateUpdated": datetime.datetime(2018, 3, 27, 23, 47, 41, 830000, tzinfo=tz.tzutc()),
    "DateCreated": datetime.datetime(2018, 3, 27, 23, 47, 41, 830000, tzinfo=tz.tzutc()),
    'ResponseMetadata': {
        'RequestId': 'd88449fe-feef-4d28-afdb-c8a34e99f757',
        'HTTPStatusCode': 200,
        'date': 'Wed, 16 May 2018 00:43:52 GMT',
        'RetryAttempts': 0
    }
}


DESCRIBE_APPLICATIONS_RESPONSE = {
    "Applications": [
        {
            "ApplicationName": "my-application",
            "ConfigurationTemplates": [],
            "DateUpdated": "2015-08-13T21:05:44.376Z",
            "Versions": [
                "Sample Application"
            ],
            "DateCreated": "2015-08-13T21:05:44.376Z"
        },
        {
            "ApplicationName": "my-application-2",
            "Description": "Application created from the EB CLI using \"eb init\"",
            "Versions": [
                "Sample Application"
            ],
            "DateCreated": "2015-08-13T19:05:43.637Z",
            "ConfigurationTemplates": [],
            "DateUpdated": "2015-08-13T19:05:43.637Z"
        },
        {
            "ApplicationName": "my-application-3",
            "ConfigurationTemplates": [],
            "DateUpdated": "2015-08-06T17:50:02.486Z",
            "Versions": [
                "add elasticache",
                "First Release"
            ],
            "DateCreated": "2015-08-06T17:50:02.486Z"
        }
    ],
    'ResponseMetadata': {
        'RequestId': 'd88449fe-feef-4d28-afdb-c8a34e99f757',
        'HTTPStatusCode': 200,
        'date': 'Wed, 16 May 2018 00:43:52 GMT',
        'RetryAttempts': 0
    }
}


DESCRIBE_APPLICATION_RESPONSE = {
    'Applications': [
        {
            "ApplicationName": "my-application",
            "ConfigurationTemplates": [],
            "DateUpdated": "2015-08-13T21:05:44.376Z",
            "Versions": [
                "Sample Application"
            ],
            "DateCreated": "2015-08-13T21:05:44.376Z"
        }
    ]
}
CHECK_DNS_AVAILABILITY_RESPONSE = {
    "Available": True,
    "FullyQualifiedCNAME": "my-cname.elasticbeanstalk.com"
}


DESCRIBE_CONFIGURATION_SETTINGS_RESPONSE = {
    "ConfigurationSettings": [
        {
            "ApplicationName": "my-application",
            "EnvironmentName": "environment-1",
            "Description": "Environment created from the EB CLI using \"eb create\"",
            "DeploymentStatus": "deployed",
            "DateCreated": "2015-08-13T19:16:25Z",
            "OptionSettings": [
                {
                    "OptionName": "Availability Zones",
                    "ResourceName": "AWSEBAutoScalingGroup",
                    "Namespace": "aws:autoscaling:asg",
                    "Value": "Any"
                },
                {
                    "OptionName": "Cooldown",
                    "ResourceName": "AWSEBAutoScalingGroup",
                    "Namespace": "aws:autoscaling:asg",
                    "Value": "360"
                },
                {
                    "OptionName": "ConnectionDrainingTimeout",
                    "ResourceName": "AWSEBLoadBalancer",
                    "Namespace": "aws:elb:policies",
                    "Value": "20"
                },
                {
                    "OptionName": "ConnectionSettingIdleTimeout",
                    "ResourceName": "AWSEBLoadBalancer",
                    "Namespace": "aws:elb:policies",
                    "Value": "60"
                }
            ],
            "Tier": {
                "Name": "Worker",
                "Type": "SQS/HTTP",
                "Version": "2.3"
            },
            "DateUpdated": "2015-08-13T23:30:07Z",
            "SolutionStackName": "64bit Amazon Linux 2015.03 v2.0.0 running Tomcat 8 Java 8"
        }
    ]
}


DESCRIBE_CONFIGURATION_SETTINGS_RESPONSE__2 = {
    'ConfigurationSettings': [
        {
            'SolutionStackName': '64bit Amazon Linux 2018.03 v4.5.1 running Node.js',
            'PlatformArn': 'arn:aws:elasticbeanstalk:us-west-2::platform/Node.js running on 64bit Amazon Linux/4.5.1',
            'ApplicationName': 'vpc-tests',
            'Description': 'Environment created from the EB CLI using "eb create"',
            'EnvironmentName': 'vpc-tests-dev-single',
            'DeploymentStatus': 'deployed',
            'DateCreated': datetime.datetime(2018, 7, 5, 19, 39, 35, tzinfo=tz.tzutc()),
            'DateUpdated': datetime.datetime(2018, 7, 5, 19, 39, 35, tzinfo=tz.tzutc()),
            'Tier': {
                'Type': 'Standard',
                'Name': 'WebServer',
                'Version': '1.0'
            },
            'OptionSettings': [
                {
                    'ResourceName': 'AWSEBAutoScalingGroup',
                    'Namespace': 'aws:autoscaling:asg',
                    'OptionName': 'Availability Zones',
                    'Value': 'Any'
                },
                {
                    'ResourceName': 'AWSEBAutoScalingGroup',
                    'Namespace': 'aws:autoscaling:asg',
                    'OptionName': 'Cooldown',
                    'Value': '360'
                },
                {
                    'ResourceName': 'AWSEBAutoScalingGroup',
                    'Namespace': 'aws:autoscaling:asg',
                    'OptionName': 'Custom Availability Zones',
                    'Value': ''
                },
                {
                    'ResourceName': 'AWSEBAutoScalingGroup',
                    'Namespace': 'aws:autoscaling:asg',
                    'OptionName': 'MaxSize',
                    'Value': '1'
                },
                {
                    'ResourceName': 'AWSEBAutoScalingGroup',
                    'Namespace': 'aws:autoscaling:asg',
                    'OptionName': 'MinSize',
                    'Value': '1'
                },
                {
                    'ResourceName': 'AWSEBAutoScalingLaunchConfiguration',
                    'Namespace': 'aws:autoscaling:launchconfiguration',
                    'OptionName': 'BlockDeviceMappings'
                },
                {
                    'ResourceName': 'AWSEBAutoScalingLaunchConfiguration',
                    'Namespace': 'aws:autoscaling:launchconfiguration',
                    'OptionName': 'EC2KeyName'
                },
                {
                    'ResourceName': 'AWSEBAutoScalingLaunchConfiguration',
                    'Namespace': 'aws:autoscaling:launchconfiguration',
                    'OptionName': 'IamInstanceProfile',
                    'Value': 'aws-elasticbeanstalk-ec2-role'
                },
                {
                    'ResourceName': 'AWSEBAutoScalingLaunchConfiguration',
                    'Namespace': 'aws:autoscaling:launchconfiguration',
                    'OptionName': 'ImageId',
                    'Value': 'ami-65a8e41d'
                },
                {
                    'Namespace': 'aws:autoscaling:launchconfiguration',
                    'OptionName': 'InstanceType',
                    'Value': 't2.micro'
                },
                {
                    'ResourceName': 'AWSEBAutoScalingLaunchConfiguration',
                    'Namespace': 'aws:autoscaling:launchconfiguration',
                    'OptionName': 'MonitoringInterval',
                    'Value': '5 minute'
                },
                {
                    'ResourceName': 'AWSEBAutoScalingLaunchConfiguration',
                    'Namespace': 'aws:autoscaling:launchconfiguration',
                    'OptionName': 'RootVolumeIOPS'
                },
                {
                    'ResourceName': 'AWSEBAutoScalingLaunchConfiguration',
                    'Namespace': 'aws:autoscaling:launchconfiguration',
                    'OptionName': 'RootVolumeSize'
                },
                {
                    'ResourceName': 'AWSEBAutoScalingLaunchConfiguration',
                    'Namespace': 'aws:autoscaling:launchconfiguration',
                    'OptionName': 'RootVolumeType'
                },
                {
                    'Namespace': 'aws:autoscaling:launchconfiguration',
                    'OptionName': 'SSHSourceRestriction',
                    'Value': 'tcp,22,22,0.0.0.0/0'
                },
                {
                    'ResourceName': 'AWSEBAutoScalingLaunchConfiguration',
                    'Namespace': 'aws:autoscaling:launchconfiguration',
                    'OptionName': 'SecurityGroups',
                    'Value': 'sg-013d807d,sg-48d91238'
                },
                {
                    'ResourceName': 'AWSEBAutoScalingGroup',
                    'Namespace': 'aws:autoscaling:updatepolicy:rollingupdate',
                    'OptionName': 'MaxBatchSize'
                },
                {
                    'ResourceName': 'AWSEBAutoScalingGroup',
                    'Namespace': 'aws:autoscaling:updatepolicy:rollingupdate',
                    'OptionName': 'MinInstancesInService'
                },
                {
                    'ResourceName': 'AWSEBAutoScalingGroup',
                    'Namespace': 'aws:autoscaling:updatepolicy:rollingupdate',
                    'OptionName': 'PauseTime'
                },
                {
                    'ResourceName': 'AWSEBAutoScalingGroup',
                    'Namespace': 'aws:autoscaling:updatepolicy:rollingupdate',
                    'OptionName': 'RollingUpdateEnabled',
                    'Value': 'false'
                },
                {
                    'ResourceName': 'AWSEBAutoScalingGroup',
                    'Namespace': 'aws:autoscaling:updatepolicy:rollingupdate',
                    'OptionName': 'RollingUpdateType',
                    'Value': 'Time'
                },
                {
                    'ResourceName': 'AWSEBAutoScalingGroup',
                    'Namespace': 'aws:autoscaling:updatepolicy:rollingupdate',
                    'OptionName': 'Timeout',
                    'Value': 'PT30M'
                },
                {
                    'Namespace': 'aws:cloudformation:template:parameter',
                    'OptionName': 'AppSource',
                    'Value': 'http://s3-us-west-2.amazonaws.com/elasticbeanstalk-samples-us-west-2/nodejs-sample-v2.zip'
                },
                {
                    'Namespace': 'aws:cloudformation:template:parameter',
                    'OptionName': 'EnvironmentVariables'
                },
                {
                    'Namespace': 'aws:cloudformation:template:parameter',
                    'OptionName': 'HooksPkgUrl',
                    'Value': 'https://s3.dualstack.us-west-2.amazonaws.com/elasticbeanstalk-env-resources-us-west-2/stalks/eb_node_js_4.0.1.200327.0/lib/hooks.tar.gz'
                },
                {
                    'Namespace': 'aws:cloudformation:template:parameter',
                    'OptionName': 'InstancePort',
                    'Value': '80'
                },
                {
                    'Namespace': 'aws:cloudformation:template:parameter',
                    'OptionName': 'InstanceTypeFamily',
                    'Value': 't2'
                },
                {
                    'Namespace': 'aws:cloudformation:template:parameter',
                    'OptionName': 'ServerPort',
                    'Value': '8080'
                },
                {
                    'Namespace': 'aws:cloudformation:template:parameter',
                    'OptionName': 'StaticFiles'
                },
                {
                    'ResourceName': 'AWSEBAutoScalingLaunchConfiguration',
                    'Namespace': 'aws:ec2:vpc',
                    'OptionName': 'AssociatePublicIpAddress',
                    'Value': 'true'
                },
                {
                    'Namespace': 'aws:ec2:vpc',
                    'OptionName': 'ELBScheme',
                    'Value': 'public'
                },
                {
                    'Namespace': 'aws:ec2:vpc',
                    'OptionName': 'ELBSubnets',
                    'Value': 'subnet-90e8a0f7,subnet-2f6f9d74'
                },
                {
                    'ResourceName': 'AWSEBAutoScalingGroup',
                    'Namespace': 'aws:ec2:vpc',
                    'OptionName': 'Subnets',
                    'Value': 'subnet-90e8a0f7,subnet-2f6f9d74'
                },
                {
                    'ResourceName': 'AWSEBSecurityGroup',
                    'Namespace': 'aws:ec2:vpc',
                    'OptionName': 'VPCId',
                    'Value': 'vpc-0b94a86c'
                },
                {
                    'Namespace': 'aws:elasticbeanstalk:application',
                    'OptionName': 'Application Healthcheck URL',
                    'Value': ''
                },
                {
                    'Namespace': 'aws:elasticbeanstalk:application:environment',
                    'OptionName': 'DB_USERNAME',
                    'Value': 'root'
                },
                {
                    'Namespace': 'aws:elasticbeanstalk:cloudwatch:logs',
                    'OptionName': 'DeleteOnTerminate',
                    'Value': 'false'
                },
                {
                    'Namespace': 'aws:elasticbeanstalk:cloudwatch:logs',
                    'OptionName': 'RetentionInDays',
                    'Value': '7'
                },
                {
                    'Namespace': 'aws:elasticbeanstalk:cloudwatch:logs',
                    'OptionName': 'StreamLogs',
                    'Value': 'false'
                },
                {
                    'Namespace': 'aws:elasticbeanstalk:cloudwatch:logs:health',
                    'OptionName': 'DeleteOnTerminate',
                    'Value': 'false'
                },
                {
                    'Namespace': 'aws:elasticbeanstalk:cloudwatch:logs:health',
                    'OptionName': 'HealthStreamingEnabled',
                    'Value': 'false'
                },
                {
                    'Namespace': 'aws:elasticbeanstalk:cloudwatch:logs:health',
                    'OptionName': 'RetentionInDays',
                    'Value': '7'
                },
                {
                    'Namespace': 'aws:elasticbeanstalk:command',
                    'OptionName': 'BatchSize',
                    'Value': '30'
                },
                {
                    'Namespace': 'aws:elasticbeanstalk:command',
                    'OptionName': 'BatchSizeType',
                    'Value': 'Percentage'
                },
                {
                    'Namespace': 'aws:elasticbeanstalk:command',
                    'OptionName': 'IgnoreHealthCheck',
                    'Value': 'false'
                },
                {
                    'Namespace': 'aws:elasticbeanstalk:command',
                    'OptionName': 'Timeout',
                    'Value': '600'
                },
                {
                    'Namespace': 'aws:elasticbeanstalk:container:nodejs',
                    'OptionName': 'GzipCompression',
                    'Value': 'true'
                },
                {
                    'Namespace': 'aws:elasticbeanstalk:container:nodejs',
                    'OptionName': 'NodeCommand'
                },
                {
                    'Namespace': 'aws:elasticbeanstalk:container:nodejs',
                    'OptionName': 'NodeVersion',
                    'Value': '6.14.3'
                },
                {
                    'Namespace': 'aws:elasticbeanstalk:container:nodejs',
                    'OptionName': 'ProxyServer',
                    'Value': 'nginx'
                },
                {
                    'Namespace': 'aws:elasticbeanstalk:control',
                    'OptionName': 'DefaultSSHPort',
                    'Value': '22'
                },
                {
                    'Namespace': 'aws:elasticbeanstalk:control',
                    'OptionName': 'LaunchTimeout',
                    'Value': '0'
                },
                {
                    'Namespace': 'aws:elasticbeanstalk:control',
                    'OptionName': 'LaunchType',
                    'Value': 'Migration'
                },
                {
                    'Namespace': 'aws:elasticbeanstalk:control',
                    'OptionName': 'RollbackLaunchOnFailure',
                    'Value': 'false'
                },
                {
                    'Namespace': 'aws:elasticbeanstalk:environment',
                    'OptionName': 'EnvironmentType',
                    'Value': 'SingleInstance'
                },
                {
                    'Namespace': 'aws:elasticbeanstalk:environment',
                    'OptionName': 'ExternalExtensionsS3Bucket'
                },
                {
                    'Namespace': 'aws:elasticbeanstalk:environment',
                    'OptionName': 'ExternalExtensionsS3Key'
                },
                {
                    'Namespace': 'aws:elasticbeanstalk:environment',
                    'OptionName': 'ServiceRole',
                    'Value': 'aws-elasticbeanstalk-service-role'
                },
                {
                    'Namespace': 'aws:elasticbeanstalk:healthreporting:system',
                    'OptionName': 'ConfigDocument',
                    'Value': '{"Version":1,"CloudWatchMetrics":{"Instance":{"CPUIrq":null,"LoadAverage5min":null,"ApplicationRequests5xx":null,"ApplicationRequests4xx":null,"CPUUser":null,"LoadAverage1min":null,"ApplicationLatencyP50":null,"CPUIdle":null,"InstanceHealth":null,"ApplicationLatencyP95":null,"ApplicationLatencyP85":null,"RootFilesystemUtil":null,"ApplicationLatencyP90":null,"CPUSystem":null,"ApplicationLatencyP75":null,"CPUSoftirq":null,"ApplicationLatencyP10":null,"ApplicationLatencyP99":null,"ApplicationRequestsTotal":null,"ApplicationLatencyP99.9":null,"ApplicationRequests3xx":null,"ApplicationRequests2xx":null,"CPUIowait":null,"CPUNice":null},"Environment":{"InstancesSevere":null,"InstancesDegraded":null,"ApplicationRequests5xx":null,"ApplicationRequests4xx":null,"ApplicationLatencyP50":null,"ApplicationLatencyP95":null,"ApplicationLatencyP85":null,"InstancesUnknown":null,"ApplicationLatencyP90":null,"InstancesInfo":null,"InstancesPending":null,"ApplicationLatencyP75":null,"ApplicationLatencyP10":null,"ApplicationLatencyP99":null,"ApplicationRequestsTotal":null,"InstancesNoData":null,"ApplicationLatencyP99.9":null,"ApplicationRequests3xx":null,"ApplicationRequests2xx":null,"InstancesOk":null,"InstancesWarning":null}}}'
                },
                {
                    'Namespace': 'aws:elasticbeanstalk:healthreporting:system',
                    'OptionName': 'HealthCheckSuccessThreshold',
                    'Value': 'Ok'
                },
                {
                    'Namespace': 'aws:elasticbeanstalk:healthreporting:system',
                    'OptionName': 'SystemType',
                    'Value': 'enhanced'
                },
                {
                    'Namespace': 'aws:elasticbeanstalk:hostmanager',
                    'OptionName': 'LogPublicationControl',
                    'Value': 'false'
                },
                {
                    'Namespace': 'aws:elasticbeanstalk:managedactions',
                    'OptionName': 'ManagedActionsEnabled',
                    'Value': 'false'
                },
                {
                    'Namespace': 'aws:elasticbeanstalk:managedactions',
                    'OptionName': 'PreferredStartTime'
                },
                {
                    'Namespace': 'aws:elasticbeanstalk:managedactions:platformupdate',
                    'OptionName': 'InstanceRefreshEnabled',
                    'Value': 'false'
                },
                {
                    'Namespace': 'aws:elasticbeanstalk:managedactions:platformupdate',
                    'OptionName': 'UpdateLevel'
                },
                {
                    'Namespace': 'aws:elasticbeanstalk:monitoring',
                    'OptionName': 'Automatically Terminate Unhealthy Instances',
                    'Value': 'true'
                },
                {
                    'Namespace': 'aws:elasticbeanstalk:sns:topics',
                    'OptionName': 'Notification Endpoint'
                },
                {
                    'Namespace': 'aws:elasticbeanstalk:sns:topics',
                    'OptionName': 'Notification Protocol',
                    'Value': 'email'
                },
                {
                    'Namespace': 'aws:elasticbeanstalk:sns:topics',
                    'OptionName': 'Notification Topic ARN'
                },
                {
                    'Namespace': 'aws:elasticbeanstalk:sns:topics',
                    'OptionName': 'Notification Topic Name'
                },
                {
                    'Namespace': 'aws:elasticbeanstalk:xray',
                    'OptionName': 'XRayEnabled',
                    'Value': 'false'
                }
            ]
        }
    ]
}


LIST_AVAILABLE_SOLUTION_STACKS = {
    "SolutionStacks": [
        "64bit Amazon Linux 2018.03 v2.8.0 running Tomcat 8 Java 8",
        "64bit Amazon Linux 2018.03 v2.8.0 running Tomcat 7 Java 7",
        "64bit Amazon Linux 2018.03 v2.8.0 running Tomcat 7 Java 6",
        "64bit Amazon Linux 2018.03 v2.8.0 running Go 1.10",
        "64bit Amazon Linux 2017.09 v2.7.6 running Go 1.9",
        "64bit Amazon Linux 2018.03 v2.7.0 running Python 3.6",
        "64bit Amazon Linux 2018.03 v2.7.0 running Python 3.4",
        "64bit Amazon Linux 2018.03 v2.7.1 running Java 8",
        "64bit Amazon Linux 2018.03 v2.7.0 running Python",
        "64bit Amazon Linux 2018.03 v2.7.1 running Java 7",
        "64bit Amazon Linux 2018.03 v2.7.0 running Python 2.7",
        "64bit Amazon Linux 2018.03 v4.5.0 running Node.js",
        "64bit Amazon Linux 2018.03 v2.7.0 running PHP 5.4",
        "64bit Amazon Linux 2018.03 v2.7.0 running PHP 5.5",
        "64bit Amazon Linux 2018.03 v2.7.0 running PHP 5.6",
        "64bit Amazon Linux 2018.03 v2.7.0 running PHP 7.0",
        "64bit Amazon Linux 2018.03 v2.7.0 running PHP 7.1",
        "64bit Amazon Linux 2018.03 v2.8.0 running Ruby 2.5 (Puma)",
        "64bit Amazon Linux 2018.03 v2.8.0 running Ruby 2.4 (Puma)",
        "64bit Amazon Linux 2018.03 v2.8.0 running Ruby 2.3 (Puma)",
        "64bit Amazon Linux 2018.03 v2.8.0 running Ruby 2.2 (Puma)",
        "64bit Amazon Linux 2018.03 v2.8.0 running Ruby 2.1 (Puma)",
        "64bit Amazon Linux 2018.03 v2.8.0 running Ruby 2.0 (Puma)",
        "64bit Amazon Linux 2018.03 v2.8.0 running Ruby 2.5 (Passenger Standalone)",
        "64bit Amazon Linux 2018.03 v2.8.0 running Ruby 2.4 (Passenger Standalone)",
        "64bit Amazon Linux 2018.03 v2.8.0 running Ruby 2.3 (Passenger Standalone)",
        "64bit Amazon Linux 2018.03 v2.8.0 running Ruby 2.2 (Passenger Standalone)",
        "64bit Amazon Linux 2018.03 v2.8.0 running Ruby 2.1 (Passenger Standalone)",
        "64bit Amazon Linux 2018.03 v2.8.0 running Ruby 2.0 (Passenger Standalone)",
        "64bit Amazon Linux 2018.03 v2.8.0 running Ruby 1.9.3",
        "64bit Amazon Linux 2018.03 v2.10.0 running Docker 17.12.1-ce",
        "64bit Amazon Linux 2017.09 v2.8.4 running Docker 17.09.1-ce",
        "64bit Windows Server Core 2016 v1.2.0 running IIS 10.0",
        "64bit Windows Server 2016 v1.2.0 running IIS 10.0",
        "64bit Windows Server Core 2012 R2 v1.2.0 running IIS 8.5",
        "64bit Windows Server 2012 R2 v1.2.0 running IIS 8.5",
        "64bit Windows Server 2012 v1.2.0 running IIS 8",
        "64bit Windows Server 2008 R2 v1.2.0 running IIS 7.5",
        "64bit Windows Server Core 2012 R2 running IIS 8.5",
        "64bit Windows Server 2012 R2 running IIS 8.5",
        "64bit Windows Server 2012 running IIS 8",
        "64bit Windows Server 2008 R2 running IIS 7.5",
        "64bit Amazon Linux 2018.03 v2.5.0 running Packer 1.0.3",
        "64bit Debian jessie v2.10.0 running GlassFish 4.1 Java 8 (Preconfigured - Docker)",
        "64bit Debian jessie v2.10.0 running GlassFish 4.0 Java 7 (Preconfigured - Docker)",
        "64bit Debian jessie v2.10.0 running Go 1.4 (Preconfigured - Docker)",
        "64bit Debian jessie v2.10.0 running Go 1.3 (Preconfigured - Docker)",
        "64bit Debian jessie v2.10.0 running Python 3.4 (Preconfigured - Docker)"
    ]
}


CREATE_STORAGE_LOCATION_RESPONSE = {
    "S3Bucket": "elasticbeanstalk-us-west-2-0123456789012"
}


CREATE_CONFIGURATION_TEMPLATE_RESPONSE = {
    "ApplicationName": "my-application",
    "TemplateName": "my-template",
    "DateCreated": "2015-08-12T18:40:39Z",
    "DateUpdated": "2015-08-12T18:40:39Z",
    "SolutionStackName": "64bit Amazon Linux 2015.03 v2.0.0 running Tomcat 8 Java 8"
}


VALIDATE_CONFIGURATION_SETTINGS_RESPONSE__VALID = {
    "Messages": []
}


VALIDATE_CONFIGURATION_SETTINGS_RESPONSE__INVALID = {
    "Messages": [
        {
            "OptionName": "ConfigDocumet",
            "Message": "Invalid option specification (Namespace: 'aws:elasticbeanstalk:healthreporting:system', OptionName: 'ConfigDocumet'): Unknown configuration setting.",
            "Namespace": "aws:elasticbeanstalk:healthreporting:system",
            "Severity": "error"
        }
    ]
}


DESCRIBE_ENVIRONMENT_HEALTH_RESPONSE = {
    "Status": "Ready",
    "EnvironmentName": "environment-1",
    "Color": "Green",
    "ApplicationMetrics": {
        "Duration": 10,
        "Latency": {
            "P99": 0.004,
            "P75": 0.002,
            "P90": 0.003,
            "P95": 0.004,
            "P85": 0.003,
            "P10": 0.001,
            "P999": 0.004,
            "P50": 0.001
        },
        "RequestCount": 45,
        "StatusCodes": {
            "Status3xx": 0,
            "Status2xx": 45,
            "Status5xx": 0,
            "Status4xx": 0
        }
    },
    "RefreshedAt": "2015-08-20T21:09:18Z",
    "HealthStatus": "Ok",
    "InstancesHealth": {
        "Info": 0,
        "Ok": 1,
        "Unknown": 0,
        "Severe": 0,
        "Warning": 0,
        "Degraded": 0,
        "NoData": 0,
        "Pending": 0
    },
    "Causes": []
}


DESCRIBE_INSTANCES_HEALTH_RESPONSE = {
    "InstanceHealthList": [
        {
            "InstanceId": "i-08691cc7",
            "ApplicationMetrics": {
                "Duration": 10,
                "Latency": {
                    "P99": 0.006,
                    "P75": 0.002,
                    "P90": 0.004,
                    "P95": 0.005,
                    "P85": 0.003,
                    "P10": 0.0,
                    "P999": 0.006,
                    "P50": 0.001
                },
                "RequestCount": 48,
                "StatusCodes": {
                    "Status3xx": 0,
                    "Status2xx": 47,
                    "Status5xx": 0,
                    "Status4xx": 1
                }
            },
            "System": {
                "LoadAverage": [
                    0.0,
                    0.02,
                    0.05
                ],
                "CPUUtilization": {
                    "SoftIRQ": 0.1,
                    "IOWait": 0.2,
                    "System": 0.3,
                    "Idle": 97.8,
                    "User": 1.5,
                    "IRQ": 0.0,
                    "Nice": 0.1
                }
            },
            "Color": "Green",
            "HealthStatus": "Ok",
            "LaunchedAt": "2015-08-13T19:17:09Z",
            "Causes": []
        }
    ],
    "RefreshedAt": "2015-08-20T21:09:08Z"
}


LIST_TAGS_FOR_RESOURCE_RESPONSE = {
    "ResourceArn": 'arn:aws:elasticbeanstalk:us-west-2:123123123123:environment/my-application/environment-1',
    "ResourceTags": [
        {
            "Key": "elasticbeanstalk:environment-name",
            "Value": "environment-1"
        },
        {
            "Key": "elasticbeanstalk:environment-id",
            "Value": "e-cnpdgh26cm"
        },
        {
            "Key": "Name",
            "Value": "environment-1"
        }
    ]
}


DESCRIBE_LOG_STREAMS_RESPONSE = {
    'logStreams': [
        {
            'lastIngestionTime': 1522104918499,
            'firstEventTimestamp': 1522104834000,
            'uploadSequenceToken': '49581045816077287818028642094834630247536380630456711345',
            'arn': 'arn:aws:logs:us-east-1:123123123123:log-group:/aws/elasticbeanstalk/env-name/environment-health.log:log-stream:archive-health-2018-03-26',
            'creationTime': 1522104860498,
            'storedBytes': 0,
            'logStreamName': 'archive-health-2018-03-26',
            'lastEventTimestamp': 1522104864000
        },
        {
            'lastIngestionTime': 1522185082040,
            'firstEventTimestamp': 1522114566000,
            'uploadSequenceToken': '495782746617210878802139966459935713174460150927741245',
            'arn': 'arn:aws:logs:us-east-1:123123123123:log-group:/aws/elasticbeanstalk/env-name/environment-health.log:log-stream:archive-health-2018-03-27',
            'creationTime': 1522114571763,
            'storedBytes': 0,
            'logStreamName': 'archive-health-2018-03-27',
            'lastEventTimestamp': 1522185066000
        },
        {
            'lastIngestionTime': 1522273517592,
            'firstEventTimestamp': 1522214971000,
            'uploadSequenceToken': '4957832466795318902173372629991138882266085318618712345',
            'arn': 'arn:aws:logs:us-east-1:123123123123:log-group:/aws/elasticbeanstalk/env-name/environment-health.log:log-stream:archive-health-2018-03-28',
            'creationTime': 1522215000673,
            'storedBytes': 0,
            'logStreamName': 'archive-health-2018-03-28',
            'lastEventTimestamp': 1522273511000
        },
    ]
}


BATCH_GET_BUILDS = {
    "builds": [
        {
            "id": "Elastic-Beanstalk-my-web-app-app-170706_000919-uUTqM:3362ef1d-584d-48c1-800a-c1c695b71562",
            "arn": "arn:aws:codebuild:us-west-2:123123123123:build/Elastic-Beanstalk-my-web-app-app-170706_000919-uUTqM:3362ef1d-584d-48c1-800a-c1c695b71562",
            "startTime": 1499299760.483,
            "endTime": 1499299762.231,
            "currentPhase": "COMPLETED",
            "buildStatus": "FAILED",
            "projectName": "Elastic-Beanstalk-my-web-app-app-170706_000919-uUTqM",
            "phases": [
                {
                    "phaseType": "SUBMITTED",
                    "phaseStatus": "SUCCEEDED",
                    "startTime": 1499299760.483,
                    "endTime": 1499299761.321,
                    "durationInSeconds": 0
                },
                {
                    "phaseType": "PROVISIONING",
                    "phaseStatus": "CLIENT_ERROR",
                    "startTime": 1499299761.321,
                    "endTime": 1499299762.231,
                    "durationInSeconds": 0,
                    "contexts": [
                        {
                            "statusCode": "ACCESS_DENIED",
                            "message": "Service role arn:aws:iam::123123123123:role/service-role/codebuild-sample_maven_project-service-role does not allow AWS CodeBuild to create Amazon CloudWatch Logs log streams for build arn:aws:codebuild:us-west-2:123123123123:build/Elastic-Beanstalk-my-web-app-app-170706_001032-OYjRZ:a4db9491-91ba-4614-b5e4-3f8d9e994a19"
                        }
                    ]
                },
                {
                    "phaseType": "COMPLETED",
                    "startTime": 1499299762.231
                }
            ],
            "source": {
                "type": "S3",
                "location": "elasticbeanstalk-us-west-2-123123123123/my-web-app/app-170706_000919.zip"
            },
            "artifacts": {
                "location": "arn:aws:s3:::elasticbeanstalk-us-west-2-123123123123/resources/my-web-app/codebuild/codebuild-app-170706_000919.zip"
            },
            "environment": {
                "type": "LINUX_CONTAINER",
                "image": "aws/codebuild/java:openjdk-8",
                "computeType": "BUILD_GENERAL1_SMALL",
                "environmentVariables": [],
                "privilegedMode": False
            },
            "timeoutInMinutes": 60,
            "buildComplete": True,
            "initiator": "some-user"
        },
        {
            "id": "Elastic-Beanstalk-my-web-app-app-170706_001032-OYjRZ:a4db9491-91ba-4614-b5e4-3f8d9e994a19",
            "arn": "arn:aws:codebuild:us-west-2:123123123123:build/Elastic-Beanstalk-my-web-app-app-170706_001032-OYjRZ:a4db9491-91ba-4614-b5e4-3f8d9e994a19",
            "startTime": 1499299833.657,
            "endTime": 1499299835.069,
            "currentPhase": "COMPLETED",
            "buildStatus": "FAILED",
            "projectName": "Elastic-Beanstalk-my-web-app-app-170706_001032-OYjRZ",
            "phases": [
                {
                    "phaseType": "SUBMITTED",
                    "phaseStatus": "SUCCEEDED",
                    "startTime": 1499299833.657,
                    "endTime": 1499299834.0,
                    "durationInSeconds": 0
                },
                {
                    "phaseType": "PROVISIONING",
                    "phaseStatus": "CLIENT_ERROR",
                    "startTime": 1499299834.0,
                    "endTime": 1499299835.069,
                    "durationInSeconds": 1,
                    "contexts": [
                        {
                            "statusCode": "ACCESS_DENIED",
                            "message": "Service role arn:aws:iam::123123123123:role/service-role/codebuild-sample_maven_project-service-role does not allow AWS CodeBuild to create Amazon CloudWatch Logs log streams for build arn:aws:codebuild:us-west-2:123123123123:build/Elastic-Beanstalk-my-web-app-app-170706_001032-OYjRZ:a4db9491-91ba-4614-b5e4-3f8d9e994a19"
                        }
                    ]
                },
                {
                    "phaseType": "COMPLETED",
                    "startTime": 1499299835.069
                }
            ],
            "source": {
                "type": "S3",
                "location": "elasticbeanstalk-us-west-2-123123123123/my-web-app/app-170706_001032.zip"
            },
            "artifacts": {
                "location": "arn:aws:s3:::elasticbeanstalk-us-west-2-123123123123/resources/my-web-app/codebuild/codebuild-app-170706_001032.zip"
            },
            "environment": {
                "type": "LINUX_CONTAINER",
                "image": "aws/codebuild/java:openjdk-8",
                "computeType": "BUILD_GENERAL1_SMALL",
                "environmentVariables": [],
                "privilegedMode": False
            },
            "timeoutInMinutes": 60,
            "buildComplete": True,
            "initiator": "some-user"
        }
    ],
    "buildsNotFound": [
        "bad-batch-id-170706_001032-OYjRZ:a4db9491-91ba-4614-b5e4-3f8d9e994a19"
    ]
}


LIST_CURATED_ENVIRONMENT_IMAGES_RESPONSE = {
    'platforms':
        [
            {
                'languages': [
                    {
                        'images': [
                            {
                                'name': 'aws/codebuild/eb-java-7-amazonlinux-64:2.1.3', 'description': 'AWS ElasticBeanstalk - Java 7 Running on Amazon Linux 64bit v2.1.3'
                            },
                            {
                                'name': 'aws/codebuild/eb-java-8-amazonlinux-64:2.1.3', 'description': 'AWS ElasticBeanstalk - Java 8 Running on Amazon Linux 64bit v2.1.3'
                            },
                            {
                                'name': 'aws/codebuild/eb-java-7-amazonlinux-64:2.1.6', 'description': 'AWS ElasticBeanstalk - Java 7 Running on Amazon Linux 64bit v2.1.6'
                            },
                            {
                                'name': 'aws/codebuild/eb-java-8-amazonlinux-64:2.1.6', 'description': 'AWS ElasticBeanstalk - Java 8 Running on Amazon Linux 64bit v2.1.6'
                            }
                        ],
                        'language': 'Java'
                    },
                    {
                        'images': [
                            {
                                'name': 'aws/codebuild/eb-go-1.5-amazonlinux-64:2.1.3', 'description': 'AWS ElasticBeanstalk - Go 1.5 Running on Amazon Linux 64bit v2.1.3'
                            },
                            {
                                'name': 'aws/codebuild/eb-go-1.5-amazonlinux-64:2.1.6', 'description': 'AWS ElasticBeanstalk - Go 1.5 Running on Amazon Linux 64bit v2.1.6'
                            }
                        ],
                        'language': 'Golang'
                    },
                    {
                        'images': [
                            {
                                'name': 'aws/codebuild/android-java-6:24.4.1', 'description': 'AWS CodeBuild - Android 24.4.1 with java 6'
                            },
                            {
                                'name': 'aws/codebuild/android-java-7:24.4.1', 'description': 'AWS CodeBuild - Android 24.4.1 with java 7'
                            },
                            {
                                'name': 'aws/codebuild/android-java-8:24.4.1', 'description': 'AWS CodeBuild - Android 24.4.1 with java 8'
                            }
                        ],
                        'language': 'Android'
                    }
                ]
            }
        ],
    'ResponseMetadata': {
        'date': 'Tue, 22 Nov 2016 21:36:19 GMT',
        'RetryAttempts': 0, 'HTTPStatusCode': 200,
        'RequestId': 'b47ba2d1-b0fb-11e6-a6a7-6fc6c5a33aee'
    }
}


DESCRIBE_LOG_GROUPS_RESPONSE = {
    "logGroups": [
        {
            "storedBytes": 0,
            "metricFilterCount": 0,
            "creationTime": 1433189500783,
            "logGroupName": "my-logs",
            "retentionInDays": 5,
            "arn": "arn:aws:logs:us-west-2:0123456789012:log-group:my-logs:*"
        }
    ]
}


LIST_OBJECTS_RESPONSE = {
    'ResponseMetadata': {
        'RequestId': '751065621A29D27C',
        'HostId': 'X8PA6BclbDpIJIf41zVeJrexo2ejHDeFAxNvqH3hlxqgKOQX02xHWX0mKM3bijWf70YzWoWJcNw=',
        'HTTPStatusCode': 200,
        'HTTPHeaders': {
            'x-amz-id-2': 'X8PA6BclbDpIJIf41zVeJrexo2ejHDeFAxNvqH3hlxqgKOQX02xHWX0mKM3bijWf70YzWoWJcNw=',
            'x-amz-request-id': '751065621A29D27C',
            'date': 'Tue, 24 Jul 2018 01:15:44 GMT',
            'x-amz-bucket-region': 'us-east-2',
            'content-type': 'application/xml',
            'transfer-encoding': 'chunked',
            'server': 'AmazonS3'
        },
        'RetryAttempts': 0
    },
    'IsTruncated': False,
    'Marker': '',
    'Contents': [
        {
            'Key': '.elasticbeanstalk',
            'LastModified': datetime.datetime(2017, 7, 12, 21, 59, 23, tzinfo=tz.tzutc()),
            'ETag': '"d41d8cd98f00b2042234534asdfasdff8427e"',
            'Size': 0,
            'StorageClass': 'STANDARD',
            'Owner': {
                'ID': '15a1b0d3e1e432234123412341423144d71093667b756f3435c1dcad2247c7124'
            }
        },
        {
            'Key': 'my-application/app-171205_194441.zip',
            'LastModified': datetime.datetime(2017, 12, 5, 19, 44, 42, tzinfo=tz.tzutc()),
            'ETag': '"4ee0f32888afdgsdfg34523552345f8494f7"',
            'Size': 10724,
            'StorageClass': 'STANDARD',
            'Owner': {
                'ID': '15a1b0d3e1e432234123412341423144d71093667b756f3435c1dcad2247c7124'
            }
        }
    ]
}


DELETE_OBJECTS_RESPONSE = {
    'Deleted': [
        {
            'Key': 'key_1',
            'VersionId': 'version_id_1',
            'DeleteMarker': True,
            'DeleteMarkerVersionId': 'marker_1'
        },
        {
            'Key': 'key_2',
            'VersionId': 'version_id_2',
            'DeleteMarker': True,
            'DeleteMarkerVersionId': 'marker_2'
        },
    ],
}


DESCRIBE_TARGET_GROUPS_RESPONSE = {
    "TargetGroups": [
        {
            "TargetGroupArn": "arn:aws:elasticloadbalancing:us-west-2:123123123123:targetgroup/awseb-AWSEB-179V6JWWL9HI5/e57decc4139bfdd2",
            "TargetGroupName": "awseb-AWSEB-179V6JWWL9HI5",
            "Protocol": "TCP",
            "Port": 80,
            "VpcId": "vpc-0b94a86c",
            "HealthCheckProtocol": "TCP",
            "HealthCheckPort": "traffic-port",
            "HealthCheckIntervalSeconds": 10,
            "HealthCheckTimeoutSeconds": 10,
            "HealthyThresholdCount": 5,
            "UnhealthyThresholdCount": 5,
            "LoadBalancerArns": [
                "arn:aws:elasticloadbalancing:us-west-2:123123123123:loadbalancer/net/awseb-AWSEB-1SCRDNB3JJ0K1/01e95fc8160f13cf"
            ],
            "TargetType": "instance"
        }
    ]
}


DESCRIBE_TARGET_HEALTH_RESPONSE = {
    "TargetHealthDescriptions": [
        {
            "Target": {
                "Id": "i-01641763db1c0cb47",
                "Port": 80
            },
            "HealthCheckPort": "80",
            "TargetHealth": {
                "State": "healthy"
            }
        }
    ]
}


DESCRIBE_TARGET_HEALTH_RESPONSE__REGISTRATION_IN_PROGRESS = {
    "TargetHealthDescriptions": [
        {
            "Target": {
                "Id": "i-01641763db1c0cb47",
                "Port": 80
            },
            "HealthCheckPort": "80",
            "TargetHealth": {
                "State": "initial",
                "Reason": "Elb.RegistrationInProgress",
                "Description": "Target registration is in progress"
            }
        }
    ]
}


DESCRIBE_INSTANCE_HEALTH = {
    "InstanceStates": [
        {
            "InstanceId": "i-23452345346456566",
            "ReasonCode": "N/A",
            "State": "InService",
            "Description": "N/A"
        },
        {
            "InstanceId": "i-21312312312312312",
            "ReasonCode": "ELB",
            "State": "OutOfService",
            "Description": "Instance registration is still in progress."
        }
    ]
}



GET_USER_RESPONSE = {
    'User': {
        'Path': '/',
        'UserName': 'someuser',
        'UserId': '123123123123123123123',
        'Arn': 'arn:aws:iam::123123123123:user/someuser',
        'CreateDate': datetime.datetime(2017, 7, 6, 22, 48, 47, tzinfo=tz.tzutc())
    },
    'ResponseMetadata': {
        'RequestId': 'c9cbbd69-ba07-11e8-8950-bfd2975be980',
        'HTTPStatusCode': 200,
        'HTTPHeaders': {
            'x-amzn-requestid': 'c9cbbd69-ba07-11e8-8950-bfd2975be980',
            'content-type': 'text/xml',
            'content-length': '473',
            'date': 'Sun, 16 Sep 2018 23:25:24 GMT'
        },
        'RetryAttempts': 0
    }
}


LIST_TOPICS_RESPONSE = {
    'Topics': [
        {
            'TopicArn': 'arn:aws:sns:us-west-2:123123123123:topic_1'
        },
        {
            'TopicArn': 'arn:aws:sns:us-west-2:123123123123:topic_2'
        },
        {
            'TopicArn': 'arn:aws:sns:us-west-2:123123123123:topic_3'
        }
    ],
    'ResponseMetadata': {
        'RequestId': '0a22bc17-eaa8-56be-847d-e80f0637f7cf',
        'HTTPStatusCode': 200,
        'HTTPHeaders': {
            'x-amzn-requestid': '0a22bc17-eaa8-56be-847d-e80f0637f7cf',
            'content-type': 'text/xml',
            'content-length': '600',
            'date': 'Sun, 16 Sep 2018 23:42:22 GMT'
        },
        'RetryAttempts': 0
    }
}


LIST_KEYS_RESPONSE = {
    'Keys': [
        {
            'KeyId': '12312312-a783-4f6c-8b8f-502a99545967',
            'KeyArn': 'arn:aws:kms:us-west-2:123123123123:key/12312312-a783-4f6c-8b8f-502a99545967'
        },
        {
            'KeyId': '12312312-c7d9-457a-a90d-943be31f6144',
            'KeyArn': 'arn:aws:kms:us-west-2:123123123123:key/12312312-c7d9-457a-a90d-943be31f6144'
        },
        {
            'KeyId': '12312312-ff32-4398-b352-a470ced64752',
            'KeyArn': 'arn:aws:kms:us-west-2:123123123123:key/12312312-ff32-4398-b352-a470ced64752'
        },
        {
            'KeyId': '12312312-36d5-43e6-89ef-c6e82f027d8b',
            'KeyArn': 'arn:aws:kms:us-west-2:123123123123:key/12312312-36d5-43e6-89ef-c6e82f027d8b'
        },
        {
            'KeyId': '12312312-c660-48ee-b5d1-02d6d1ffc275',
            'KeyArn': 'arn:aws:kms:us-west-2:123123123123:key/12312312-c660-48ee-b5d1-02d6d1ffc275'
        },
        {
            'KeyId': '12312312-eec7-49a1-a696-335efc664327',
            'KeyArn': 'arn:aws:kms:us-west-2:123123123123:key/12312312-eec7-49a1-a696-335efc664327'
        },
        {
            'KeyId': '12312312-87b5-4fe3-b69f-57494da80071',
            'KeyArn': 'arn:aws:kms:us-west-2:123123123123:key/12312312-87b5-4fe3-b69f-57494da80071'
        }
    ],
    'Truncated': False,
    'ResponseMetadata': {
        'RequestId': '4fe7eb3b-c547-47fc-a674-d79c652d8289',
        'HTTPStatusCode': 200,
        'HTTPHeaders': {
            'x-amzn-requestid': '4fe7eb3b-c547-47fc-a674-d79c652d8289',
            'content-type': 'application/x-amz-json-1.1',
            'content-length': '993'
        },
        'RetryAttempts': 0
    }
}

LIST_BUCKETS_RESPONSE = {
    'ResponseMetadata': {
        'RequestId': '421450C9254B454A',
        'HostId': 'gEp+QmtD0Vi/72Xl8uT4pAGBe9R7Wc7L97qNbt9H4R6kEKTt8NuXb/DDcRlwTbCMwiBs7mq94x4=',
        'HTTPStatusCode': 200,
        'HTTPHeaders': {
            'x-amz-id-2': 'gEp+QmtD0Vi/72Xl8uT4pAGBe9R7Wc7L97qNbt9H4R6kEKTt8NuXb/DDcRlwTbCMwiBs7mq94x4=',
            'x-amz-request-id': '421450C9254B454A',
            'date': 'Sun, 16 Sep 2018 22:57:25 GMT',
            'content-type': 'application/xml',
            'transfer-encoding': 'chunked',
            'server': 'AmazonS3'
        },
        'RetryAttempts': 0
    },
    'Buckets': [
        {
            'Name': 'cloudtrail-awslogs-123123123123-isengard-do-not-delete',
            'CreationDate': datetime.datetime(2017, 5, 2, 20, 57, 56, tzinfo=tz.tzutc())
        },
        {
            'Name': 'config-bucket-123123123123',
            'CreationDate': datetime.datetime(2018, 1, 28, 4, 21, 34, tzinfo=tz.tzutc())
        },
        {
            'Name': 'do-not-delete-gatedgarden-audit-123123123123',
            'CreationDate': datetime.datetime(2018, 8, 30, 7, 27, 5, tzinfo=tz.tzutc())
        },
        {
            'Name': 'elasticbeanstalk-ap-northeast-1-123123123123',
            'CreationDate': datetime.datetime(2018, 3, 26, 19, 47, 4, tzinfo=tz.tzutc())
        },
        {
            'Name': 'elasticbeanstalk-ap-northeast-2-123123123123',
            'CreationDate': datetime.datetime(2017, 6, 27, 23, 3, 30, tzinfo=tz.tzutc())
        },
        {
            'Name': 'elasticbeanstalk-ap-northeast-3-123123123123',
            'CreationDate': datetime.datetime(2018, 2, 21, 8, 8, 16, tzinfo=tz.tzutc())
        },
        {
            'Name': 'elasticbeanstalk-ap-south-1-123123123123',
            'CreationDate': datetime.datetime(2017, 7, 5, 0, 4, 43, tzinfo=tz.tzutc())
        },
        {
            'Name': 'elasticbeanstalk-ap-southeast-1-123123123123',
            'CreationDate': datetime.datetime(2017, 6, 9, 22, 44, 24, tzinfo=tz.tzutc())
        },
        {
            'Name': 'elasticbeanstalk-ap-southeast-2-123123123123',
            'CreationDate': datetime.datetime(2017, 6, 9, 21, 54, 12, tzinfo=tz.tzutc())
        },
        {
            'Name': 'elasticbeanstalk-ca-central-1-123123123123',
            'CreationDate': datetime.datetime(2017, 12, 18, 19, 42, 23, tzinfo=tz.tzutc())
        },
        {
            'Name': 'elasticbeanstalk-eu-central-1-123123123123',
            'CreationDate': datetime.datetime(2017, 6, 28, 0, 27, 1, tzinfo=tz.tzutc())
        },
        {
            'Name': 'elasticbeanstalk-eu-west-1-123123123123',
            'CreationDate': datetime.datetime(2017, 7, 3, 20, 34, 47, tzinfo=tz.tzutc())
        },
        {
            'Name': 'elasticbeanstalk-eu-west-2-123123123123',
            'CreationDate': datetime.datetime(2017, 6, 27, 22, 54, 41, tzinfo=tz.tzutc())
        },
        {
            'Name': 'elasticbeanstalk-eu-west-3-123123123123',
            'CreationDate': datetime.datetime(2018, 1, 8, 10, 40, 53, tzinfo=tz.tzutc())
        },
        {
            'Name': 'elasticbeanstalk-sa-east-1-123123123123',
            'CreationDate': datetime.datetime(2017, 12, 18, 21, 28, 4, tzinfo=tz.tzutc())
        },
        {
            'Name': 'elasticbeanstalk-us-east-1-123123123123',
            'CreationDate': datetime.datetime(2017, 7, 11, 1, 12, 26, tzinfo=tz.tzutc())
        },
        {
            'Name': 'elasticbeanstalk-us-east-2-123123123123',
            'CreationDate': datetime.datetime(2017, 7, 12, 21, 59, 31, tzinfo=tz.tzutc())
        },
        {
            'Name': 'elasticbeanstalk-us-west-1-123123123123',
            'CreationDate': datetime.datetime(2017, 7, 11, 0, 8, 58, tzinfo=tz.tzutc())
        },
        {
            'Name': 'elasticbeanstalk-us-west-2-123123123123',
            'CreationDate': datetime.datetime(2018, 3, 26, 19, 47, 34, tzinfo=tz.tzutc())
        },
        {
            'Name': 'images-app-bucket',
            'CreationDate': datetime.datetime(2017, 8, 20, 0, 51, 8, tzinfo=tz.tzutc())
        }
    ],
    'Owner': {
        'DisplayName': 'someuser',
        'ID': '12341342134fd2684e6218e27436c04d71093667b756f3435c1dcad2247c7124'
    }
}


DESCRIBE_STACK_EVENTS_RESPONSE = {
    'StackEvents': [
        {
            'StackId': 'arn:aws:cloudformation:us-west-2:123123123123:stack/sam-cfn-stack/5bf79720-9e5d-11e8-99f3-0206b4669a7e',
            'EventId': 'b31b10d0-9e5e-11e8-8eb0-02c3ece5f9fa',
            'StackName': 'sam-cfn-stack',
            'LogicalResourceId': 'sam-cfn-stack',
            'PhysicalResourceId': 'arn:aws:cloudformation:us-west-2:123123123123:stack/sam-cfn-stack/5bf79720-9e5d-11e8-99f3-0206b4669a7e',
            'ResourceType': 'AWS::CloudFormation::Stack',
            'Timestamp': datetime.datetime(2018, 8, 12, 18, 37, 0, 365000, tzinfo=tz.tzutc()),
            'ResourceStatus': 'CREATE_COMPLETE'
        },
        {
            'StackId': 'arn:aws:cloudformation:us-west-2:123123123123:stack/sam-cfn-stack/5bf79720-9e5d-11e8-99f3-0206b4669a7e',
            'EventId': 'HelloWorldFunctionHelloWorldPermissionProd-CREATE_COMPLETE-2018-08-12T18:36:58.371Z',
            'StackName': 'sam-cfn-stack',
            'LogicalResourceId': 'HelloWorldFunctionHelloWorldPermissionProd',
            'PhysicalResourceId': 'sam-cfn-stack-HelloWorldFunctionHelloWorldPermissionProd-W56I7KRNMPOT',
            'ResourceType': 'AWS::Lambda::Permission',
            'Timestamp': datetime.datetime(2018, 8, 12, 18, 36, 58, 371000, tzinfo=tz.tzutc()),
            'ResourceStatus': 'CREATE_COMPLETE',
            'ResourceProperties': '{"FunctionName":"sam-cfn-stack-HelloWorldFunction-1RD6BAM5MKPH5","Action":"lambda:invokeFunction","SourceArn":"arn:aws:execute-api:us-west-2:123123123123:9bpc31p3ij/Prod/GET/hello","Principal":"apigateway.amazonaws.com"}'
        },
        {
            'StackId': 'arn:aws:cloudformation:us-west-2:123123123123:stack/sam-cfn-stack/5bf79720-9e5d-11e8-99f3-0206b4669a7e',
            'EventId': 'HelloWorldFunctionHelloWorldPermissionTest-CREATE_COMPLETE-2018-08-12T18:36:58.294Z',
            'StackName': 'sam-cfn-stack',
            'LogicalResourceId': 'HelloWorldFunctionHelloWorldPermissionTest',
            'PhysicalResourceId': 'sam-cfn-stack-HelloWorldFunctionHelloWorldPermissionTest-2XLHA0LFS2T7',
            'ResourceType': 'AWS::Lambda::Permission',
            'Timestamp': datetime.datetime(2018, 8, 12, 18, 36, 58, 294000, tzinfo=tz.tzutc()),
            'ResourceStatus': 'CREATE_COMPLETE',
            'ResourceProperties': '{"FunctionName":"sam-cfn-stack-HelloWorldFunction-1RD6BAM5MKPH5","Action":"lambda:invokeFunction","SourceArn":"arn:aws:execute-api:us-west-2:123123123123:9bpc31p3ij/*/GET/hello","Principal":"apigateway.amazonaws.com"}'
        },
        {
            'StackId': 'arn:aws:cloudformation:us-west-2:123123123123:stack/sam-cfn-stack/5bf79720-9e5d-11e8-99f3-0206b4669a7e',
            'EventId': 'ServerlessRestApiProdStage-CREATE_COMPLETE-2018-08-12T18:36:52.617Z',
            'StackName': 'sam-cfn-stack',
            'LogicalResourceId': 'ServerlessRestApiProdStage',
            'PhysicalResourceId': 'Prod',
            'ResourceType': 'AWS::ApiGateway::Stage',
            'Timestamp': datetime.datetime(2018, 8, 12, 18, 36, 52, 617000, tzinfo=tz.tzutc()),
            'ResourceStatus': 'CREATE_COMPLETE',
            'ResourceProperties': '{"DeploymentId":"mydbce","StageName":"Prod","RestApiId":"9bpc31p3ij"}'
        },
        {
            'StackId': 'arn:aws:cloudformation:us-west-2:123123123123:stack/sam-cfn-stack/5bf79720-9e5d-11e8-99f3-0206b4669a7e',
            'EventId': 'ServerlessRestApiProdStage-CREATE_IN_PROGRESS-2018-08-12T18:36:51.865Z',
            'StackName': 'sam-cfn-stack',
            'LogicalResourceId': 'ServerlessRestApiProdStage',
            'PhysicalResourceId': 'Prod',
            'ResourceType': 'AWS::ApiGateway::Stage',
            'Timestamp': datetime.datetime(2018, 8, 12, 18, 36, 51, 865000, tzinfo=tz.tzutc()),
            'ResourceStatus': 'CREATE_IN_PROGRESS',
            'ResourceStatusReason': 'Resource creation Initiated',
            'ResourceProperties': '{"DeploymentId":"mydbce","StageName":"Prod","RestApiId":"9bpc31p3ij"}'
        },
        {
            'StackId': 'arn:aws:cloudformation:us-west-2:123123123123:stack/sam-cfn-stack/5bf79720-9e5d-11e8-99f3-0206b4669a7e',
            'EventId': 'ServerlessRestApiProdStage-CREATE_IN_PROGRESS-2018-08-12T18:36:51.037Z',
            'StackName': 'sam-cfn-stack',
            'LogicalResourceId': 'ServerlessRestApiProdStage',
            'PhysicalResourceId': '',
            'ResourceType': 'AWS::ApiGateway::Stage',
            'Timestamp': datetime.datetime(2018, 8, 12, 18, 36, 51, 37000, tzinfo=tz.tzutc()),
            'ResourceStatus': 'CREATE_IN_PROGRESS',
            'ResourceProperties': '{"DeploymentId":"mydbce","StageName":"Prod","RestApiId":"9bpc31p3ij"}'
        },
        {
            'StackId': 'arn:aws:cloudformation:us-west-2:123123123123:stack/sam-cfn-stack/5bf79720-9e5d-11e8-99f3-0206b4669a7e',
            'EventId': 'ServerlessRestApiDeployment47fc2d5f9d-CREATE_COMPLETE-2018-08-12T18:36:49.176Z',
            'StackName': 'sam-cfn-stack',
            'LogicalResourceId': 'ServerlessRestApiDeployment47fc2d5f9d',
            'PhysicalResourceId': 'mydbce',
            'ResourceType': 'AWS::ApiGateway::Deployment',
            'Timestamp': datetime.datetime(2018, 8, 12, 18, 36, 49, 176000, tzinfo=tz.tzutc()),
            'ResourceStatus': 'CREATE_COMPLETE',
            'ResourceProperties': '{"Description":"RestApi deployment id: 47fc2d5f9d21ad56f83937abe2779d0e26d7095e","StageName":"Stage","RestApiId":"9bpc31p3ij"}'
        },
        {
            'StackId': 'arn:aws:cloudformation:us-west-2:123123123123:stack/sam-cfn-stack/5bf79720-9e5d-11e8-99f3-0206b4669a7e',
            'EventId': 'ServerlessRestApiDeployment47fc2d5f9d-CREATE_IN_PROGRESS-2018-08-12T18:36:48.716Z',
            'StackName': 'sam-cfn-stack',
            'LogicalResourceId': 'ServerlessRestApiDeployment47fc2d5f9d',
            'PhysicalResourceId': 'mydbce',
            'ResourceType': 'AWS::ApiGateway::Deployment',
            'Timestamp': datetime.datetime(2018, 8, 12, 18, 36, 48, 716000, tzinfo=tz.tzutc()),
            'ResourceStatus': 'CREATE_IN_PROGRESS',
            'ResourceStatusReason': 'Resource creation Initiated',
            'ResourceProperties': '{"Description":"RestApi deployment id: 47fc2d5f9d21ad56f83937abe2779d0e26d7095e","StageName":"Stage","RestApiId":"9bpc31p3ij"}'
        },
        {
            'StackId': 'arn:aws:cloudformation:us-west-2:123123123123:stack/sam-cfn-stack/5bf79720-9e5d-11e8-99f3-0206b4669a7e',
            'EventId': 'HelloWorldFunctionHelloWorldPermissionProd-CREATE_IN_PROGRESS-2018-08-12T18:36:47.984Z',
            'StackName': 'sam-cfn-stack',
            'LogicalResourceId': 'HelloWorldFunctionHelloWorldPermissionProd',
            'PhysicalResourceId': 'sam-cfn-stack-HelloWorldFunctionHelloWorldPermissionProd-W56I7KRNMPOT',
            'ResourceType': 'AWS::Lambda::Permission',
            'Timestamp': datetime.datetime(2018, 8, 12, 18, 36, 47, 984000, tzinfo=tz.tzutc()),
            'ResourceStatus': 'CREATE_IN_PROGRESS',
            'ResourceStatusReason': 'Resource creation Initiated',
            'ResourceProperties': '{"FunctionName":"sam-cfn-stack-HelloWorldFunction-1RD6BAM5MKPH5","Action":"lambda:invokeFunction","SourceArn":"arn:aws:execute-api:us-west-2:123123123123:9bpc31p3ij/Prod/GET/hello","Principal":"apigateway.amazonaws.com"}'
        },
        {
            'StackId': 'arn:aws:cloudformation:us-west-2:123123123123:stack/sam-cfn-stack/5bf79720-9e5d-11e8-99f3-0206b4669a7e',
            'EventId': 'ServerlessRestApiDeployment47fc2d5f9d-CREATE_IN_PROGRESS-2018-08-12T18:36:47.928Z',
            'StackName': 'sam-cfn-stack',
            'LogicalResourceId': 'ServerlessRestApiDeployment47fc2d5f9d',
            'PhysicalResourceId': '',
            'ResourceType': 'AWS::ApiGateway::Deployment',
            'Timestamp': datetime.datetime(2018, 8, 12, 18, 36, 47, 928000, tzinfo=tz.tzutc()),
            'ResourceStatus': 'CREATE_IN_PROGRESS',
            'ResourceProperties': '{"Description":"RestApi deployment id: 47fc2d5f9d21ad56f83937abe2779d0e26d7095e","StageName":"Stage","RestApiId":"9bpc31p3ij"}'
        },
        {
            'StackId': 'arn:aws:cloudformation:us-west-2:123123123123:stack/sam-cfn-stack/5bf79720-9e5d-11e8-99f3-0206b4669a7e',
            'EventId': 'HelloWorldFunctionHelloWorldPermissionTest-CREATE_IN_PROGRESS-2018-08-12T18:36:47.741Z',
            'StackName': 'sam-cfn-stack',
            'LogicalResourceId': 'HelloWorldFunctionHelloWorldPermissionTest',
            'PhysicalResourceId': 'sam-cfn-stack-HelloWorldFunctionHelloWorldPermissionTest-2XLHA0LFS2T7',
            'ResourceType': 'AWS::Lambda::Permission',
            'Timestamp': datetime.datetime(2018, 8, 12, 18, 36, 47, 741000, tzinfo=tz.tzutc()),
            'ResourceStatus': 'CREATE_IN_PROGRESS',
            'ResourceStatusReason': 'Resource creation Initiated',
            'ResourceProperties': '{"FunctionName":"sam-cfn-stack-HelloWorldFunction-1RD6BAM5MKPH5","Action":"lambda:invokeFunction","SourceArn":"arn:aws:execute-api:us-west-2:123123123123:9bpc31p3ij/*/GET/hello","Principal":"apigateway.amazonaws.com"}'
        },
        {
            'StackId': 'arn:aws:cloudformation:us-west-2:123123123123:stack/sam-cfn-stack/5bf79720-9e5d-11e8-99f3-0206b4669a7e',
            'EventId': 'HelloWorldFunctionHelloWorldPermissionProd-CREATE_IN_PROGRESS-2018-08-12T18:36:47.661Z',
            'StackName': 'sam-cfn-stack',
            'LogicalResourceId': 'HelloWorldFunctionHelloWorldPermissionProd',
            'PhysicalResourceId': '',
            'ResourceType': 'AWS::Lambda::Permission',
            'Timestamp': datetime.datetime(2018, 8, 12, 18, 36, 47, 661000, tzinfo=tz.tzutc()),
            'ResourceStatus': 'CREATE_IN_PROGRESS',
            'ResourceProperties': '{"FunctionName":"sam-cfn-stack-HelloWorldFunction-1RD6BAM5MKPH5","Action":"lambda:invokeFunction","SourceArn":"arn:aws:execute-api:us-west-2:123123123123:9bpc31p3ij/Prod/GET/hello","Principal":"apigateway.amazonaws.com"}'
        },
        {
            'StackId': 'arn:aws:cloudformation:us-west-2:123123123123:stack/sam-cfn-stack/5bf79720-9e5d-11e8-99f3-0206b4669a7e',
            'EventId': 'HelloWorldFunctionHelloWorldPermissionTest-CREATE_IN_PROGRESS-2018-08-12T18:36:47.460Z',
            'StackName': 'sam-cfn-stack',
            'LogicalResourceId': 'HelloWorldFunctionHelloWorldPermissionTest',
            'PhysicalResourceId': '',
            'ResourceType': 'AWS::Lambda::Permission',
            'Timestamp': datetime.datetime(2018, 8, 12, 18, 36, 47, 460000, tzinfo=tz.tzutc()),
            'ResourceStatus': 'CREATE_IN_PROGRESS',
            'ResourceProperties': '{"FunctionName":"sam-cfn-stack-HelloWorldFunction-1RD6BAM5MKPH5","Action":"lambda:invokeFunction","SourceArn":"arn:aws:execute-api:us-west-2:123123123123:9bpc31p3ij/*/GET/hello","Principal":"apigateway.amazonaws.com"}'
        },
        {
            'StackId': 'arn:aws:cloudformation:us-west-2:123123123123:stack/sam-cfn-stack/5bf79720-9e5d-11e8-99f3-0206b4669a7e',
            'EventId': 'ServerlessRestApi-CREATE_COMPLETE-2018-08-12T18:36:45.977Z',
            'StackName': 'sam-cfn-stack',
            'LogicalResourceId': 'ServerlessRestApi',
            'PhysicalResourceId': '9bpc31p3ij',
            'ResourceType': 'AWS::ApiGateway::RestApi',
            'Timestamp': datetime.datetime(2018, 8, 12, 18, 36, 45, 977000, tzinfo=tz.tzutc()),
            'ResourceStatus': 'CREATE_COMPLETE',
            'ResourceProperties': '{"Body":{"paths":{"/hello":{"get":{"responses":{},"x-amazon-apigateway-integration":{"httpMethod":"POST","type":"aws_proxy","uri":"arn:aws:apigateway:us-west-2:lambda:path/2015-03-31/functions/arn:aws:lambda:us-west-2:123123123123:function:sam-cfn-stack-HelloWorldFunction-1RD6BAM5MKPH5/invocations"}}}},"swagger":"2.0","info":{"title":"sam-cfn-stack","version":"1.0"}}}'
        },
        {
            'StackId': 'arn:aws:cloudformation:us-west-2:123123123123:stack/sam-cfn-stack/5bf79720-9e5d-11e8-99f3-0206b4669a7e',
            'EventId': 'ServerlessRestApi-CREATE_IN_PROGRESS-2018-08-12T18:36:45.329Z',
            'StackName': 'sam-cfn-stack',
            'LogicalResourceId': 'ServerlessRestApi',
            'PhysicalResourceId': '9bpc31p3ij',
            'ResourceType': 'AWS::ApiGateway::RestApi',
            'Timestamp': datetime.datetime(2018, 8, 12, 18, 36, 45, 329000, tzinfo=tz.tzutc()),
            'ResourceStatus': 'CREATE_IN_PROGRESS',
            'ResourceStatusReason': 'Resource creation Initiated',
            'ResourceProperties': '{"Body":{"paths":{"/hello":{"get":{"responses":{},"x-amazon-apigateway-integration":{"httpMethod":"POST","type":"aws_proxy","uri":"arn:aws:apigateway:us-west-2:lambda:path/2015-03-31/functions/arn:aws:lambda:us-west-2:123123123123:function:sam-cfn-stack-HelloWorldFunction-1RD6BAM5MKPH5/invocations"}}}},"swagger":"2.0","info":{"title":"sam-cfn-stack","version":"1.0"}}}'
        },
        {
            'StackId': 'arn:aws:cloudformation:us-west-2:123123123123:stack/sam-cfn-stack/5bf79720-9e5d-11e8-99f3-0206b4669a7e',
            'EventId': 'ServerlessRestApi-CREATE_IN_PROGRESS-2018-08-12T18:36:44.771Z',
            'StackName': 'sam-cfn-stack',
            'LogicalResourceId': 'ServerlessRestApi',
            'PhysicalResourceId': '',
            'ResourceType': 'AWS::ApiGateway::RestApi',
            'Timestamp': datetime.datetime(2018, 8, 12, 18, 36, 44, 771000, tzinfo=tz.tzutc()),
            'ResourceStatus': 'CREATE_IN_PROGRESS',
            'ResourceProperties': '{"Body":{"paths":{"/hello":{"get":{"responses":{},"x-amazon-apigateway-integration":{"httpMethod":"POST","type":"aws_proxy","uri":"arn:aws:apigateway:us-west-2:lambda:path/2015-03-31/functions/arn:aws:lambda:us-west-2:123123123123:function:sam-cfn-stack-HelloWorldFunction-1RD6BAM5MKPH5/invocations"}}}},"swagger":"2.0","info":{"title":"sam-cfn-stack","version":"1.0"}}}'
        },
        {
            'StackId': 'arn:aws:cloudformation:us-west-2:123123123123:stack/sam-cfn-stack/5bf79720-9e5d-11e8-99f3-0206b4669a7e',
            'EventId': 'HelloWorldFunction-CREATE_COMPLETE-2018-08-12T18:36:42.962Z',
            'StackName': 'sam-cfn-stack',
            'LogicalResourceId': 'HelloWorldFunction',
            'PhysicalResourceId': 'sam-cfn-stack-HelloWorldFunction-1RD6BAM5MKPH5',
            'ResourceType': 'AWS::Lambda::Function',
            'Timestamp': datetime.datetime(2018, 8, 12, 18, 36, 42, 962000, tzinfo=tz.tzutc()),
            'ResourceStatus': 'CREATE_COMPLETE',
            'ResourceProperties': '{"Role":"arn:aws:iam::123123123123:role/sam-cfn-stack-HelloWorldFunctionRole-A8CQME7PUBXU","Runtime":"nodejs8.10","Timeout":"3","Environment":{"Variables":{"PARAM1":"VALUE"}},"Handler":"app.lambda_handler","Code":{"S3Bucket":"elasticbeanstalk-us-west-2-123123123123","S3Key":"20f0cf89dc7c0f65c6140381a82feb19"},"Tags":[{"Value":"SAM","Key":"lambda:createdBy"}]}'
        },
        {
            'StackId': 'arn:aws:cloudformation:us-west-2:123123123123:stack/sam-cfn-stack/5bf79720-9e5d-11e8-99f3-0206b4669a7e',
            'EventId': 'HelloWorldFunction-CREATE_IN_PROGRESS-2018-08-12T18:36:42.183Z',
            'StackName': 'sam-cfn-stack',
            'LogicalResourceId': 'HelloWorldFunction',
            'PhysicalResourceId': 'sam-cfn-stack-HelloWorldFunction-1RD6BAM5MKPH5',
            'ResourceType': 'AWS::Lambda::Function',
            'Timestamp': datetime.datetime(2018, 8, 12, 18, 36, 42, 183000, tzinfo=tz.tzutc()),
            'ResourceStatus': 'CREATE_IN_PROGRESS',
            'ResourceStatusReason': 'Resource creation Initiated',
            'ResourceProperties': '{"Role":"arn:aws:iam::123123123123:role/sam-cfn-stack-HelloWorldFunctionRole-A8CQME7PUBXU","Runtime":"nodejs8.10","Timeout":"3","Environment":{"Variables":{"PARAM1":"VALUE"}},"Handler":"app.lambda_handler","Code":{"S3Bucket":"elasticbeanstalk-us-west-2-123123123123","S3Key":"20f0cf89dc7c0f65c6140381a82feb19"},"Tags":[{"Value":"SAM","Key":"lambda:createdBy"}]}'
        },
        {
            'StackId': 'arn:aws:cloudformation:us-west-2:123123123123:stack/sam-cfn-stack/5bf79720-9e5d-11e8-99f3-0206b4669a7e',
            'EventId': 'HelloWorldFunction-CREATE_IN_PROGRESS-2018-08-12T18:36:41.227Z',
            'StackName': 'sam-cfn-stack',
            'LogicalResourceId': 'HelloWorldFunction',
            'PhysicalResourceId': '',
            'ResourceType': 'AWS::Lambda::Function',
            'Timestamp': datetime.datetime(2018, 8, 12, 18, 36, 41, 227000, tzinfo=tz.tzutc()),
            'ResourceStatus': 'CREATE_IN_PROGRESS',
            'ResourceProperties': '{"Role":"arn:aws:iam::123123123123:role/sam-cfn-stack-HelloWorldFunctionRole-A8CQME7PUBXU","Runtime":"nodejs8.10","Timeout":"3","Environment":{"Variables":{"PARAM1":"VALUE"}},"Handler":"app.lambda_handler","Code":{"S3Bucket":"elasticbeanstalk-us-west-2-123123123123","S3Key":"20f0cf89dc7c0f65c6140381a82feb19"},"Tags":[{"Value":"SAM","Key":"lambda:createdBy"}]}'
        },
        {
            'StackId': 'arn:aws:cloudformation:us-west-2:123123123123:stack/sam-cfn-stack/5bf79720-9e5d-11e8-99f3-0206b4669a7e',
            'EventId': 'HelloWorldFunctionRole-CREATE_COMPLETE-2018-08-12T18:36:38.990Z',
            'StackName': 'sam-cfn-stack',
            'LogicalResourceId': 'HelloWorldFunctionRole',
            'PhysicalResourceId': 'sam-cfn-stack-HelloWorldFunctionRole-A8CQME7PUBXU',
            'ResourceType': 'AWS::IAM::Role',
            'Timestamp': datetime.datetime(2018, 8, 12, 18, 36, 38, 990000, tzinfo=tz.tzutc()),
            'ResourceStatus': 'CREATE_COMPLETE',
            'ResourceProperties': '{"ManagedPolicyArns":["arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"],"AssumeRolePolicyDocument":{"Version":"2012-10-17","Statement":[{"Action":["sts:AssumeRole"],"Effect":"Allow","Principal":{"Service":["lambda.amazonaws.com"]}}]}}'
        },
        {
            'StackId': 'arn:aws:cloudformation:us-west-2:123123123123:stack/sam-cfn-stack/5bf79720-9e5d-11e8-99f3-0206b4669a7e',
            'EventId': 'HelloWorldFunctionRole-CREATE_IN_PROGRESS-2018-08-12T18:36:24.677Z',
            'StackName': 'sam-cfn-stack',
            'LogicalResourceId': 'HelloWorldFunctionRole',
            'PhysicalResourceId': 'sam-cfn-stack-HelloWorldFunctionRole-A8CQME7PUBXU',
            'ResourceType': 'AWS::IAM::Role',
            'Timestamp': datetime.datetime(2018, 8, 12, 18, 36, 24, 677000, tzinfo=tz.tzutc()),
            'ResourceStatus': 'CREATE_IN_PROGRESS',
            'ResourceStatusReason': 'Resource creation Initiated',
            'ResourceProperties': '{"ManagedPolicyArns":["arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"],"AssumeRolePolicyDocument":{"Version":"2012-10-17","Statement":[{"Action":["sts:AssumeRole"],"Effect":"Allow","Principal":{"Service":["lambda.amazonaws.com"]}}]}}'
        },
        {
            'StackId': 'arn:aws:cloudformation:us-west-2:123123123123:stack/sam-cfn-stack/5bf79720-9e5d-11e8-99f3-0206b4669a7e',
            'EventId': 'HelloWorldFunctionRole-CREATE_IN_PROGRESS-2018-08-12T18:36:24.311Z',
            'StackName': 'sam-cfn-stack',
            'LogicalResourceId': 'HelloWorldFunctionRole',
            'PhysicalResourceId': '',
            'ResourceType': 'AWS::IAM::Role',
            'Timestamp': datetime.datetime(2018, 8, 12, 18, 36, 24, 311000, tzinfo=tz.tzutc()),
            'ResourceStatus': 'CREATE_IN_PROGRESS',
            'ResourceProperties': '{"ManagedPolicyArns":["arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"],"AssumeRolePolicyDocument":{"Version":"2012-10-17","Statement":[{"Action":["sts:AssumeRole"],"Effect":"Allow","Principal":{"Service":["lambda.amazonaws.com"]}}]}}'
        },
        {
            'StackId': 'arn:aws:cloudformation:us-west-2:123123123123:stack/sam-cfn-stack/5bf79720-9e5d-11e8-99f3-0206b4669a7e',
            'EventId': '9c5d1320-9e5e-11e8-afcd-50a68d01a68d',
            'StackName': 'sam-cfn-stack',
            'LogicalResourceId': 'sam-cfn-stack',
            'PhysicalResourceId': 'arn:aws:cloudformation:us-west-2:123123123123:stack/sam-cfn-stack/5bf79720-9e5d-11e8-99f3-0206b4669a7e',
            'ResourceType': 'AWS::CloudFormation::Stack',
            'Timestamp': datetime.datetime(2018, 8, 12, 18, 36, 22, 220000, tzinfo=tz.tzutc()),
            'ResourceStatus': 'CREATE_IN_PROGRESS',
            'ResourceStatusReason': 'User Initiated'
        },
        {
            'StackId': 'arn:aws:cloudformation:us-west-2:123123123123:stack/sam-cfn-stack/5bf79720-9e5d-11e8-99f3-0206b4669a7e',
            'EventId': '5bf721f0-9e5d-11e8-99f3-0206b4669a7e',
            'StackName': 'sam-cfn-stack',
            'LogicalResourceId': 'sam-cfn-stack',
            'PhysicalResourceId': 'arn:aws:cloudformation:us-west-2:123123123123:stack/sam-cfn-stack/5bf79720-9e5d-11e8-99f3-0206b4669a7e',
            'ResourceType': 'AWS::CloudFormation::Stack',
            'Timestamp': datetime.datetime(2018, 8, 12, 18, 27, 24, 711000, tzinfo=tz.tzutc()),
            'ResourceStatus': 'REVIEW_IN_PROGRESS',
            'ResourceStatusReason': 'User Initiated'
        }
    ],
    'ResponseMetadata': {
        'RequestId': '5754212c-bab8-11e8-88df-cdf3c9f5e602',
        'HTTPStatusCode': 200,
        'HTTPHeaders': {
            'x-amzn-requestid': '5754212c-bab8-11e8-88df-cdf3c9f5e602',
            'content-type': 'text/xml',
            'content-length': '49435',
            'vary': 'Accept-Encoding',
            'date': 'Mon, 17 Sep 2018 20:29:13 GMT'
        },
        'RetryAttempts': 0
    }
}


DESCRIBE_STACK_EVENTS_RESPONSE__CREATE_FAILED = {
    'StackEvents': [
        {
            'StackId': 'arn:aws:cloudformation:us-west-2:123123123123:stack/my-cfn-stack/5f60bc20-b91f-11e8-bed7-027277c482a4',
            'EventId': 'f3ea0660-b921-11e8-a287-02493f0d1b56',
            'StackName': 'my-cfn-stack',
            'LogicalResourceId': 'my-cfn-stack',
            'PhysicalResourceId': 'arn:aws:cloudformation:us-west-2:123123123123:stack/my-cfn-stack/5f60bc20-b91f-11e8-bed7-027277c482a4',
            'ResourceType': 'AWS::CloudFormation::Stack',
            'Timestamp': datetime.datetime(2018, 9, 15, 20, 0, 11, 189000, tzinfo=tz.tzutc()),
            'ResourceStatus': 'CREATE_FAILED',
            'ResourceStatusReason': 'The following resource(s) failed to create: [AWSEBInstanceLaunchWaitCondition]. '
        },
        {
            'StackId': 'arn:aws:cloudformation:us-west-2:123123123123:stack/my-cfn-stack/5f60bc20-b91f-11e8-bed7-027277c482a4',
            'EventId': 'AWSEBInstanceLaunchWaitCondition-CREATE_FAILED-2018-09-15T20:00:10.397Z',
            'StackName': 'my-cfn-stack',
            'LogicalResourceId': 'AWSEBInstanceLaunchWaitCondition',
            'PhysicalResourceId': 'arn:aws:cloudformation:us-west-2:123123123123:stack/my-cfn-stack/5f60bc20-b91f-11e8-bed7-027277c482a4/AWSEBInstanceLaunchWaitHandle',
            'ResourceType': 'AWS::CloudFormation::WaitCondition',
            'Timestamp': datetime.datetime(2018, 9, 15, 20, 0, 10, 397000, tzinfo=tz.tzutc()),
            'ResourceStatus': 'CREATE_FAILED',
            'ResourceStatusReason': 'WaitCondition timed out. Received 0 conditions when expecting 1',
            'ResourceProperties': '{"Timeout":"900","Count":"1","Handle":"https://cloudformation-waitcondition-us-west-2.s3-us-west-2.amazonaws.com/arn%3Aaws%3Acloudformation%3Aus-west-2%3A123123123123%3Astack/my-cfn-stack/5f60bc20-b91f-11e8-bed7-027277c482a4/AWSEBInstanceLaunchWaitHandle?AWSAccessKeyId=AKIAI5ZDPCT4PV2AKKAA&Expires=1537126906&Signature=ZMzoAUTwL5OU2ImILgqCmBXwsvo%3D"}'
        },
        {
            'StackId': 'arn:aws:cloudformation:us-west-2:123123123123:stack/my-cfn-stack/5f60bc20-b91f-11e8-bed7-027277c482a4',
            'EventId': 'AWSEBV2LoadBalancerListener-CREATE_COMPLETE-2018-09-15T19:44:05.532Z',
            'StackName': 'my-cfn-stack',
            'LogicalResourceId': 'AWSEBV2LoadBalancerListener',
            'PhysicalResourceId': 'arn:aws:elasticloadbalancing:us-west-2:123123123123:listener/app/awseb-AWSEB-1VGXTCA62TZW5/f58275dd12edce24/442e932df2317ed3',
            'ResourceType': 'AWS::ElasticLoadBalancingV2::Listener',
            'Timestamp': datetime.datetime(2018, 9, 15, 19, 44, 5, 532000, tzinfo=tz.tzutc()),
            'ResourceStatus': 'CREATE_COMPLETE',
            'ResourceProperties': '{"LoadBalancerArn":"arn:aws:elasticloadbalancing:us-west-2:123123123123:loadbalancer/app/awseb-AWSEB-1VGXTCA62TZW5/f58275dd12edce24","DefaultActions":[{"TargetGroupArn":"arn:aws:elasticloadbalancing:us-west-2:123123123123:targetgroup/awseb-AWSEB-17R8PVLEWQWEC/234d7a174f1aa491","Type":"forward"}],"Port":"80","Protocol":"HTTP"}'
        },
        {
            'StackId': 'arn:aws:cloudformation:us-west-2:123123123123:stack/my-cfn-stack/5f60bc20-b91f-11e8-bed7-027277c482a4',
            'EventId': 'AWSEBV2LoadBalancerListener-CREATE_IN_PROGRESS-2018-09-15T19:44:05.215Z',
            'StackName': 'my-cfn-stack',
            'LogicalResourceId': 'AWSEBV2LoadBalancerListener',
            'PhysicalResourceId': 'arn:aws:elasticloadbalancing:us-west-2:123123123123:listener/app/awseb-AWSEB-1VGXTCA62TZW5/f58275dd12edce24/442e932df2317ed3',
            'ResourceType': 'AWS::ElasticLoadBalancingV2::Listener',
            'Timestamp': datetime.datetime(2018, 9, 15, 19, 44, 5, 215000, tzinfo=tz.tzutc()),
            'ResourceStatus': 'CREATE_IN_PROGRESS',
            'ResourceStatusReason': 'Resource creation Initiated',
            'ResourceProperties': '{"LoadBalancerArn":"arn:aws:elasticloadbalancing:us-west-2:123123123123:loadbalancer/app/awseb-AWSEB-1VGXTCA62TZW5/f58275dd12edce24","DefaultActions":[{"TargetGroupArn":"arn:aws:elasticloadbalancing:us-west-2:123123123123:targetgroup/awseb-AWSEB-17R8PVLEWQWEC/234d7a174f1aa491","Type":"forward"}],"Port":"80","Protocol":"HTTP"}'
        },
        {
            'StackId': 'arn:aws:cloudformation:us-west-2:123123123123:stack/my-cfn-stack/5f60bc20-b91f-11e8-bed7-027277c482a4',
            'EventId': 'AWSEBV2LoadBalancerListener-CREATE_IN_PROGRESS-2018-09-15T19:44:04.860Z',
            'StackName': 'my-cfn-stack',
            'LogicalResourceId': 'AWSEBV2LoadBalancerListener',
            'PhysicalResourceId': '',
            'ResourceType': 'AWS::ElasticLoadBalancingV2::Listener',
            'Timestamp': datetime.datetime(2018, 9, 15, 19, 44, 4, 860000, tzinfo=tz.tzutc()),
            'ResourceStatus': 'CREATE_IN_PROGRESS',
            'ResourceProperties': '{"LoadBalancerArn":"arn:aws:elasticloadbalancing:us-west-2:123123123123:loadbalancer/app/awseb-AWSEB-1VGXTCA62TZW5/f58275dd12edce24","DefaultActions":[{"TargetGroupArn":"arn:aws:elasticloadbalancing:us-west-2:123123123123:targetgroup/awseb-AWSEB-17R8PVLEWQWEC/234d7a174f1aa491","Type":"forward"}],"Port":"80","Protocol":"HTTP"}'
        },
        {
            'StackId': 'arn:aws:cloudformation:us-west-2:123123123123:stack/my-cfn-stack/5f60bc20-b91f-11e8-bed7-027277c482a4',
            'EventId': 'AWSEBV2LoadBalancer-CREATE_COMPLETE-2018-09-15T19:44:00.197Z',
            'StackName': 'my-cfn-stack',
            'LogicalResourceId': 'AWSEBV2LoadBalancer',
            'PhysicalResourceId': 'arn:aws:elasticloadbalancing:us-west-2:123123123123:loadbalancer/app/awseb-AWSEB-1VGXTCA62TZW5/f58275dd12edce24',
            'ResourceType': 'AWS::ElasticLoadBalancingV2::LoadBalancer',
            'Timestamp': datetime.datetime(2018, 9, 15, 19, 44, 0, 197000, tzinfo=tz.tzutc()),
            'ResourceStatus': 'CREATE_COMPLETE',
            'ResourceProperties': '{"SecurityGroups":["sg-088da58b23bc89ea2"],"Subnets":["subnet-0556027c","subnet-005248b6cc2dfa908"]}'
        },
        {
            'StackId': 'arn:aws:cloudformation:us-west-2:123123123123:stack/my-cfn-stack/5f60bc20-b91f-11e8-bed7-027277c482a4',
            'EventId': 'AWSEBCloudwatchAlarmLow-CREATE_COMPLETE-2018-09-15T19:43:15.732Z',
            'StackName': 'my-cfn-stack',
            'LogicalResourceId': 'AWSEBCloudwatchAlarmLow',
            'PhysicalResourceId': 'my-cfn-stack-AWSEBCloudwatchAlarmLow-1MFS7DYBPD2UZ',
            'ResourceType': 'AWS::CloudWatch::Alarm',
            'Timestamp': datetime.datetime(2018, 9, 15, 19, 43, 15, 732000, tzinfo=tz.tzutc()),
            'ResourceStatus': 'CREATE_COMPLETE',
            'ResourceProperties': '{"AlarmActions":["arn:aws:autoscaling:us-west-2:123123123123:scalingPolicy:b2818a6b-eb82-46bf-8e2c-d356dd461be3:autoScalingGroupName/my-cfn-stack-AWSEBAutoScalingGroup-UP1RZPYEFMGW:policyName/my-cfn-stack-AWSEBAutoScalingScaleDownPolicy-14H4PCTKAXIJ1"],"MetricName":"NetworkOut","ComparisonOperator":"LessThanThreshold","Statistic":"Average","AlarmDescription":"ElasticBeanstalk Default Scale Down alarm","Period":"300","Dimensions":[{"Value":"my-cfn-stack-AWSEBAutoScalingGroup-UP1RZPYEFMGW","Name":"AutoScalingGroupName"}],"EvaluationPeriods":"1","Namespace":"AWS/EC2","Threshold":"2000000"}'
        },
        {
            'StackId': 'arn:aws:cloudformation:us-west-2:123123123123:stack/my-cfn-stack/5f60bc20-b91f-11e8-bed7-027277c482a4',
            'EventId': 'AWSEBCloudwatchAlarmLow-CREATE_IN_PROGRESS-2018-09-15T19:43:15.600Z',
            'StackName': 'my-cfn-stack',
            'LogicalResourceId': 'AWSEBCloudwatchAlarmLow',
            'PhysicalResourceId': 'my-cfn-stack-AWSEBCloudwatchAlarmLow-1MFS7DYBPD2UZ',
            'ResourceType': 'AWS::CloudWatch::Alarm',
            'Timestamp': datetime.datetime(2018, 9, 15, 19, 43, 15, 600000, tzinfo=tz.tzutc()),
            'ResourceStatus': 'CREATE_IN_PROGRESS',
            'ResourceStatusReason': 'Resource creation Initiated',
            'ResourceProperties': '{"AlarmActions":["arn:aws:autoscaling:us-west-2:123123123123:scalingPolicy:b2818a6b-eb82-46bf-8e2c-d356dd461be3:autoScalingGroupName/my-cfn-stack-AWSEBAutoScalingGroup-UP1RZPYEFMGW:policyName/my-cfn-stack-AWSEBAutoScalingScaleDownPolicy-14H4PCTKAXIJ1"],"MetricName":"NetworkOut","ComparisonOperator":"LessThanThreshold","Statistic":"Average","AlarmDescription":"ElasticBeanstalk Default Scale Down alarm","Period":"300","Dimensions":[{"Value":"my-cfn-stack-AWSEBAutoScalingGroup-UP1RZPYEFMGW","Name":"AutoScalingGroupName"}],"EvaluationPeriods":"1","Namespace":"AWS/EC2","Threshold":"2000000"}'
        },
        {
            'StackId': 'arn:aws:cloudformation:us-west-2:123123123123:stack/my-cfn-stack/5f60bc20-b91f-11e8-bed7-027277c482a4',
            'EventId': 'AWSEBCloudwatchAlarmHigh-CREATE_COMPLETE-2018-09-15T19:43:15.499Z',
            'StackName': 'my-cfn-stack',
            'LogicalResourceId': 'AWSEBCloudwatchAlarmHigh',
            'PhysicalResourceId': 'my-cfn-stack-AWSEBCloudwatchAlarmHigh-N26UEPD6N8M3',
            'ResourceType': 'AWS::CloudWatch::Alarm',
            'Timestamp': datetime.datetime(2018, 9, 15, 19, 43, 15, 499000, tzinfo=tz.tzutc()),
            'ResourceStatus': 'CREATE_COMPLETE',
            'ResourceProperties': '{"AlarmActions":["arn:aws:autoscaling:us-west-2:123123123123:scalingPolicy:65acc44b-d34a-4956-ba61-cfee4f9242be:autoScalingGroupName/my-cfn-stack-AWSEBAutoScalingGroup-UP1RZPYEFMGW:policyName/my-cfn-stack-AWSEBAutoScalingScaleUpPolicy-96KTMSIQJPF0"],"MetricName":"NetworkOut","ComparisonOperator":"GreaterThanThreshold","Statistic":"Average","AlarmDescription":"ElasticBeanstalk Default Scale Up alarm","Period":"300","Dimensions":[{"Value":"my-cfn-stack-AWSEBAutoScalingGroup-UP1RZPYEFMGW","Name":"AutoScalingGroupName"}],"EvaluationPeriods":"1","Namespace":"AWS/EC2","Threshold":"6000000"}'
        },
        {
            'StackId': 'arn:aws:cloudformation:us-west-2:123123123123:stack/my-cfn-stack/5f60bc20-b91f-11e8-bed7-027277c482a4',
            'EventId': 'AWSEBCloudwatchAlarmHigh-CREATE_IN_PROGRESS-2018-09-15T19:43:15.363Z',
            'StackName': 'my-cfn-stack',
            'LogicalResourceId': 'AWSEBCloudwatchAlarmHigh',
            'PhysicalResourceId': 'my-cfn-stack-AWSEBCloudwatchAlarmHigh-N26UEPD6N8M3',
            'ResourceType': 'AWS::CloudWatch::Alarm',
            'Timestamp': datetime.datetime(2018, 9, 15, 19, 43, 15, 363000, tzinfo=tz.tzutc()),
            'ResourceStatus': 'CREATE_IN_PROGRESS',
            'ResourceStatusReason': 'Resource creation Initiated',
            'ResourceProperties': '{"AlarmActions":["arn:aws:autoscaling:us-west-2:123123123123:scalingPolicy:65acc44b-d34a-4956-ba61-cfee4f9242be:autoScalingGroupName/my-cfn-stack-AWSEBAutoScalingGroup-UP1RZPYEFMGW:policyName/my-cfn-stack-AWSEBAutoScalingScaleUpPolicy-96KTMSIQJPF0"],"MetricName":"NetworkOut","ComparisonOperator":"GreaterThanThreshold","Statistic":"Average","AlarmDescription":"ElasticBeanstalk Default Scale Up alarm","Period":"300","Dimensions":[{"Value":"my-cfn-stack-AWSEBAutoScalingGroup-UP1RZPYEFMGW","Name":"AutoScalingGroupName"}],"EvaluationPeriods":"1","Namespace":"AWS/EC2","Threshold":"6000000"}'
        },
        {
            'StackId': 'arn:aws:cloudformation:us-west-2:123123123123:stack/my-cfn-stack/5f60bc20-b91f-11e8-bed7-027277c482a4',
            'EventId': 'AWSEBCloudwatchAlarmLow-CREATE_IN_PROGRESS-2018-09-15T19:43:15.191Z',
            'StackName': 'my-cfn-stack',
            'LogicalResourceId': 'AWSEBCloudwatchAlarmLow',
            'PhysicalResourceId': '',
            'ResourceType': 'AWS::CloudWatch::Alarm',
            'Timestamp': datetime.datetime(2018, 9, 15, 19, 43, 15, 191000, tzinfo=tz.tzutc()),
            'ResourceStatus': 'CREATE_IN_PROGRESS',
            'ResourceProperties': '{"AlarmActions":["arn:aws:autoscaling:us-west-2:123123123123:scalingPolicy:b2818a6b-eb82-46bf-8e2c-d356dd461be3:autoScalingGroupName/my-cfn-stack-AWSEBAutoScalingGroup-UP1RZPYEFMGW:policyName/my-cfn-stack-AWSEBAutoScalingScaleDownPolicy-14H4PCTKAXIJ1"],"MetricName":"NetworkOut","ComparisonOperator":"LessThanThreshold","Statistic":"Average","AlarmDescription":"ElasticBeanstalk Default Scale Down alarm","Period":"300","Dimensions":[{"Value":"my-cfn-stack-AWSEBAutoScalingGroup-UP1RZPYEFMGW","Name":"AutoScalingGroupName"}],"EvaluationPeriods":"1","Namespace":"AWS/EC2","Threshold":"2000000"}'
        },
        {
            'StackId': 'arn:aws:cloudformation:us-west-2:123123123123:stack/my-cfn-stack/5f60bc20-b91f-11e8-bed7-027277c482a4',
            'EventId': 'AWSEBCloudwatchAlarmHigh-CREATE_IN_PROGRESS-2018-09-15T19:43:14.989Z',
            'StackName': 'my-cfn-stack',
            'LogicalResourceId': 'AWSEBCloudwatchAlarmHigh',
            'PhysicalResourceId': '',
            'ResourceType': 'AWS::CloudWatch::Alarm',
            'Timestamp': datetime.datetime(2018, 9, 15, 19, 43, 14, 989000, tzinfo=tz.tzutc()),
            'ResourceStatus': 'CREATE_IN_PROGRESS',
            'ResourceProperties': '{"AlarmActions":["arn:aws:autoscaling:us-west-2:123123123123:scalingPolicy:65acc44b-d34a-4956-ba61-cfee4f9242be:autoScalingGroupName/my-cfn-stack-AWSEBAutoScalingGroup-UP1RZPYEFMGW:policyName/my-cfn-stack-AWSEBAutoScalingScaleUpPolicy-96KTMSIQJPF0"],"MetricName":"NetworkOut","ComparisonOperator":"GreaterThanThreshold","Statistic":"Average","AlarmDescription":"ElasticBeanstalk Default Scale Up alarm","Period":"300","Dimensions":[{"Value":"my-cfn-stack-AWSEBAutoScalingGroup-UP1RZPYEFMGW","Name":"AutoScalingGroupName"}],"EvaluationPeriods":"1","Namespace":"AWS/EC2","Threshold":"6000000"}'
        },
        {
            'StackId': 'arn:aws:cloudformation:us-west-2:123123123123:stack/my-cfn-stack/5f60bc20-b91f-11e8-bed7-027277c482a4',
            'EventId': 'AWSEBAutoScalingScaleUpPolicy-CREATE_COMPLETE-2018-09-15T19:43:11.782Z',
            'StackName': 'my-cfn-stack',
            'LogicalResourceId': 'AWSEBAutoScalingScaleUpPolicy',
            'PhysicalResourceId': 'arn:aws:autoscaling:us-west-2:123123123123:scalingPolicy:65acc44b-d34a-4956-ba61-cfee4f9242be:autoScalingGroupName/my-cfn-stack-AWSEBAutoScalingGroup-UP1RZPYEFMGW:policyName/my-cfn-stack-AWSEBAutoScalingScaleUpPolicy-96KTMSIQJPF0',
            'ResourceType': 'AWS::AutoScaling::ScalingPolicy',
            'Timestamp': datetime.datetime(2018, 9, 15, 19, 43, 11, 782000, tzinfo=tz.tzutc()),
            'ResourceStatus': 'CREATE_COMPLETE',
            'ResourceProperties': '{"ScalingAdjustment":"1","AutoScalingGroupName":"my-cfn-stack-AWSEBAutoScalingGroup-UP1RZPYEFMGW","AdjustmentType":"ChangeInCapacity"}'
        },
        {
            'StackId': 'arn:aws:cloudformation:us-west-2:123123123123:stack/my-cfn-stack/5f60bc20-b91f-11e8-bed7-027277c482a4',
            'EventId': 'AWSEBAutoScalingScaleUpPolicy-CREATE_IN_PROGRESS-2018-09-15T19:43:11.633Z',
            'StackName': 'my-cfn-stack',
            'LogicalResourceId': 'AWSEBAutoScalingScaleUpPolicy',
            'PhysicalResourceId': 'arn:aws:autoscaling:us-west-2:123123123123:scalingPolicy:65acc44b-d34a-4956-ba61-cfee4f9242be:autoScalingGroupName/my-cfn-stack-AWSEBAutoScalingGroup-UP1RZPYEFMGW:policyName/my-cfn-stack-AWSEBAutoScalingScaleUpPolicy-96KTMSIQJPF0',
            'ResourceType': 'AWS::AutoScaling::ScalingPolicy',
            'Timestamp': datetime.datetime(2018, 9, 15, 19, 43, 11, 633000, tzinfo=tz.tzutc()),
            'ResourceStatus': 'CREATE_IN_PROGRESS',
            'ResourceStatusReason': 'Resource creation Initiated',
            'ResourceProperties': '{"ScalingAdjustment":"1","AutoScalingGroupName":"my-cfn-stack-AWSEBAutoScalingGroup-UP1RZPYEFMGW","AdjustmentType":"ChangeInCapacity"}'
        },
        {
            'StackId': 'arn:aws:cloudformation:us-west-2:123123123123:stack/my-cfn-stack/5f60bc20-b91f-11e8-bed7-027277c482a4',
            'EventId': 'AWSEBAutoScalingScaleDownPolicy-CREATE_COMPLETE-2018-09-15T19:43:11.449Z',
            'StackName': 'my-cfn-stack',
            'LogicalResourceId': 'AWSEBAutoScalingScaleDownPolicy',
            'PhysicalResourceId': 'arn:aws:autoscaling:us-west-2:123123123123:scalingPolicy:b2818a6b-eb82-46bf-8e2c-d356dd461be3:autoScalingGroupName/my-cfn-stack-AWSEBAutoScalingGroup-UP1RZPYEFMGW:policyName/my-cfn-stack-AWSEBAutoScalingScaleDownPolicy-14H4PCTKAXIJ1',
            'ResourceType': 'AWS::AutoScaling::ScalingPolicy',
            'Timestamp': datetime.datetime(2018, 9, 15, 19, 43, 11, 449000, tzinfo=tz.tzutc()),
            'ResourceStatus': 'CREATE_COMPLETE',
            'ResourceProperties': '{"ScalingAdjustment":"-1","AutoScalingGroupName":"my-cfn-stack-AWSEBAutoScalingGroup-UP1RZPYEFMGW","AdjustmentType":"ChangeInCapacity"}'
        },
        {
            'StackId': 'arn:aws:cloudformation:us-west-2:123123123123:stack/my-cfn-stack/5f60bc20-b91f-11e8-bed7-027277c482a4',
            'EventId': 'AWSEBAutoScalingScaleDownPolicy-CREATE_IN_PROGRESS-2018-09-15T19:43:11.336Z',
            'StackName': 'my-cfn-stack',
            'LogicalResourceId': 'AWSEBAutoScalingScaleDownPolicy',
            'PhysicalResourceId': 'arn:aws:autoscaling:us-west-2:123123123123:scalingPolicy:b2818a6b-eb82-46bf-8e2c-d356dd461be3:autoScalingGroupName/my-cfn-stack-AWSEBAutoScalingGroup-UP1RZPYEFMGW:policyName/my-cfn-stack-AWSEBAutoScalingScaleDownPolicy-14H4PCTKAXIJ1',
            'ResourceType': 'AWS::AutoScaling::ScalingPolicy',
            'Timestamp': datetime.datetime(2018, 9, 15, 19, 43, 11, 336000, tzinfo=tz.tzutc()),
            'ResourceStatus': 'CREATE_IN_PROGRESS',
            'ResourceStatusReason': 'Resource creation Initiated',
            'ResourceProperties': '{"ScalingAdjustment":"-1","AutoScalingGroupName":"my-cfn-stack-AWSEBAutoScalingGroup-UP1RZPYEFMGW","AdjustmentType":"ChangeInCapacity"}'
        },
        {
            'StackId': 'arn:aws:cloudformation:us-west-2:123123123123:stack/my-cfn-stack/5f60bc20-b91f-11e8-bed7-027277c482a4',
            'EventId': 'AWSEBAutoScalingScaleUpPolicy-CREATE_IN_PROGRESS-2018-09-15T19:43:11.202Z',
            'StackName': 'my-cfn-stack',
            'LogicalResourceId': 'AWSEBAutoScalingScaleUpPolicy',
            'PhysicalResourceId': '',
            'ResourceType': 'AWS::AutoScaling::ScalingPolicy',
            'Timestamp': datetime.datetime(2018, 9, 15, 19, 43, 11, 202000, tzinfo=tz.tzutc()),
            'ResourceStatus': 'CREATE_IN_PROGRESS',
            'ResourceProperties': '{"ScalingAdjustment":"1","AutoScalingGroupName":"my-cfn-stack-AWSEBAutoScalingGroup-UP1RZPYEFMGW","AdjustmentType":"ChangeInCapacity"}'
        },
        {
            'StackId': 'arn:aws:cloudformation:us-west-2:123123123123:stack/my-cfn-stack/5f60bc20-b91f-11e8-bed7-027277c482a4',
            'EventId': 'AWSEBInstanceLaunchWaitCondition-CREATE_IN_PROGRESS-2018-09-15T19:43:11.104Z',
            'StackName': 'my-cfn-stack',
            'LogicalResourceId': 'AWSEBInstanceLaunchWaitCondition',
            'PhysicalResourceId': 'arn:aws:cloudformation:us-west-2:123123123123:stack/my-cfn-stack/5f60bc20-b91f-11e8-bed7-027277c482a4/AWSEBInstanceLaunchWaitHandle',
            'ResourceType': 'AWS::CloudFormation::WaitCondition',
            'Timestamp': datetime.datetime(2018, 9, 15, 19, 43, 11, 104000, tzinfo=tz.tzutc()),
            'ResourceStatus': 'CREATE_IN_PROGRESS',
            'ResourceStatusReason': 'Resource creation Initiated',
            'ResourceProperties': '{"Timeout":"900","Count":"1","Handle":"https://cloudformation-waitcondition-us-west-2.s3-us-west-2.amazonaws.com/arn%3Aaws%3Acloudformation%3Aus-west-2%3A123123123123%3Astack/my-cfn-stack/5f60bc20-b91f-11e8-bed7-027277c482a4/AWSEBInstanceLaunchWaitHandle?AWSAccessKeyId=AKIAI5ZDPCT4PV2AKKAA&Expires=1537126906&Signature=ZMzoAUTwL5OU2ImILgqCmBXwsvo%3D"}'
        },
        {
            'StackId': 'arn:aws:cloudformation:us-west-2:123123123123:stack/my-cfn-stack/5f60bc20-b91f-11e8-bed7-027277c482a4',
            'EventId': 'AWSEBInstanceLaunchWaitCondition-CREATE_IN_PROGRESS-2018-09-15T19:43:10.945Z',
            'StackName': 'my-cfn-stack',
            'LogicalResourceId': 'AWSEBInstanceLaunchWaitCondition',
            'PhysicalResourceId': '',
            'ResourceType': 'AWS::CloudFormation::WaitCondition',
            'Timestamp': datetime.datetime(2018, 9, 15, 19, 43, 10, 945000, tzinfo=tz.tzutc()),
            'ResourceStatus': 'CREATE_IN_PROGRESS',
            'ResourceProperties': '{"Timeout":"900","Count":"1","Handle":"https://cloudformation-waitcondition-us-west-2.s3-us-west-2.amazonaws.com/arn%3Aaws%3Acloudformation%3Aus-west-2%3A123123123123%3Astack/my-cfn-stack/5f60bc20-b91f-11e8-bed7-027277c482a4/AWSEBInstanceLaunchWaitHandle?AWSAccessKeyId=AKIAI5ZDPCT4PV2AKKAA&Expires=1537126906&Signature=ZMzoAUTwL5OU2ImILgqCmBXwsvo%3D"}'
        },
        {
            'StackId': 'arn:aws:cloudformation:us-west-2:123123123123:stack/my-cfn-stack/5f60bc20-b91f-11e8-bed7-027277c482a4',
            'EventId': 'AWSEBAutoScalingScaleDownPolicy-CREATE_IN_PROGRESS-2018-09-15T19:43:10.889Z',
            'StackName': 'my-cfn-stack',
            'LogicalResourceId': 'AWSEBAutoScalingScaleDownPolicy',
            'PhysicalResourceId': '',
            'ResourceType': 'AWS::AutoScaling::ScalingPolicy',
            'Timestamp': datetime.datetime(2018, 9, 15, 19, 43, 10, 889000, tzinfo=tz.tzutc()),
            'ResourceStatus': 'CREATE_IN_PROGRESS',
            'ResourceProperties': '{"ScalingAdjustment":"-1","AutoScalingGroupName":"my-cfn-stack-AWSEBAutoScalingGroup-UP1RZPYEFMGW","AdjustmentType":"ChangeInCapacity"}'
        },
        {
            'StackId': 'arn:aws:cloudformation:us-west-2:123123123123:stack/my-cfn-stack/5f60bc20-b91f-11e8-bed7-027277c482a4',
            'EventId': 'AWSEBAutoScalingGroup-CREATE_COMPLETE-2018-09-15T19:43:07.525Z',
            'StackName': 'my-cfn-stack',
            'LogicalResourceId': 'AWSEBAutoScalingGroup',
            'PhysicalResourceId': 'my-cfn-stack-AWSEBAutoScalingGroup-UP1RZPYEFMGW',
            'ResourceType': 'AWS::AutoScaling::AutoScalingGroup',
            'Timestamp': datetime.datetime(2018, 9, 15, 19, 43, 7, 525000, tzinfo=tz.tzutc()),
            'ResourceStatus': 'CREATE_COMPLETE',
            'ResourceProperties': '{"MinSize":"1","LaunchConfigurationName":"my-cfn-stack-AWSEBAutoScalingLaunchConfiguration-NZO3NRE5JEEN","TargetGroupARNs":["arn:aws:elasticloadbalancing:us-west-2:123123123123:targetgroup/awseb-AWSEB-17R8PVLEWQWEC/234d7a174f1aa491"],"AvailabilityZones":["us-west-2a","us-west-2b"],"Cooldown":"360","VPCZoneIdentifier":["subnet-0556027c","subnet-005248b6cc2dfa908"],"MaxSize":"4","Tags":[{"Value":"****","Key":"elasticbeanstalk:environment-name","PropagateAtLaunch":"true"},{"Value":"****","Key":"Name","PropagateAtLaunch":"true"},{"Value":"****","Key":"elasticbeanstalk:environment-id","PropagateAtLaunch":"true"}]}'
        },
        {
            'StackId': 'arn:aws:cloudformation:us-west-2:123123123123:stack/my-cfn-stack/5f60bc20-b91f-11e8-bed7-027277c482a4',
            'EventId': 'AWSEBAutoScalingGroup-CREATE_IN_PROGRESS-2018-09-15T19:42:14.636Z',
            'StackName': 'my-cfn-stack',
            'LogicalResourceId': 'AWSEBAutoScalingGroup',
            'PhysicalResourceId': 'my-cfn-stack-AWSEBAutoScalingGroup-UP1RZPYEFMGW',
            'ResourceType': 'AWS::AutoScaling::AutoScalingGroup',
            'Timestamp': datetime.datetime(2018, 9, 15, 19, 42, 14, 636000, tzinfo=tz.tzutc()),
            'ResourceStatus': 'CREATE_IN_PROGRESS',
            'ResourceStatusReason': 'Resource creation Initiated',
            'ResourceProperties': '{"MinSize":"1","LaunchConfigurationName":"my-cfn-stack-AWSEBAutoScalingLaunchConfiguration-NZO3NRE5JEEN","TargetGroupARNs":["arn:aws:elasticloadbalancing:us-west-2:123123123123:targetgroup/awseb-AWSEB-17R8PVLEWQWEC/234d7a174f1aa491"],"AvailabilityZones":["us-west-2a","us-west-2b"],"Cooldown":"360","VPCZoneIdentifier":["subnet-0556027c","subnet-005248b6cc2dfa908"],"MaxSize":"4","Tags":[{"Value":"****","Key":"elasticbeanstalk:environment-name","PropagateAtLaunch":"true"},{"Value":"****","Key":"Name","PropagateAtLaunch":"true"},{"Value":"****","Key":"elasticbeanstalk:environment-id","PropagateAtLaunch":"true"}]}'
        },
        {
            'StackId': 'arn:aws:cloudformation:us-west-2:123123123123:stack/my-cfn-stack/5f60bc20-b91f-11e8-bed7-027277c482a4',
            'EventId': 'AWSEBAutoScalingGroup-CREATE_IN_PROGRESS-2018-09-15T19:42:13.720Z',
            'StackName': 'my-cfn-stack',
            'LogicalResourceId': 'AWSEBAutoScalingGroup',
            'PhysicalResourceId': '',
            'ResourceType': 'AWS::AutoScaling::AutoScalingGroup',
            'Timestamp': datetime.datetime(2018, 9, 15, 19, 42, 13, 720000, tzinfo=tz.tzutc()),
            'ResourceStatus': 'CREATE_IN_PROGRESS',
            'ResourceProperties': '{"MinSize":"1","LaunchConfigurationName":"my-cfn-stack-AWSEBAutoScalingLaunchConfiguration-NZO3NRE5JEEN","TargetGroupARNs":["arn:aws:elasticloadbalancing:us-west-2:123123123123:targetgroup/awseb-AWSEB-17R8PVLEWQWEC/234d7a174f1aa491"],"AvailabilityZones":["us-west-2a","us-west-2b"],"Cooldown":"360","VPCZoneIdentifier":["subnet-0556027c","subnet-005248b6cc2dfa908"],"MaxSize":"4","Tags":[{"Value":"****","Key":"elasticbeanstalk:environment-name","PropagateAtLaunch":"true"},{"Value":"****","Key":"Name","PropagateAtLaunch":"true"},{"Value":"****","Key":"elasticbeanstalk:environment-id","PropagateAtLaunch":"true"}]}'
        },
        {
            'StackId': 'arn:aws:cloudformation:us-west-2:123123123123:stack/my-cfn-stack/5f60bc20-b91f-11e8-bed7-027277c482a4',
            'EventId': 'AWSEBAutoScalingLaunchConfiguration-CREATE_COMPLETE-2018-09-15T19:42:07.901Z',
            'StackName': 'my-cfn-stack',
            'LogicalResourceId': 'AWSEBAutoScalingLaunchConfiguration',
            'PhysicalResourceId': 'my-cfn-stack-AWSEBAutoScalingLaunchConfiguration-NZO3NRE5JEEN',
            'ResourceType': 'AWS::AutoScaling::LaunchConfiguration',
            'Timestamp': datetime.datetime(2018, 9, 15, 19, 42, 7, 901000, tzinfo=tz.tzutc()),
            'ResourceStatus': 'CREATE_COMPLETE',
            'ResourceProperties': '{"****":"****"}'
        },
        {
            'StackId': 'arn:aws:cloudformation:us-west-2:123123123123:stack/my-cfn-stack/5f60bc20-b91f-11e8-bed7-027277c482a4',
            'EventId': 'AWSEBAutoScalingLaunchConfiguration-CREATE_IN_PROGRESS-2018-09-15T19:42:07.617Z',
            'StackName': 'my-cfn-stack',
            'LogicalResourceId': 'AWSEBAutoScalingLaunchConfiguration',
            'PhysicalResourceId': 'my-cfn-stack-AWSEBAutoScalingLaunchConfiguration-NZO3NRE5JEEN',
            'ResourceType': 'AWS::AutoScaling::LaunchConfiguration',
            'Timestamp': datetime.datetime(2018, 9, 15, 19, 42, 7, 617000, tzinfo=tz.tzutc()),
            'ResourceStatus': 'CREATE_IN_PROGRESS',
            'ResourceStatusReason': 'Resource creation Initiated',
            'ResourceProperties': '{"****":"****"}'
        },
        {
            'StackId': 'arn:aws:cloudformation:us-west-2:123123123123:stack/my-cfn-stack/5f60bc20-b91f-11e8-bed7-027277c482a4',
            'EventId': 'AWSEBAutoScalingLaunchConfiguration-CREATE_IN_PROGRESS-2018-09-15T19:42:06.998Z',
            'StackName': 'my-cfn-stack',
            'LogicalResourceId': 'AWSEBAutoScalingLaunchConfiguration',
            'PhysicalResourceId': '',
            'ResourceType': 'AWS::AutoScaling::LaunchConfiguration',
            'Timestamp': datetime.datetime(2018, 9, 15, 19, 42, 6, 998000, tzinfo=tz.tzutc()),
            'ResourceStatus': 'CREATE_IN_PROGRESS',
            'ResourceProperties': '{"****":"****"}'
        },
        {
            'StackId': 'arn:aws:cloudformation:us-west-2:123123123123:stack/my-cfn-stack/5f60bc20-b91f-11e8-bed7-027277c482a4',
            'EventId': 'AWSEBSecurityGroup-CREATE_COMPLETE-2018-09-15T19:42:03.029Z',
            'StackName': 'my-cfn-stack',
            'LogicalResourceId': 'AWSEBSecurityGroup',
            'PhysicalResourceId': 'sg-0de671aa9d26f5fc0',
            'ResourceType': 'AWS::EC2::SecurityGroup',
            'Timestamp': datetime.datetime(2018, 9, 15, 19, 42, 3, 29000, tzinfo=tz.tzutc()),
            'ResourceStatus': 'CREATE_COMPLETE',
            'ResourceProperties': '{"GroupDescription":"VPC Security Group","VpcId":"vpc-574cb42f","SecurityGroupIngress":[{"FromPort":"80","ToPort":"80","IpProtocol":"tcp","SourceSecurityGroupId":"sg-088da58b23bc89ea2"}]}'
        },
        {
            'StackId': 'arn:aws:cloudformation:us-west-2:123123123123:stack/my-cfn-stack/5f60bc20-b91f-11e8-bed7-027277c482a4',
            'EventId': 'AWSEBSecurityGroup-CREATE_IN_PROGRESS-2018-09-15T19:42:02.027Z',
            'StackName': 'my-cfn-stack',
            'LogicalResourceId': 'AWSEBSecurityGroup',
            'PhysicalResourceId': 'sg-0de671aa9d26f5fc0',
            'ResourceType': 'AWS::EC2::SecurityGroup',
            'Timestamp': datetime.datetime(2018, 9, 15, 19, 42, 2, 27000, tzinfo=tz.tzutc()),
            'ResourceStatus': 'CREATE_IN_PROGRESS',
            'ResourceStatusReason': 'Resource creation Initiated',
            'ResourceProperties': '{"GroupDescription":"VPC Security Group","VpcId":"vpc-574cb42f","SecurityGroupIngress":[{"FromPort":"80","ToPort":"80","IpProtocol":"tcp","SourceSecurityGroupId":"sg-088da58b23bc89ea2"}]}'
        },
        {
            'StackId': 'arn:aws:cloudformation:us-west-2:123123123123:stack/my-cfn-stack/5f60bc20-b91f-11e8-bed7-027277c482a4',
            'EventId': 'AWSEBV2LoadBalancer-CREATE_IN_PROGRESS-2018-09-15T19:41:58.955Z',
            'StackName': 'my-cfn-stack',
            'LogicalResourceId': 'AWSEBV2LoadBalancer',
            'PhysicalResourceId': 'arn:aws:elasticloadbalancing:us-west-2:123123123123:loadbalancer/app/awseb-AWSEB-1VGXTCA62TZW5/f58275dd12edce24',
            'ResourceType': 'AWS::ElasticLoadBalancingV2::LoadBalancer',
            'Timestamp': datetime.datetime(2018, 9, 15, 19, 41, 58, 955000, tzinfo=tz.tzutc()),
            'ResourceStatus': 'CREATE_IN_PROGRESS',
            'ResourceStatusReason': 'Resource creation Initiated',
            'ResourceProperties': '{"SecurityGroups":["sg-088da58b23bc89ea2"],"Subnets":["subnet-0556027c","subnet-005248b6cc2dfa908"]}'
        },
        {
            'StackId': 'arn:aws:cloudformation:us-west-2:123123123123:stack/my-cfn-stack/5f60bc20-b91f-11e8-bed7-027277c482a4',
            'EventId': 'AWSEBV2LoadBalancer-CREATE_IN_PROGRESS-2018-09-15T19:41:57.909Z',
            'StackName': 'my-cfn-stack',
            'LogicalResourceId': 'AWSEBV2LoadBalancer',
            'PhysicalResourceId': '',
            'ResourceType': 'AWS::ElasticLoadBalancingV2::LoadBalancer',
            'Timestamp': datetime.datetime(2018, 9, 15, 19, 41, 57, 909000, tzinfo=tz.tzutc()),
            'ResourceStatus': 'CREATE_IN_PROGRESS',
            'ResourceProperties': '{"SecurityGroups":["sg-088da58b23bc89ea2"],"Subnets":["subnet-0556027c","subnet-005248b6cc2dfa908"]}'
        },
        {
            'StackId': 'arn:aws:cloudformation:us-west-2:123123123123:stack/my-cfn-stack/5f60bc20-b91f-11e8-bed7-027277c482a4',
            'EventId': 'AWSEBSecurityGroup-CREATE_IN_PROGRESS-2018-09-15T19:41:57.478Z',
            'StackName': 'my-cfn-stack',
            'LogicalResourceId': 'AWSEBSecurityGroup',
            'PhysicalResourceId': '',
            'ResourceType': 'AWS::EC2::SecurityGroup',
            'Timestamp': datetime.datetime(2018, 9, 15, 19, 41, 57, 478000, tzinfo=tz.tzutc()),
            'ResourceStatus': 'CREATE_IN_PROGRESS',
            'ResourceProperties': '{"GroupDescription":"VPC Security Group","VpcId":"vpc-574cb42f","SecurityGroupIngress":[{"FromPort":"80","ToPort":"80","IpProtocol":"tcp","SourceSecurityGroupId":"sg-088da58b23bc89ea2"}]}'
        },
        {
            'StackId': 'arn:aws:cloudformation:us-west-2:123123123123:stack/my-cfn-stack/5f60bc20-b91f-11e8-bed7-027277c482a4',
            'EventId': 'AWSEBLoadBalancerSecurityGroup-CREATE_COMPLETE-2018-09-15T19:41:53.947Z',
            'StackName': 'my-cfn-stack',
            'LogicalResourceId': 'AWSEBLoadBalancerSecurityGroup',
            'PhysicalResourceId': 'sg-088da58b23bc89ea2',
            'ResourceType': 'AWS::EC2::SecurityGroup',
            'Timestamp': datetime.datetime(2018, 9, 15, 19, 41, 53, 947000, tzinfo=tz.tzutc()),
            'ResourceStatus': 'CREATE_COMPLETE',
            'ResourceProperties': '{"GroupDescription":"Load Balancer Security Group","VpcId":"vpc-574cb42f","SecurityGroupIngress":[{"CidrIp":"0.0.0.0/0","FromPort":"80","ToPort":"80","IpProtocol":"tcp"}],"SecurityGroupEgress":[{"CidrIp":"0.0.0.0/0","FromPort":"80","ToPort":"80","IpProtocol":"tcp"}]}'
        },
        {
            'StackId': 'arn:aws:cloudformation:us-west-2:123123123123:stack/my-cfn-stack/5f60bc20-b91f-11e8-bed7-027277c482a4',
            'EventId': 'AWSEBLoadBalancerSecurityGroup-CREATE_IN_PROGRESS-2018-09-15T19:41:52.616Z',
            'StackName': 'my-cfn-stack',
            'LogicalResourceId': 'AWSEBLoadBalancerSecurityGroup',
            'PhysicalResourceId': 'sg-088da58b23bc89ea2',
            'ResourceType': 'AWS::EC2::SecurityGroup',
            'Timestamp': datetime.datetime(2018, 9, 15, 19, 41, 52, 616000, tzinfo=tz.tzutc()),
            'ResourceStatus': 'CREATE_IN_PROGRESS',
            'ResourceStatusReason': 'Resource creation Initiated',
            'ResourceProperties': '{"GroupDescription":"Load Balancer Security Group","VpcId":"vpc-574cb42f","SecurityGroupIngress":[{"CidrIp":"0.0.0.0/0","FromPort":"80","ToPort":"80","IpProtocol":"tcp"}],"SecurityGroupEgress":[{"CidrIp":"0.0.0.0/0","FromPort":"80","ToPort":"80","IpProtocol":"tcp"}]}'
        },
        {
            'StackId': 'arn:aws:cloudformation:us-west-2:123123123123:stack/my-cfn-stack/5f60bc20-b91f-11e8-bed7-027277c482a4',
            'EventId': 'AWSEBV2LoadBalancerTargetGroup-CREATE_COMPLETE-2018-09-15T19:41:47.968Z',
            'StackName': 'my-cfn-stack',
            'LogicalResourceId': 'AWSEBV2LoadBalancerTargetGroup',
            'PhysicalResourceId': 'arn:aws:elasticloadbalancing:us-west-2:123123123123:targetgroup/awseb-AWSEB-17R8PVLEWQWEC/234d7a174f1aa491',
            'ResourceType': 'AWS::ElasticLoadBalancingV2::TargetGroup',
            'Timestamp': datetime.datetime(2018, 9, 15, 19, 41, 47, 968000, tzinfo=tz.tzutc()),
            'ResourceStatus': 'CREATE_COMPLETE',
            'ResourceProperties': '{"HealthCheckIntervalSeconds":"15","VpcId":"vpc-574cb42f","HealthyThresholdCount":"3","HealthCheckPath":"/","Port":"80","TargetGroupAttributes":[{"Value":"20","Key":"deregistration_delay.timeout_seconds"}],"Protocol":"HTTP","UnhealthyThresholdCount":"5","HealthCheckTimeoutSeconds":"5"}'
        },
        {
            'StackId': 'arn:aws:cloudformation:us-west-2:123123123123:stack/my-cfn-stack/5f60bc20-b91f-11e8-bed7-027277c482a4',
            'EventId': 'AWSEBLoadBalancerSecurityGroup-CREATE_IN_PROGRESS-2018-09-15T19:41:47.954Z',
            'StackName': 'my-cfn-stack',
            'LogicalResourceId': 'AWSEBLoadBalancerSecurityGroup',
            'PhysicalResourceId': '',
            'ResourceType': 'AWS::EC2::SecurityGroup',
            'Timestamp': datetime.datetime(2018, 9, 15, 19, 41, 47, 954000, tzinfo=tz.tzutc()),
            'ResourceStatus': 'CREATE_IN_PROGRESS',
            'ResourceProperties': '{"GroupDescription":"Load Balancer Security Group","VpcId":"vpc-574cb42f","SecurityGroupIngress":[{"CidrIp":"0.0.0.0/0","FromPort":"80","ToPort":"80","IpProtocol":"tcp"}],"SecurityGroupEgress":[{"CidrIp":"0.0.0.0/0","FromPort":"80","ToPort":"80","IpProtocol":"tcp"}]}'
        },
        {
            'StackId': 'arn:aws:cloudformation:us-west-2:123123123123:stack/my-cfn-stack/5f60bc20-b91f-11e8-bed7-027277c482a4',
            'EventId': 'AWSEBBeanstalkMetadata-CREATE_COMPLETE-2018-09-15T19:41:47.843Z',
            'StackName': 'my-cfn-stack',
            'LogicalResourceId': 'AWSEBBeanstalkMetadata',
            'PhysicalResourceId': 'https://cloudformation-waitcondition-us-west-2.s3-us-west-2.amazonaws.com/arn%3Aaws%3Acloudformation%3Aus-west-2%3A123123123123%3Astack/my-cfn-stack/5f60bc20-b91f-11e8-bed7-027277c482a4/AWSEBBeanstalkMetadata?AWSAccessKeyId=AKIAI5ZDPCT4PV2AKKAA&Expires=1537126907&Signature=IKsDdTYtxeYQRaCIgNyT5OQTqNQ%3D',
            'ResourceType': 'AWS::CloudFormation::WaitConditionHandle',
            'Timestamp': datetime.datetime(2018, 9, 15, 19, 41, 47, 843000, tzinfo=tz.tzutc()),
            'ResourceStatus': 'CREATE_COMPLETE',
            'ResourceProperties': '{}'
        },
        {
            'StackId': 'arn:aws:cloudformation:us-west-2:123123123123:stack/my-cfn-stack/5f60bc20-b91f-11e8-bed7-027277c482a4',
            'EventId': 'AWSEBBeanstalkMetadata-CREATE_IN_PROGRESS-2018-09-15T19:41:47.693Z',
            'StackName': 'my-cfn-stack',
            'LogicalResourceId': 'AWSEBBeanstalkMetadata',
            'PhysicalResourceId': 'https://cloudformation-waitcondition-us-west-2.s3-us-west-2.amazonaws.com/arn%3Aaws%3Acloudformation%3Aus-west-2%3A123123123123%3Astack/my-cfn-stack/5f60bc20-b91f-11e8-bed7-027277c482a4/AWSEBBeanstalkMetadata?AWSAccessKeyId=AKIAI5ZDPCT4PV2AKKAA&Expires=1537126907&Signature=IKsDdTYtxeYQRaCIgNyT5OQTqNQ%3D',
            'ResourceType': 'AWS::CloudFormation::WaitConditionHandle',
            'Timestamp': datetime.datetime(2018, 9, 15, 19, 41, 47, 693000, tzinfo=tz.tzutc()),
            'ResourceStatus': 'CREATE_IN_PROGRESS',
            'ResourceStatusReason': 'Resource creation Initiated',
            'ResourceProperties': '{}'
        },
        {
            'StackId': 'arn:aws:cloudformation:us-west-2:123123123123:stack/my-cfn-stack/5f60bc20-b91f-11e8-bed7-027277c482a4',
            'EventId': 'AWSEBV2LoadBalancerTargetGroup-CREATE_IN_PROGRESS-2018-09-15T19:41:47.479Z',
            'StackName': 'my-cfn-stack',
            'LogicalResourceId': 'AWSEBV2LoadBalancerTargetGroup',
            'PhysicalResourceId': 'arn:aws:elasticloadbalancing:us-west-2:123123123123:targetgroup/awseb-AWSEB-17R8PVLEWQWEC/234d7a174f1aa491',
            'ResourceType': 'AWS::ElasticLoadBalancingV2::TargetGroup',
            'Timestamp': datetime.datetime(2018, 9, 15, 19, 41, 47, 479000, tzinfo=tz.tzutc()),
            'ResourceStatus': 'CREATE_IN_PROGRESS',
            'ResourceStatusReason': 'Resource creation Initiated',
            'ResourceProperties': '{"HealthCheckIntervalSeconds":"15","VpcId":"vpc-574cb42f","HealthyThresholdCount":"3","HealthCheckPath":"/","Port":"80","TargetGroupAttributes":[{"Value":"20","Key":"deregistration_delay.timeout_seconds"}],"Protocol":"HTTP","UnhealthyThresholdCount":"5","HealthCheckTimeoutSeconds":"5"}'
        },
        {
            'StackId': 'arn:aws:cloudformation:us-west-2:123123123123:stack/my-cfn-stack/5f60bc20-b91f-11e8-bed7-027277c482a4',
            'EventId': 'AWSEBBeanstalkMetadata-CREATE_IN_PROGRESS-2018-09-15T19:41:47.477Z',
            'StackName': 'my-cfn-stack',
            'LogicalResourceId': 'AWSEBBeanstalkMetadata',
            'PhysicalResourceId': '',
            'ResourceType': 'AWS::CloudFormation::WaitConditionHandle',
            'Timestamp': datetime.datetime(2018, 9, 15, 19, 41, 47, 477000, tzinfo=tz.tzutc()),
            'ResourceStatus': 'CREATE_IN_PROGRESS',
            'ResourceProperties': '{}'
        },
        {
            'StackId': 'arn:aws:cloudformation:us-west-2:123123123123:stack/my-cfn-stack/5f60bc20-b91f-11e8-bed7-027277c482a4',
            'EventId': 'AWSEBV2LoadBalancerTargetGroup-CREATE_IN_PROGRESS-2018-09-15T19:41:47.079Z',
            'StackName': 'my-cfn-stack',
            'LogicalResourceId': 'AWSEBV2LoadBalancerTargetGroup',
            'PhysicalResourceId': '',
            'ResourceType': 'AWS::ElasticLoadBalancingV2::TargetGroup',
            'Timestamp': datetime.datetime(2018, 9, 15, 19, 41, 47, 79000, tzinfo=tz.tzutc()),
            'ResourceStatus': 'CREATE_IN_PROGRESS',
            'ResourceProperties': '{"HealthCheckIntervalSeconds":"15","VpcId":"vpc-574cb42f","HealthyThresholdCount":"3","HealthCheckPath":"/","Port":"80","TargetGroupAttributes":[{"Value":"20","Key":"deregistration_delay.timeout_seconds"}],"Protocol":"HTTP","UnhealthyThresholdCount":"5","HealthCheckTimeoutSeconds":"5"}'
        },
        {
            'StackId': 'arn:aws:cloudformation:us-west-2:123123123123:stack/my-cfn-stack/5f60bc20-b91f-11e8-bed7-027277c482a4',
            'EventId': 'AWSEBInstanceLaunchWaitHandle-CREATE_COMPLETE-2018-09-15T19:41:46.876Z',
            'StackName': 'my-cfn-stack',
            'LogicalResourceId': 'AWSEBInstanceLaunchWaitHandle',
            'PhysicalResourceId': 'https://cloudformation-waitcondition-us-west-2.s3-us-west-2.amazonaws.com/arn%3Aaws%3Acloudformation%3Aus-west-2%3A123123123123%3Astack/my-cfn-stack/5f60bc20-b91f-11e8-bed7-027277c482a4/AWSEBInstanceLaunchWaitHandle?AWSAccessKeyId=AKIAI5ZDPCT4PV2AKKAA&Expires=1537126906&Signature=ZMzoAUTwL5OU2ImILgqCmBXwsvo%3D',
            'ResourceType': 'AWS::CloudFormation::WaitConditionHandle',
            'Timestamp': datetime.datetime(2018, 9, 15, 19, 41, 46, 876000, tzinfo=tz.tzutc()),
            'ResourceStatus': 'CREATE_COMPLETE',
            'ResourceProperties': '{}'
        },
        {
            'StackId': 'arn:aws:cloudformation:us-west-2:123123123123:stack/my-cfn-stack/5f60bc20-b91f-11e8-bed7-027277c482a4',
            'EventId': 'AWSEBInstanceLaunchWaitHandle-CREATE_IN_PROGRESS-2018-09-15T19:41:46.696Z',
            'StackName': 'my-cfn-stack',
            'LogicalResourceId': 'AWSEBInstanceLaunchWaitHandle',
            'PhysicalResourceId': 'https://cloudformation-waitcondition-us-west-2.s3-us-west-2.amazonaws.com/arn%3Aaws%3Acloudformation%3Aus-west-2%3A123123123123%3Astack/my-cfn-stack/5f60bc20-b91f-11e8-bed7-027277c482a4/AWSEBInstanceLaunchWaitHandle?AWSAccessKeyId=AKIAI5ZDPCT4PV2AKKAA&Expires=1537126906&Signature=ZMzoAUTwL5OU2ImILgqCmBXwsvo%3D',
            'ResourceType': 'AWS::CloudFormation::WaitConditionHandle',
            'Timestamp': datetime.datetime(2018, 9, 15, 19, 41, 46, 696000, tzinfo=tz.tzutc()),
            'ResourceStatus': 'CREATE_IN_PROGRESS',
            'ResourceStatusReason': 'Resource creation Initiated',
            'ResourceProperties': '{}'
        },
        {
            'StackId': 'arn:aws:cloudformation:us-west-2:123123123123:stack/my-cfn-stack/5f60bc20-b91f-11e8-bed7-027277c482a4',
            'EventId': 'AWSEBInstanceLaunchWaitHandle-CREATE_IN_PROGRESS-2018-09-15T19:41:46.383Z',
            'StackName': 'my-cfn-stack',
            'LogicalResourceId': 'AWSEBInstanceLaunchWaitHandle',
            'PhysicalResourceId': '',
            'ResourceType': 'AWS::CloudFormation::WaitConditionHandle',
            'Timestamp': datetime.datetime(2018, 9, 15, 19, 41, 46, 383000, tzinfo=tz.tzutc()),
            'ResourceStatus': 'CREATE_IN_PROGRESS',
            'ResourceProperties': '{}'
        },
        {
            'StackId': 'arn:aws:cloudformation:us-west-2:123123123123:stack/my-cfn-stack/5f60bc20-b91f-11e8-bed7-027277c482a4',
            'EventId': '5f613150-b91f-11e8-bed7-027277c482a4',
            'StackName': 'my-cfn-stack',
            'LogicalResourceId': 'my-cfn-stack',
            'PhysicalResourceId': 'arn:aws:cloudformation:us-west-2:123123123123:stack/my-cfn-stack/5f60bc20-b91f-11e8-bed7-027277c482a4',
            'ResourceType': 'AWS::CloudFormation::Stack',
            'Timestamp': datetime.datetime(2018, 9, 15, 19, 41, 43, 73000, tzinfo=tz.tzutc()),
            'ResourceStatus': 'CREATE_IN_PROGRESS',
            'ResourceStatusReason': 'User Initiated'
        }
    ],
    'ResponseMetadata': {
        'RequestId': '92b827b1-bafb-11e8-a480-cd9a64683a20',
        'HTTPStatusCode': 200,
        'HTTPHeaders': {
            'x-amzn-requestid': '92b827b1-bafb-11e8-a480-cd9a64683a20',
            'content-type': 'text/xml',
            'content-length': '51972',
            'vary': 'Accept-Encoding',
            'date': 'Tue, 18 Sep 2018 04:30:29 GMT'
        },
        'RetryAttempts': 0
    }
}


GET_LISTENERS_FOR_LOAD_BALANCER_RESPONSE= [
{
    "Listeners": [
        {
            "ListenerArn": "arn:aws:elasticloadbalancing:us-east-1:881508045124:listener/app/alb-2/5a957e362e1339a9/45eb527de2160a42",
            "LoadBalancerArn": "arn:aws:elasticloadbalancing:us-east-1:881508045124:loadbalancer/app/alb-2/5a957e362e1339a9",
            "Port": 100,
            "Protocol": "HTTP",
            "DefaultActions": [
                {
                    "Type": "forward",
                    "TargetGroupArn": "arn:aws:elasticloadbalancing:us-east-1:881508045124:targetgroup/alb-2-tg-1/e62e3762716b3f54",
                    "Order": 1,
                    "ForwardConfig": {
                        "TargetGroups": [
                            {
                                "TargetGroupArn": "arn:aws:elasticloadbalancing:us-east-1:881508045124:targetgroup/alb-2-tg-1/e62e3762716b3f54",
                                "Weight": 1
                            }
                        ],
                        "TargetGroupStickinessConfig": {
                            "Enabled": 'false'
                        }
                    }
                }
            ]
        },
        {
            "ListenerArn": "arn:aws:elasticloadbalancing:us-east-1:881508045124:listener/app/alb-2/5a957e362e1339a9/a9716362c384b615",
            "LoadBalancerArn": "arn:aws:elasticloadbalancing:us-east-1:881508045124:loadbalancer/app/alb-2/5a957e362e1339a9",
            "Port": 80,
            "Protocol": "HTTP",
            "DefaultActions": [
                {
                    "Type": "forward",
                    "TargetGroupArn": "arn:aws:elasticloadbalancing:us-east-1:881508045124:targetgroup/alb-2-tg-1/e62e3762716b3f54",
                    "Order": 1,
                    "ForwardConfig": {
                        "TargetGroups": [
                            {
                                "TargetGroupArn": "arn:aws:elasticloadbalancing:us-east-1:881508045124:targetgroup/alb-2-tg-1/e62e3762716b3f54",
                                "Weight": 1
                            }
                        ],
                        "TargetGroupStickinessConfig": {
                            "Enabled": 'false'
                        }
                    }
                }
            ]
        }
    ]
}]


GET_LISTENERS_FOR_LOAD_BALANCER_RESPONSE_2 = [
{
    "Listeners": [
        {
            "ListenerArn": "arn:aws:elasticloadbalancing:us-east-1:881508045124:listener/app/alb-3/3dfc9ab663f79319/156708acbcbfec4b",
            "LoadBalancerArn": "arn:aws:elasticloadbalancing:us-east-1:881508045124:loadbalancer/app/alb-3/3dfc9ab663f79319",
            "Port": 80,
            "Protocol": "HTTP",
            "DefaultActions": [
                {
                    "Type": "forward",
                    "TargetGroupArn": "arn:aws:elasticloadbalancing:us-east-1:881508045124:targetgroup/alb-3-tg-1/584bea6a7a357574",
                    "ForwardConfig": {
                        "TargetGroups": [
                            {
                                "TargetGroupArn": "arn:aws:elasticloadbalancing:us-east-1:881508045124:targetgroup/alb-3-tg-1/584bea6a7a357574",
                                "Weight": 1
                            }
                        ],
                        "TargetGroupStickinessConfig": {
                            "Enabled": 'false'
                        }
                    }
                }
            ]
        }
    ]
}]


DESCRIBE_LOAD_BALANCERS_RESPONSE = [
{
    "LoadBalancers": [
        {
            "LoadBalancerArn": "arn:aws:elasticloadbalancing:us-east-1:881508045124:loadbalancer/app/alb-1/72074d479748b405",
            "DNSName": "alb-1-1923055434.us-east-1.elb.amazonaws.com",
            "CanonicalHostedZoneId": "Z35SXDOTRQ7X7K",
            "CreatedTime": "2020-07-07T17:18:20.290Z",
            "LoadBalancerName": "alb-1",
            "Scheme": "internet-facing",
            "VpcId": "vpc-bae3dbc0",
            "State": {
                "Code": "active"
            },
            "Type": "application",
            "AvailabilityZones": [
                {
                    "ZoneName": "us-east-1b",
                    "SubnetId": "subnet-74e80255",
                    "LoadBalancerAddresses": []
                },
                {
                    "ZoneName": "us-east-1a",
                    "SubnetId": "subnet-7a0be71c",
                    "LoadBalancerAddresses": []
                }
            ],
            "SecurityGroups": [
                "sg-abdee486"
            ],
            "IpAddressType": "ipv4"
        }
    ]
}]
