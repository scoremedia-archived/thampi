from pathlib import Path
from typing import Dict, Callable, List

from thampi import core
from thampi.core import constants
from thampi.core.model import Model
from thampi.core import helper
import json
from thampi.lib import util
from thampi.lib import aws
from thampi.lib.util import dicts
import subprocess
import docker
from functools import partial

import shutil
import requests
import slugify
import datetime
import cloudpickle
import os

import re

PIP = 'pip'
CONDA = 'conda'
DEV_ENVIRONMENT = 'dev'

AWS_REGION = 'aws_region'

PROJECT_ENV_VARIABLE = 'THAMPI_HOME'

DEFAULT_HOME = '.cache/thampi'

THAMPI_ZAPPA_SETTINGS = dict(keep_warm=True,
                             memory_size=3008,
                             slim_handler=True,
                             timeout_seconds=300)

AWS_FOLDER = '.aws'
SSH_FOLDER = '.ssh'
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

    with open(helper.default_zappa_settings_path(), 'w') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def check_init_variant(zappa_settings_path: str = None):
    zappa_settings_path = zappa_settings_path or os.path.join(os.getcwd(), constants.ZAPPA_FILE_NAME)
    zappa_file = Path(zappa_settings_path)

    if zappa_file.exists():
        raise ValueError(f'{constants.ZAPPA_FILE_NAME} already exists. Delete it and run again.')


def init(all_config: Dict):
    thampi_init(all_config)


def save_dependencies(path: Path):
    check_venv()
    subprocess.run(f'pip freeze > {str(path)}', shell=True)


def remove_thampi(tmp_file):
    with open(tmp_file, 'r') as f:
        lines = f.readlines()

    result = []
    for l in lines:
        if not l.startswith('thampi=='):
            result.append(l)

    with open(tmp_file, 'w') as f:
        f.writelines(result)


# def remove_thampi(tmp_file):
#     with open(tmp_file, 'r') as f:
#         lines = f.readlines()
#     thampi_line = 'thampi==0.1.0\n'
#     if thampi_line in lines:
#         lines.remove(thampi_line)
#
#     with open(tmp_file, 'w') as f:
#         f.writelines(lines)


def clean_up(environment, zappa_settings):
    base_path = working_project_directory(environment, zappa_settings)
    if base_path.exists():
        shutil.rmtree(str(base_path))
    os.makedirs(str(base_path))


def working_project_dir(environment=DEV_ENVIRONMENT, zappa_settings_file=None):
    zappa_settings = read_zappa_file(zappa_settings_file)
    return working_project_directory(environment, zappa_settings)


def project_home():
    return determine_project_home_path(PROJECT_ENV_VARIABLE, DEFAULT_HOME)


def s3_bucket(environment=DEV_ENVIRONMENT, zappa_settings_file=None):
    zappa_settings = read_zappa_file(zappa_settings_file)
    return zappa_settings[environment]['s3_bucket']


def s3_project_prefix(environment=DEV_ENVIRONMENT, zappa_settings_file=None):
    zappa_settings = read_zappa_file(zappa_settings_file)
    project_name = zappa_settings[environment]['project_name']
    environments = '{' + ",".join(list(zappa_settings.keys())) + '}'
    return f"{constants.THAMPI}/{environments}/{project_name}"


def s3_project_prefix_list(environment=DEV_ENVIRONMENT, zappa_settings_file=None):
    zappa_settings = read_zappa_file(zappa_settings_file)
    project_name = zappa_settings[environment]['project_name']

    environments = zappa_settings.keys()
    result = []
    for e in environments:
        result.append(f"{constants.THAMPI}/{e}/{project_name}")

    return result


def working_project_directory(environment, zappa_settings):
    project_home_path = determine_project_home_path(PROJECT_ENV_VARIABLE, DEFAULT_HOME)
    # file_name = constants.ZAPPA_FILE_NAME
    # zappa_settings = read_zappa(zappa_settings_file)
    project = get_project_name(environment, zappa_settings)
    base_path = project_home_path / project
    return base_path


def get_project_name(environment, zappa_settings):
    return zappa_settings[environment][constants.PROJECT_NAME]


def save(model: Model,
         name: str,
         path: str = None,
         trained_time_utc: datetime.datetime = None,
         instance_id: str = None,
         tags: Dict = None,
         now_func: Callable[[], datetime.datetime] = None,
         uuid_str_func: Callable[[], str] = None):
    now_func = now_func or util.utc_now_str
    uuid_str_func = uuid_str_func or util.uuid

    path = path or os.getcwd()
    model_dir = os.path.join(path, name)

    os.makedirs(model_dir, exist_ok=True)

    with open(helper.model_path(model_dir), "wb") as f:
        cloudpickle.dump(model, f)

    opts = util.optional(tags=tags)
    fixed = dict(trained_time_utc=trained_time_utc.isoformat() if trained_time_utc else now_func(),
                 instance_id=instance_id or uuid_str_func())
    meta = dict(thampi_data_version='0.1')
    properties = util.dicts(meta, fixed, opts)

    with open(helper.properties_path(model_dir), "w") as f:
        json.dump(properties, f, indent=4, ensure_ascii=False)


