from mock import Mock


def get_pathconfig():
    return Mock(docker_proj_path=lambda: DOCKER_PROJ_PATH,
                dockerfile_path=lambda: DOCKERFILE_PATH,
                new_dockerfile_path=lambda: NEW_DOCKERFILE_PATH,
                dockerignore_path=lambda: DOCKERIGNORE_PATH,
                logdir_path=lambda: LOGDIR_PATH,
                dockerrun_path=lambda: DOCKERRUN_PATH,
                compose_path=lambda: COMPOSE_PATH,
                setenv_path=lambda: SETENV_PATH,
                dockerfile_exists=lambda: DOCKERFILE_EXISTS,
                dockerrun_exists=lambda: DOCKERRUN_EXISTS)


def get_container_fs_handler():
    return Mock(pathconfig=get_pathconfig(),
                dockerrun=get_dockerrun_dict())


def get_multicontainer_fs_handler():
    return Mock(pathconfig=get_pathconfig(),
                hostlog_path=HOSTLOG_PATH,
                dockerrun=get_container_fs_handler())


def get_soln_stk():
    return Mock()


def get_container_cfg():
    return {}


def get_dockerrun_dict():
    return {'AWSEBDockerrunVersion': '1'}


DOCKER_PROJ_PATH = '/eb-project'
DOCKERFILE_PATH = '/eb-project/Dockerfile'
NEW_DOCKERFILE_PATH = '/eb-project/.elasticbeanstalk/Dockerfile.local'
DOCKERIGNORE_PATH = '/eb-project/.dockerignore'
LOGDIR_PATH = '/eb-project/.elasticbeanstalk/logs/local'
HOSTLOG_PATH = '/eb-project/.elasticbeanstalk/logs/local/12345_6789'
DOCKERRUN_PATH = '/eb-project/Dockerrun.aws.json'
COMPOSE_PATH = '/eb-project/.elasticbeanstalk/docker-compose.yml'
SETENV_PATH = '/eb-project/.elasticbeanstalk/.envvars'
DOCKERFILE_EXISTS = True
DOCKERRUN_EXISTS = True
HOST_PORT = '9000'
SOLN_STK = get_soln_stk()
CONTAINER_CFG = get_container_cfg()
DOCKERRUN_DICT = get_dockerrun_dict()
PATH_CONFIG = get_pathconfig()
MULTICONTAINER_FS_HANDLER = get_multicontainer_fs_handler()
CONTAINER_FS_HANDLER = get_container_fs_handler()
