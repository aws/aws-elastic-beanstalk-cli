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
		}
	]
}
