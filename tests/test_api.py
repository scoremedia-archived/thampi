import unittest
from thampi.core import api
from unittest.mock import MagicMock
import json
from pathlib import Path

AWS_REGION = "us-east-1"

S3_BUCKET = "zappa-thampi-trial"


def dummy_working_dir(a_uuid, project_name, dep_file, project_dir):
    print(f'Setup Working Dir, uuid:{a_uuid}, project:{project_name}, dep_file:{dep_file}, project:{project_dir}')
    return '/tmp/project_dir', dep_file


def dummy_clean_up(env, zappa_settings):
    print(f'Dummy Clean Up, env:{env}, zappa_settings:{zappa_settings}')


def dummy_docker_run(a_uuid, project_name, project_working_dir, thampi_req_file, zappa_action):
    print(
        f'Docker Run, uuid:{a_uuid}, project:{project_name}, project dir:{project_working_dir}, dep_file:{thampi_req_file},zappa_action:{zappa_action} ')


class MyTestCase(unittest.TestCase):
    def test_serve(self):
        # Given
        environment = 'dev'
        project_name = "thampi-trial"
        project_dir = '/project_dir'
        req_file = '/tmp/req.txt'
        zappa_settings_path = '/tmp/thampi_test_settings.json'
        a_uuid = 'abc_uuid'
        thampi_req_file = api.thampi_req_file_name(a_uuid)

        model_name = 'test_name'
        model_version = 'test_version'
        model_date = '2018-07-25T21:39:58.910578'
        instance_id = 'a_instance_id'
        model_path = '/tmp/no_model.pkl'

        thampi_working_dir = '/tmp/project_dir'

        data = {"dev": {
            "s3_bucket": S3_BUCKET,
            "project_name": project_name,
            "aws_region": AWS_REGION,
        }

        }
        with open(zappa_settings_path, 'w') as f:
            json.dump(data, f)

        now_func = None
        docker_run = MagicMock()
        setup_working_dir = MagicMock(return_value=(thampi_working_dir, thampi_req_file))
        clean_up_func = MagicMock()
        uuid_str_func = MagicMock(return_value=a_uuid)
        aws_module = MagicMock()
        project_exists_func = MagicMock(return_value=True)

        # When
        api.serve(environment, model_path, model_name, model_version, model_date, instance_id,
                  req_file, zappa_settings_path, project_dir, docker_run, setup_working_dir, clean_up_func,
                  uuid_str_func, aws_module, project_exists_func, now_func)

        # Then
        setup_working_dir.assert_called_once_with(a_uuid, project_name, req_file, project_dir)

        clean_up_func.assert_called_once_with(environment, data)

        aws_module.create_bucket.assert_called_once_with(S3_BUCKET)
        aws_module.upload_to_s3.assert_called_once_with(model_path, S3_BUCKET,
                                                        f'thampi/{environment}/{project_name}/model/current/model.pkl')
        stream = f'{{"name": "{model_name}", "version": "{model_version}", "training_time_utc": "{model_date}", "instance_id": "{instance_id}"}}'

        aws_module.upload_stream_to_s3.assert_called_once_with(stream, S3_BUCKET,
                                                               f'thampi/{environment}/{project_name}/model/current/thampi.json')
        docker_run.assert_called_once_with(a_uuid, project_name, thampi_working_dir, thampi_req_file,
                                           f'zappa update {environment}')
        project_exists_func.assert_called_once_with(environment, project_name, AWS_REGION)

        # Cleanup
        Path(zappa_settings_path).unlink()


if __name__ == '__main__':
    unittest.main()