def serve(environment: str,
          model_dir: str,
          dependency_file: str,
          zappa_settings_file: str = None,
          project_dir: str = None,
          served_time_utc: datetime.datetime = None,
          docker_run_func=None,
          setup_working_dir_func=None,
          clean_up_func=None,
          uuid_str_func=None,
          aws_module=None,
          project_exists_func=None,
          now_func=None,
          read_properties_func: Callable[[str], Dict] = None
          ):
    project_working_dir = None
    check_environment_provided(environment=environment)
    docker_run_func = docker_run_func or run_zappa_command_in_docker
    setup_working_dir_func = setup_working_dir_func or setup_working_directory
    clean_up_func = clean_up_func or clean_up
    uuid_str_func = uuid_str_func or util.uuid
    aws_module = aws_module or aws
    project_exists_func = project_exists_func or helper.project_exists
    now_func = now_func or util.utc_now_str
    read_properties_func = read_properties_func or read_properties
    served_time_utc = served_time_utc.isoformat() if served_time_utc else now_func()

    zappa_settings = read_zappa_file(zappa_settings_file)

    clean_up_func(DEV_ENVIRONMENT, zappa_settings)

    a_uuid = uuid_str_func()

    project_name = zappa_settings[environment][constants.PROJECT_NAME]
    bucket = zappa_settings[environment][constants.ZAPPA_BUCKET]
    region_name = zappa_settings[environment][AWS_REGION]

    aws_module.create_bucket(bucket)

    training_properties = read_properties_func(model_dir)

    properties = dict(training_properties, served_time_utc=served_time_utc)
    stream = json.dumps(properties)
    aws_module.upload_stream_to_s3(stream, bucket, helper.properties_key(environment, project_name))

    model_key = helper.model_key(environment, project_name)
    aws_module.upload_to_s3(helper.model_path(model_dir), bucket, model_key)

    try:
        project_working_dir, thampi_req_file = setup_working_dir_func(a_uuid, project_name, dependency_file,
                                                                      project_dir)
        docker_run_command = partial(docker_run_func,
                                     a_uuid=a_uuid,
                                     project_name=project_name,
                                     project_working_dir=project_working_dir,
                                     thampi_req_file=thampi_req_file,
                                     zappa_settings=zappa_settings[environment])

        if not project_exists_func(environment, project_name, region_name):
            # if not project_exists(environment, project_name, region_name):
            deploy_action = f'zappa deploy {environment}'
            docker_run_command(zappa_action=deploy_action)
        else:
            update_action = f'zappa update {environment}'
            docker_run_command(zappa_action=update_action)
    finally:
        if project_working_dir:
            shutil.rmtree(project_working_dir)


def clean(scope: str):
    if scope == 'project':
        clean_project()
    elif scope == 'all':
        clean_all()


def clean_all():
    project_dir = project_home()
    if os.path.isdir(project_dir):
        shutil.rmtree(project_dir)


def clean_project(environment=DEV_ENVIRONMENT, zappa_settings_file=None):
    a_dir = working_project_dir()
    if os.path.isdir(a_dir):
        shutil.rmtree(a_dir)
    bucket = s3_bucket()
    for p in s3_project_prefix_list(environment, zappa_settings_file):
        aws.delete_prefix(bucket, p)


def read_zappa_file(zappa_settings_file):
    zappa_settings_p = zappa_settings_file or helper.default_zappa_settings_path()
    zappa_settings = helper.read_zappa(zappa_settings_p)
    return zappa_settings


def read_properties(model_dir):
    with open(helper.properties_path(model_dir)) as f:
        training_properties = json.load(f)
    return training_properties


# def serve(environment: str, model: str):
#     zappa_settings = read_zappa(constants.ZAPPA_FILE_NAME)
#     a_uuid = str(uuid.uuid4())
#     project_working_dir, thampi_req_file, project_name = setup_working_directory(a_uuid, environment, zappa_settings)

# (thampi-env) ➜  thampi PYTHONPATH=. python thampi/cli/cli.py predict staging   --args a=1,b=2,c=33
def predict(environment: str, data: Dict) -> Dict:
    import sys
    zappa_settings = helper.read_zappa(helper.default_zappa_settings_path())
    project_name = zappa_settings[environment][constants.PROJECT_NAME]
    region_name = zappa_settings[environment][constants.REGION]
    a_lambda_name = helper.lambda_name(environment, project_name)

    # TODO: get api url for project/environment
    url = helper.get_api_url(a_lambda_name, environment, region_name)
    predict_url = url + '/' + project_name + '/' + 'predict'
    headers = {"Content-type": "application/json"}
    try:
        result = requests.post(predict_url, headers=headers, data=json.dumps(dict(data=data)))
        result.raise_for_status()
        return result.json()
    except requests.exceptions.RequestException as e:  # This is the correct syntax
        print(e)
        print(f"Run 'zappa tail {environment} --since=3m' to see recent error logs.")
        sys.exit(1)


