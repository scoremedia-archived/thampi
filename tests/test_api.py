import unittest
from thampi.core import api
from unittest.mock import MagicMock
import json
from pathlib import Path

AWS_REGION = "us-east-1"

S3_BUCKET = "zappa-thampi-trial"


class MyTestCase(unittest.TestCase):
    def test_serve(self):
        # Given
        environment = 'dev'
        project_name = "thampi-trial"
        project_dir = '/project_dir'
        dependency_file = '/tmp/req.txt'
        zappa_settings_path = '/tmp/thampi_test_settings.json'
        a_uuid = 'abc_uuid'
        thampi_req_file = api.thampi_req_file_name(a_uuid)
        model_date = '2018-07-25T21:39:58.910578'
        instance_id = 'a_instance_id'
        model_dir = '/tmp/no_model'

        thampi_working_dir = '/tmp/project_dir'

        data = {"dev": {
            "s3_bucket": S3_BUCKET,
            "project_name": project_name,
            "aws_region": AWS_REGION,
        }

        }
        with open(zappa_settings_path, 'w') as f:
            json.dump(data, f)

        now_func = lambda: model_date
        docker_run = MagicMock()
        setup_working_dir = MagicMock(return_value=(thampi_working_dir, thampi_req_file))
        clean_up_func = MagicMock()
        uuid_str_func = MagicMock(return_value=a_uuid)
        aws_module = MagicMock()
        project_exists_func = MagicMock(return_value=True)
        read_properties_func = MagicMock(return_value=dict(instance_id=instance_id))

        # When
        api.serve(environment,
                  model_dir,
                  dependency_file,
                  zappa_settings_file=zappa_settings_path,
                  project_dir=project_dir,
                  docker_run_func=docker_run,
                  setup_working_dir_func=setup_working_dir,
                  clean_up_func=clean_up_func,
                  uuid_str_func=uuid_str_func,
                  aws_module=aws_module,
                  project_exists_func=project_exists_func,
                  now_func=now_func,
                  read_properties_func=read_properties_func)

        # Then
        setup_working_dir.assert_called_once_with(a_uuid, project_name, dependency_file, project_dir)

        clean_up_func.assert_called_once_with(environment, data)

        aws_module.create_bucket.assert_called_once_with(S3_BUCKET)
        from thampi.core import helper
        aws_module.upload_to_s3.assert_called_once_with(helper.model_path(model_dir), S3_BUCKET,
                                                        f'thampi/{environment}/{project_name}/model/current/model.pkl')

        stream = f'{{"instance_id": "{instance_id}", "utc_time_served": "{model_date}"}}'

        aws_module.upload_stream_to_s3.assert_called_once_with(stream, S3_BUCKET,
                                                               f'thampi/{environment}/{project_name}/model/current/thampi.json')
        docker_run.assert_called_once_with(a_uuid=a_uuid,
                                           project_name=project_name,
                                           project_working_dir=thampi_working_dir,
                                           thampi_req_file=thampi_req_file,
                                           zappa_action=f'zappa update {environment}',
                                           zappa_settings=data['dev'])
        project_exists_func.assert_called_once_with(environment, project_name, AWS_REGION)

        # Cleanup
        Path(zappa_settings_path).unlink()


if __name__ == '__main__':
    unittest.main()
