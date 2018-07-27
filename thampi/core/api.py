from pathlib import Path
from typing import Dict

from thampi import core
from thampi.core import constants
import json
from thampi.lib import util
from thampi.lib.util import dicts
import subprocess
import docker
from pprint import pprint
import uuid
import shutil
import os
import requests
import slugify
import datetime
from thampi.lib import aws
import re

DEV_ENVIRONMENT = 'dev'

ZAPPA_BUCKET = 's3_bucket'
AWS_REGION = 'aws_region'
THAMPI = 'thampi'

PROJECT_ENV_VARIABLE = 'THAMPI_HOME'

DEFAULT_HOME = '.cache/thampi'

THAMPI_ZAPPA_SETTINGS = dict(keep_warm=True,
                             memory_size=3008,
                             slim_handler=True,
                             timeout_seconds=300)

AWS_FOLDER = '.aws'
PYTHON_VERSION_STR = 'python3.6'
LAMBDA_IMAGE = f'lambci/lambda:build-{PYTHON_VERSION_STR}'
SRC_PATH = '/src'

NAME_PATTERN_STRING = '^[a-zA-Z0-9_-]+$'
name_pattern = re.compile(NAME_PATTERN_STRING)


def match_str(a_str, a_pattern):
    if a_pattern.match(a_str):
        return True
    raise ValueError(f"String {a_str} does not match pattern:{a_pattern.pattern}")


# def thampi_init():
#     '''
#     Read Zappa file. If it does not exist, raise file not found exception
#     take dev settings, and create staging and production and add default settings
#     tmp store the zappa_settings file
#     write the new zappa_settings file
#     delete the temp zappa_settings file
#     :return:
#     '''
#     # cwd = Path(os.getcwd())
#     file_name = constants.ZAPPA_FILE_NAME
#     # zappa_settings_path = cwd / file_name
#     #
#     # if not zappa_settings_path.is_file():
#     #     raise ValueError(f"Expect {file_name} to be in the current working directory. Run 'thampi init' first.")
#     #
#     # # with open(zappa_settings_path) as f:
#     # #     data = json.load(f)
#     # data = json.load(zappa_settings_path.open())
#     # zappa_file = constants.ZAPPA_FILE_NAME
#
#     data = read_zappa(default_zappa_settings_path())
#     dev_environment = 'dev'
#     if dev_environment not in data:
#         raise ValueError(
#             f"Didn't find {dev_environment} as a key in {file_name}.\n"
#             f"- Delete {file_name}\n"
#             f"- Run 'thampi init' again and keep dev as the default environment/stage")
#     dev_data = data[dev_environment]
#     data['staging'] = settings(data, dev_data, 'staging')
#     data['production'] = settings(data, dev_data, 'production')
#
#     with open(default_zappa_settings_path(), 'w') as f:
#         json.dump(data, f, indent=4, ensure_ascii=False)

def thampi_init(all_config: Dict):
    data = dict()
    data['dev'] = all_config
    data['staging'] = settings(all_config)
    data['production'] = settings(all_config)

    with open(default_zappa_settings_path(), 'w') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


# def init():
#     # from click.testing import CliRunner
#     from zappa.cli import handle
#     # runner = CliRunner()
#     # result = runner.invoke(handler, ['init'])
#     # print(result)
#     cwd = Path(os.getcwd())
#     thampi_app = cwd / constants.THAMPI_APP
#
#     try:
#         thampi_app.touch()
#         handle()
#
#     except SystemExit:
#         thampi_app.unlink()
#         thampi_init()


def init(all_config: Dict):
    thampi_init(all_config)


def save_dependencies(path: Path):
    check_venv()
    subprocess.run(f'pip freeze > {str(path)}', shell=True)


def read_zappa_settings(zappa_settings_path: Path) -> Dict[str, Dict[str, str]]:
    if not zappa_settings_path.is_file():
        raise ValueError(
            f"Expect {zappa_settings_path} to be in the current working directory. Run 'thampi init' first.")

    with zappa_settings_path.open() as f:
        return json.load(f)