def info(environment: str) -> Dict:
    zappa_settings = helper.read_zappa(helper.default_zappa_settings_path())
    project_name = zappa_settings[environment][constants.PROJECT_NAME]
    region_name = zappa_settings[environment][constants.REGION]
    lambda_name = slugify.slugify(project_name + '-' + environment)

    # TODO: get api url for project/environment
    url = helper.get_api_url(lambda_name, environment, region_name)
    predict_url = url + '/' + project_name + '/' + 'predict'
    return dict(url=predict_url)


# def model_path(environment: str, project_name: str) -> str:
#     return aws.s3_key(thampi, environment, project_name, 'model', 'current', 'model.pkl')


def run_zappa_command_in_docker(a_uuid: str, project_name: str, project_working_dir, thampi_req_file,
                                zappa_settings,
                                zappa_action):
    venv = f"venv-{a_uuid}"
    package_manager = zappa_settings[constants.THAMPI]['package_manager']
    src = Path(SRC_PATH)
    requirements_file_path = src / thampi_req_file
    install_prerequisites = 'pip install pip==9.0.3'
    install_post = 'pip install zappa==0.45.1 && pip install Flask==0.12.4 && pip install cloudpickle'
    conda_commands = [
        'unset PYTHONPATH',
        'curl https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh --output /tmp/miniconda_installer.sh',
        'bash /tmp/miniconda_installer.sh -b',
        '/root/miniconda3/bin/conda create --name docker-conda python=3.6 -y',
        'source /root/miniconda3/bin/activate docker-conda',
        install_prerequisites,
        f'/root/miniconda3/bin/conda env update -n docker-conda --file {requirements_file_path}',
        install_post,
        'export VIRTUAL_ENV=$CONDA_PREFIX'
    ]

    pip_commands = [
        f'virtualenv {venv}',
        f'source {venv}/bin/activate',
        install_prerequisites,
        f'pip install -r {requirements_file_path}',
        install_post

    ]

    packager_commands = conda_commands if package_manager == CONDA else pip_commands
    volume_bindings = {
        project_working_dir: {
            'bind': SRC_PATH,
            'mode': 'rw',
        },
    }

    setup = ['export LC_ALL=en_US.UTF-8',
             'export LANG=en_US.UTF-8',
             'mv ./.aws /root',  # TODO: and delete it as if we keep it here, it will be zipped into the code zip
             'cd /tmp',
             'mkdir thampi && cd thampi',
             f'mkdir {project_name} && cd {project_name}',
             f'cd /var/runtime && rm -rf dateutil python_dateutil*.dist-info/ && cd -']

    post = [f'cd {SRC_PATH}',
            'find . -name __pycache__ -type d -exec rm -rf {} +',
            "find . -name '*.pyc' -delete",
            zappa_action]
    commands = setup + packager_commands + post
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
    from pprint import pprint
    pprint(logs.decode().split('\n'))


def setup_working_directory(a_uuid, project_name, dependency_file: str, project_dir: str = None):
    flask_api_file = Path(core.__path__[0]) / constants.FLASK_FILE

    thampi_req_file = thampi_req_file_name(a_uuid)

    dep_path = Path(dependency_file)
    # TODO: This is temporary, remove the remove_thampi method!
    remove_thampi(dep_path)
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
    dest_aws = project_working_dir / AWS_FOLDER
    src_aws = f'{home}/{AWS_FOLDER}'
    shutil.copytree(src_aws, dest_aws)

    dest_thampi = project_working_dir / constants.THAMPI
    src_thampi = util.parent_dir(__file__)
    shutil.copytree(src_thampi, dest_thampi)

    # Remove unnecessary files/folders
    api_file = Path(os.path.join(dest_thampi, 'core', 'api.py'))
    cli_dir = os.path.join(dest_thampi, 'cli')
    init_file = Path(os.path.join(dest_thampi, '__init__.py'))

    api_file.unlink()
    shutil.rmtree(cli_dir)
    init_file.unlink()
    init_file.touch()

    shutil.copyfile(dep_path, os.path.join(project_working_dir, thampi_req_file))
    shutil.copyfile(flask_api_file, project_working_dir / constants.THAMPI_APP_FILE)

    if not dependency_file:
        dep_path.unlink()
    return project_working_dir, thampi_req_file


def thampi_req_file_name(a_uuid):
    return f'thampi-requirements-{a_uuid}'


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


def default_package_manager() -> str:
    return PIP


def supported_package_manager() -> List[str]:
    return [CONDA, PIP]


def check_environment_provided(environment: str):
    if not environment:
        raise ValueError('Environment required. Refer to docs.')
