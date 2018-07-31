from typing import Tuple
import boto3
import io


def split_s3_path(path: str) -> Tuple[str, str]:
    truncated_path = None
    prefix = "s3://"
    if path.startswith(prefix):
        truncated_path = path[len(prefix):]
    splits = truncated_path.split('/', 1)
    return splits[0], splits[1]


# def load_s3_object(bucket, key):
#     # TODO: Refactor this taking inspiration from util.load_object so that load_model_info_from_s3 looks like load_model_info
#
#     io_obj = get_byte_stream_from_s3(bucket, key)
#     with io_obj as input_file:
#         new_object = dill.load(input_file)
#     return new_object


def load_s3_object(bucket, key):
    # TODO: Refactor this taking inspiration from util.load_object so that load_model_info_from_s3 looks like load_model_info
    import pickle
    # >> > new_squared = pickle.loads(pickled_lambda)
    io_obj = get_byte_stream_from_s3(bucket, key)
    with io_obj as f:
        result = pickle.load(f)

    return result


def get_byte_stream_from_s3(bucket, key):
    s3_obj = get_s3_object(bucket, key)
    io_obj = io.BytesIO(s3_obj)
    return io_obj


def get_s3_object(bucket, key):
    s3 = resource('s3')
    response = s3.Object(bucket, key).get()
    return response['Body'].read()


def client(service_name, config=None):
    return boto3.client(service_name, **config)


def resource(resource_name):
    session = boto3.session.Session()
    return session.resource(resource_name)


def s3_key(*keys):
    return '/'.join(keys)


def upload_to_s3(path, bucket, key):
    s3 = resource('s3')
    with open(path, 'rb') as data:
        s3.Bucket(bucket).put_object(Key=key, Body=data)


def upload_stream_to_s3(stream, bucket, key):
    s3 = resource('s3')
    s3.Object(bucket, key).put(Body=stream)


def create_bucket(bucket: str):
    s3 = resource('s3')
    s3.create_bucket(Bucket=bucket)


def get_api_id(lambda_name, region_name):
    """
    Given a lambda_name, return the API id.
    """
    cf_client = client('cloudformation', dict(region_name=region_name))
    response = cf_client.describe_stack_resource(StackName=lambda_name, LogicalResourceId='Api')
    return response['StackResourceDetail'].get('PhysicalResourceId', None)