def remove_thampi(tmp_file):
    print('tmp_file:' + str(tmp_file))
    with open(tmp_file, 'r') as f:
        lines = f.readlines()
    thampi_line = 'thampi==0.1.0\n'
    if thampi_line in lines:
        lines.remove(thampi_line)

    with open(tmp_file, 'w') as f:
        f.writelines(lines)


# def deploy(environment: str):
#     clean_up(DEV_ENVIRONMENT)
#     a_uuid = str(uuid.uuid4())
#     # zappa_settings = clean_up('dev')
#     file_name = constants.ZAPPA_FILE_NAME
#     zappa_settings = read_zappa(file_name)
#
#     if environment == 'local':
#         # data = zappa_settings
#         # dev_environment = DEV_ENVIRONMENT
#         # if dev_environment not in data:
#         #     raise ValueError(
#         #         f"Didn't find {dev_environment} as a key in {file_name}.\n"
#         #         f"- Delete {file_name}\n"
#         #         f"- Run 'thampi init' again and keep dev as the default environment/stage")
#         # dev_data = data[dev_environment]
#         # data['local'] = settings(data, dev_data, 'local')
#         # project_working_dir, thampi_req_file, project_name = setup_working_directory(a_uuid, environment, data)
#         # commands = '''
#         #     marol_venv/bin/python ./handler_python3.py --execution_uuid {ex_uuid}
#         #     '''.format(ex_uuid=str(execution_uuid))
#         venv = f"venv-{a_uuid}"
#         # commands = [
#         #     f'cd {project_working_dir}',
#         #     f'virtualenv -p python3 {venv}',
#         #     f'source {venv}/bin/activate',
#         #     'pip3 install pip==9.0.3 && pip install zappa==0.45.1',
#         #     f'pip3 install -r {thampi_req_file}',
#         #     f'FLASK_APP=thampi-app.py FLASK_DEBUG=1 python -m flask run'
#         # ]
#         # command_str = ' && '.join(commands)
#         # from subprocess import PIPE, Popen
#         # p = Popen('/bin/bash', shell=True, bufsize=0, stdin=PIPE, stdout=PIPE, stderr=PIPE, close_fds=True,
#         #           universal_newlines=True)
#         # stdout, stderr = p.communicate(command_str)
#         # for line in stdout:
#         #     print(">>> " + str(line.rstrip()))
#         #     p.stdout.flush()
#         #
#         # for line in stderr:
#         #     print(">>> " + str(line.rstrip()))
#         #     p.stderr.flush()
#         pass
#     else:
#         project_name = get_project_name(environment, zappa_settings)
#         project_working_dir, thampi_req_file = setup_working_directory(a_uuid, project_name)
#         zappa_action = f'zappa deploy {environment}'
#         run_zappa_command_in_docker(a_uuid, project_name, project_working_dir, thampi_req_file, zappa_action)
#

def clean_up(environment, zappa_settings):
    project_home_path = determine_project_home_path(PROJECT_ENV_VARIABLE, DEFAULT_HOME)
    # file_name = constants.ZAPPA_FILE_NAME
    # zappa_settings = read_zappa(zappa_settings_file)
    project = get_project_name(environment, zappa_settings)
    base_path = project_home_path / project
    if base_path.exists():
        shutil.rmtree(str(base_path))
    os.makedirs(str(base_path))


def get_project_name(environment, zappa_settings):
    return zappa_settings[environment][constants.PROJECT_NAME]


