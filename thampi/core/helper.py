from thampi.lib import aws
from pathlib import Path
from typing import Dict
import json
from thampi.core import constants
import slugify
import os


def zappa_settings_path(file_name):
    cwd = Path(os.getcwd())
    return cwd / file_name


def default_zappa_settings_path():
    return zappa_settings_path(constants.ZAPPA_FILE_NAME)


def read_zappa_settings(zappa_settings_path: Path) -> Dict[str, Dict[str, str]]:
    if not zappa_settings_path.is_file():
        raise ValueError(
            f"Expect {zappa_settings_path} to be in the current working directory. Run 'thampi init' first.")

    with zappa_settings_path.open() as f:
        return json.load(f)


def read_zappa(zappa_file_path):
    return read_zappa_settings(Path(zappa_file_path))


def get_bucket(environment: str) -> str:
    zappa_settings = read_zappa(default_zappa_settings_path())
    return zappa_settings[environment][constants.ZAPPA_BUCKET]


def model_key(environment: str, project_name: str) -> str:
    return aws.s3_key(*[constants.THAMPI, environment, project_name] + ['model', 'current', 'model.pkl'])


def properties_key(environment: str, project_name: str) -> str:
    return aws.s3_key(*[constants.THAMPI, environment, project_name] + ['model', 'current', constants.PROPERTIES_FILE])


def project_exists(environment: str, project_name: str, region_name: str) -> bool:
    lambda_client = aws.client('lambda', dict(region_name=region_name))
    try:
        lambda_client.get_function(FunctionName=lambda_name(environment, project_name))
        return True
    except lambda_client.exceptions.ResourceNotFoundException as ex:
        return False


def lambda_name(environment, project_name):
    return slugify.slugify(project_name + '-' + environment)


def get_api_url(lambda_name, stage_name, region_name):
    """
    Given a lambda_name and stage_name, return a valid API URL.
    """
    api_id = aws.get_api_id(lambda_name, region_name)
    if api_id:
        return "https://{}.execute-api.{}.amazonaws.com/{}".format(api_id, region_name, stage_name)
    else:
        return None


def model_path(model_dir: str) -> str:
    return os.path.join(model_dir, constants.MODEL_FILE)


def properties_path(model_dir: str) -> str:
    return os.path.join(model_dir, constants.PROPERTIES_FILE)
