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