def serve(environment: str,
          model_file: str,
          name: str,
          version: str,
          training_time_utc: datetime = None,
          instance_id: str = None,
          dependency_file: str = None,
          zappa_settings_file: str = None,
          project_dir: str = None,
          docker_run=None,
          setup_working_dir=None,
          clean_up_func=None,
          uuid_str_func=None,
          aws_module=None,
          project_exists_func=None,
          now_func=None
          ):
    docker_run = docker_run or run_zappa_command_in_docker
    setup_working_dir = setup_working_dir or setup_working_directory
    clean_up_func = clean_up_func or clean_up
    uuid_str_func = uuid_str_func or util.uuid
    aws_module = aws_module or aws
    project_exists_func = project_exists_func or project_exists
    now_func = now_func or util.utc_now_str

    zappa_settings_p = zappa_settings_file or default_zappa_settings_path()
    zappa_settings = read_zappa(zappa_settings_p)

    clean_up_func(DEV_ENVIRONMENT, zappa_settings)

    a_uuid = uuid_str_func()

    project_name = zappa_settings[environment][constants.PROJECT_NAME]
    bucket = zappa_settings[environment][ZAPPA_BUCKET]
    region_name = zappa_settings[environment][AWS_REGION]

    properties = dict(name=name,
                      version=version,
                      training_time_utc=str(training_time_utc) if training_time_utc else now_func(),
                      instance_id=instance_id or uuid_str_func())

    stream = json.dumps(properties)
    aws_module.create_bucket(bucket)
    aws_module.upload_stream_to_s3(stream, bucket, properties_key(environment, project_name))

    key = model_key(environment, project_name)
    aws_module.upload_to_s3(model_file, bucket, key)

    project_working_dir, thampi_req_file = setup_working_dir(a_uuid, project_name, dependency_file, project_dir)
    if not project_exists_func(environment, project_name, region_name):
        # if not project_exists(environment, project_name, region_name):
        deploy_action = f'zappa deploy {environment}'
        docker_run(a_uuid, project_name, project_working_dir, thampi_req_file, deploy_action)
    else:
        zappa_action = f'zappa update {environment}'
        docker_run(a_uuid, project_name, project_working_dir, thampi_req_file, zappa_action)


def default_zappa_settings_path():
    return zappa_settings_path(constants.ZAPPA_FILE_NAME)


# def serve(environment: str, model: str):
#     zappa_settings = read_zappa(constants.ZAPPA_FILE_NAME)
#     a_uuid = str(uuid.uuid4())
#     project_working_dir, thampi_req_file, project_name = setup_working_directory(a_uuid, environment, zappa_settings)

# (thampi-env) ➜  thampi PYTHONPATH=. python thampi/cli/cli.py predict staging   --args a=1,b=2,c=33
def predict(environment: str, args: Dict) -> Dict:
    import sys
    zappa_settings = read_zappa(default_zappa_settings_path())
    project_name = zappa_settings[environment][constants.PROJECT_NAME]
    region_name = zappa_settings[environment][constants.REGION]
    a_lambda_name = lambda_name(environment, project_name)

    # TODO: get api url for project/environment
    url = get_api_url(a_lambda_name, environment, region_name)
    predict_url = url + '/' + project_name + '/' + 'predict'
    headers = {"Content-type": "application/json"}
    try:
        result = requests.post(predict_url, headers=headers, data=json.dumps(args))
        result.raise_for_status()
        return result.json()
    except requests.exceptions.RequestException as e:  # This is the correct syntax
        print(e)
        print(f"Run 'zappa tail {environment} --since=3m' to see recent error logs.")
        sys.exit(1)


def lambda_name(environment, project_name):
    return slugify.slugify(project_name + '-' + environment)


def info(environment: str) -> Dict:
    zappa_settings = read_zappa(default_zappa_settings_path())
    project_name = zappa_settings[environment][constants.PROJECT_NAME]
    region_name = zappa_settings[environment][constants.REGION]
    lambda_name = slugify.slugify(project_name + '-' + environment)

    # TODO: get api url for project/environment
    url = get_api_url(lambda_name, environment, region_name)
    predict_url = url + '/' + project_name + '/' + 'predict'
    return dict(url=predict_url)


def get_api_url(lambda_name, stage_name, region_name):
    """
    Given a lambda_name and stage_name, return a valid API URL.
    """
    api_id = get_api_id(lambda_name, region_name)
    if api_id:
        return "https://{}.execute-api.{}.amazonaws.com/{}".format(api_id, region_name, stage_name)
    else:
        return None


