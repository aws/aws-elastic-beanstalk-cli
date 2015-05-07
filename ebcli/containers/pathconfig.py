from ..core import fileoperations


class PathConfig(object):
    COMPOSE_FILENAME = 'docker-compose.yml'
    DOCKERCFG_FILENAME = '.dockercfg'
    DOCKERIGNORE_FILENAME = '.dockerignore'
    DOCKERFILE_FILENAME = 'Dockerfile'
    DOCKERRUN_FILENAME = 'Dockerrun.aws.json'
    LOCAL_STATE_FILENAME = '.localstate'
    NEW_DOCKERFILE_FILENAME = 'Dockerfile.local'
    ROOT_LOCAL_LOGS_DIRNAME = 'local'

    @staticmethod
    def docker_proj_path():
        return fileoperations.get_project_root()

    @classmethod
    def dockerfile_path(cls):
        return fileoperations.project_file_path(cls.DOCKERFILE_FILENAME)

    @classmethod
    def new_dockerfile_path(cls):
        return fileoperations.get_eb_file_full_location(cls.NEW_DOCKERFILE_FILENAME)

    @classmethod
    def dockerignore_path(cls):
        return fileoperations.project_file_path(cls.DOCKERIGNORE_FILENAME)

    @classmethod
    def logdir_path(cls):
        return fileoperations.get_logs_location(cls.ROOT_LOCAL_LOGS_DIRNAME)

    @classmethod
    def dockerrun_path(cls):
        return fileoperations.project_file_path(cls.DOCKERRUN_FILENAME)

    @classmethod
    def compose_path(cls):
        return fileoperations.get_eb_file_full_location(cls.COMPOSE_FILENAME)

    @classmethod
    def local_state_path(cls):
        return fileoperations.get_eb_file_full_location(cls.LOCAL_STATE_FILENAME)

    @classmethod
    def dockerfile_exists(cls):
        return fileoperations.project_file_exists(cls.DOCKERFILE_FILENAME)

    @classmethod
    def dockerrun_exists(cls):
        return fileoperations.project_file_exists(cls.DOCKERRUN_FILENAME)