def get_api_id(lambda_name, region_name):
    """
    Given a lambda_name, return the API id.
    """
    cf_client = aws.client('cloudformation', dict(region_name=region_name))
    response = cf_client.describe_stack_resource(StackName=lambda_name, LogicalResourceId='Api')
    return response['StackResourceDetail'].get('PhysicalResourceId', None)
    # try:
    #     cf_client = aws.client('cloudformation', dict(region_name=region_name))
    #     response = cf_client.describe_stack_resource(StackName=lambda_name, LogicalResourceId='Api')
    #     return response['StackResourceDetail'].get('PhysicalResourceId', None)
    # except:  # pragma: no cover
    #     # try:
    #     #     # Try the old method (project was probably made on an older, non CF version)
    #     #     response = self.apigateway_client.get_rest_apis(limit=500)
    #     #
    #     #     for item in response['items']:
    #     #         if item['name'] == lambda_name:
    #     #             return item['id']
    #     #
    #     #     logger.exception('Could not get API ID.')
    #     #     return None
    #     # except:  # pragma: no cover
    #     #     # We don't even have an API deployed. That's okay!
    #     #     return None
    #     pass


def get_bucket(environment: str) -> str:
    zappa_settings = read_zappa(default_zappa_settings_path())
    return zappa_settings[environment][ZAPPA_BUCKET]


def model_key(environment: str, project_name: str) -> str:
    return aws.s3_key(THAMPI, environment, project_name, 'model', 'current', 'model.pkl')


def properties_key(environment: str, project_name: str) -> str:
    return aws.s3_key(THAMPI, environment, project_name, 'model', 'current', THAMPI + '.json')


# def model_path(environment: str, project_name: str) -> str:
#     return aws.s3_key(thampi, environment, project_name, 'model', 'current', 'model.pkl')


def run_zappa_command_in_docker(a_uuid: str, project_name, project_working_dir, thampi_req_file, zappa_action):
    # project_working_dir, thampi_req_file, project_name = setup_working_directory(a_uuid, environment, zappa_settings)

    src = Path(SRC_PATH)
    requirements_file_path = src / thampi_req_file
    volume_bindings = {
        project_working_dir: {
            'bind': SRC_PATH,
            'mode': 'rw',
        },
    }
    venv = f"venv-{a_uuid}"
    commands = [
        'export LC_ALL=en_US.UTF-8',
        'export LANG=en_US.UTF-8',
        f'cp -r ./.aws /root',  # and delete it as if we keep it here, it will be zipped into the code zip
        'cd /tmp',
        'mkdir thampi && cd thampi',
        f'mkdir {project_name} && cd {project_name}',
        f'cd /var/runtime && rm -rf dateutil python_dateutil*.dist-info/ && cd -',
        f'virtualenv {venv}',
        f'source {venv}/bin/activate',
        'pip install pip==9.0.3 && pip install zappa==0.45.1',
        f'pip install -r {requirements_file_path}',
        f'cd {SRC_PATH}',
        'find . -name __pycache__ -type d -exec rm -rf {} +',
        "find . -name '*.pyc' -delete",
        zappa_action
    ]
    command_str = ' && '.join(commands)
    command_line = ['sh', '-c', command_str]
    client = docker.from_env()
    c = client.containers.run(image=LAMBDA_IMAGE,
                              command=command_line,
                              volumes=volume_bindings,
                              stderr=True,
                              remove=True,
                              working_dir=SRC_PATH)
    print('-Logs-')
    logs = c
    pprint(logs.decode().split('\n'))
    # TODO: set project_working_dir as working_dir for docker
    # TODO: Delete credentials and other files after deploy


def setup_working_directory(a_uuid, project_name, dependency_file: str = None, project_dir: str = None):
    flask_api_file = Path(core.__path__[0]) / constants.FLASK_FILE

    thampi_req_file = thampi_req_file_name(a_uuid)
    tmp_dep_path = f'/tmp/{thampi_req_file}'
    if dependency_file:
        dep_path = Path(dependency_file)
    else:
        dep_path = Path(tmp_dep_path)
        save_dependencies(dep_path)

    # TODO: This is temporary, remove the remove_thampi method!
    # remove_thampi(dep_path)
    project_home_path = determine_project_home_path(PROJECT_ENV_VARIABLE, DEFAULT_HOME)
    # TODO: Duplication below with thampi_init
    # project_name = get_project_name(environment)
    # zappa_settings = read_zappa(constants.ZAPPA_FILE_NAME)
    # project_name = zappa_settings[environment][constants.PROJECT_NAME]
    project_working_dir = project_home_path / project_name / a_uuid

    p_path = project_dir or os.getcwd()
    cwd = Path(p_path)
    shutil.copytree(cwd, project_working_dir)
    home = home_path()
    dest = project_working_dir / AWS_FOLDER
    src = f'{home}/{AWS_FOLDER}'
    shutil.copytree(src, dest)
    shutil.copyfile(dep_path, os.path.join(project_working_dir, thampi_req_file))
    shutil.copyfile(flask_api_file, project_working_dir / constants.THAMPI_APP_FILE)

    if not dependency_file:
        dep_path.unlink()
    return project_working_dir, thampi_req_file


def thampi_req_file_name(a_uuid):
    return f'thampi-requirements-{a_uuid}'


# def get_project_name(environment):
#     data = read_zappa(constants.ZAPPA_FILE_NAME)
#     project_name = data[environment][PROJECT_NAME]
#     return project_name


def read_zappa(zappa_file_path):
    return read_zappa_settings(Path(zappa_file_path))


def zappa_settings_path(file_name):
    cwd = Path(os.getcwd())
    return cwd / file_name


def determine_project_home_path(project_env_variable: str, default_home: str) -> Path:
    if project_env_variable not in os.environ:
        path = os.path.join(home_path(), default_home)
    else:
        path = os.environ[project_env_variable]

    os.makedirs(path, exist_ok=True)
    return Path(path)


def home_path():
    if 'HOME' in os.environ:
        path = os.environ['HOME']
    else:
        path = os.path.expanduser('~')
    return path


# def check_venv(self):
#     """ Ensure we're inside a virtualenv. """
#     if self.zappa:
#         venv = self.zappa.get_current_venv()
#     else:
#         # Just for `init`, when we don't have settings yet.
#         venv = Zappa.get_current_venv()
#     if not venv:
#         raise ClickException(
#             click.style("Zappa", bold=True) + " requires an " + click.style("active virtual environment",
#                                                                             bold=True, fg="red") + "!\n" +
#             "Learn more about virtual environments here: " + click.style(
#                 "http://docs.python-guide.org/en/latest/dev/virtualenvs/", bold=False, fg="cyan"))


def check_venv():
    """ Ensure we're inside a virtualenv. """

    # Just for `init`, when we don't have settings yet.
    venv = get_current_venv()
    if not venv:
        raise ValueError('Need a virtual environment to be activate first')


def get_current_venv():
    """
    Returns the path to the current virtualenv
    """
    if 'VIRTUAL_ENV' in os.environ:
        venv = os.environ['VIRTUAL_ENV']
    elif os.path.exists('.python-version'):  # pragma: no cover
        try:
            subprocess.check_output('pyenv help', stderr=subprocess.STDOUT)
        except OSError:
            print("This directory seems to have pyenv's local venv, "
                  "but pyenv executable was not found.")
        with open('.python-version', 'r') as f:
            # minor fix in how .python-version is read
            # Related: https://github.com/Miserlou/Zappa/issues/921
            env_name = f.readline().strip()
        bin_path = subprocess.check_output(['pyenv', 'which', 'python']).decode('utf-8')
        venv = bin_path[:bin_path.rfind(env_name)] + env_name
    else:  # pragma: no cover
        return None

    return venv


def settings(all_config):
    return dicts(all_config, THAMPI_ZAPPA_SETTINGS)


def project_exists(environment: str, project_name: str, region_name: str) -> bool:
    lambda_client = aws.client('lambda', dict(region_name=region_name))
    try:
        lambda_client.get_function(FunctionName=lambda_name(environment, project_name))
        return True
    except lambda_client.exceptions.ResourceNotFoundException as ex:
        return False


if __name__ == '__main__':
    from thampi.lib import aws
    from pprint import pprint

    # ['__class__', '__copy__', '__deepcopy__', '__delattr__', '__dir__', '__doc__', '__eq__', '__format__', '__ge__', '__getattribute__', '__gt__', '__hash__', '__init__', '__init_subclass__', '__le__', '__lt__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__', 'findall', 'finditer', 'flags', 'fullmatch', 'groupindex', 'groups', 'match', 'pattern', 'scanner', 'search', 'split', 'sub', 'subn']
    print(name_pattern.pattern)
