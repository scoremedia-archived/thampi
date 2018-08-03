import click
import sys
import random
import string
from thampi.core import api
from thampi.lib import util
from thampi.core import constants

BOTO3_CONFIG_DOCS_URL = 'https://boto3.readthedocs.io/en/latest/guide/quickstart.html#configuration'


@click.command()
def init():  # pragma: no cover
    """
    Main program execution handler.
    """

    '''
    "app_function": "x.app",
        "aws_region": "us-east-1",
        "profile_name": "default",
        "project_name": "thampi-client",
        "runtime": "python3.6",
        "s3_bucket": "zappa-rbf5gr7cc"
    '''
    core_dict = {"app_function": constants.THAMPI_APP,
                 "runtime": "python3.6"}
    try:
        # api.init()
        model_name = get_model_name()
        profile_name, profile_region = get_profile_name_and_region()
        bucket = get_bucket()
        package_manager = get_package_manager()
        # zappa_settings_filename = get_zappa_settings_filename(model_name)
        input_dict = dict(project_name=model_name, profile_name=profile_name, aws_region=profile_region,
                          s3_bucket=bucket, thampi=dict(package_manager=package_manager))
        all_config = util.dicts(core_dict, input_dict)
        api.init(all_config)
        click.echo(
            "A file zappa_settings.json has been created. If you made a mistake, delete it and run `thampi init` again")
    except SystemExit as e:  # pragma: no cover
        sys.exit(e.code)
    except KeyboardInterrupt:  # pragma: no cover
        sys.exit(130)
    except Exception as e:

        click.echo("Oh no! An " + click.style("error occurred", fg='red', bold=True) + "! :(")
        click.echo("\n==============\n")
        import traceback
        traceback.print_exc()
        click.echo("\n==============\n")

        sys.exit(-1)


def get_bucket():
    click.echo('------------')
    click.echo("\nYour Zappa deployments will need to be uploaded to a " + click.style("private S3 bucket",
                                                                                       bold=True) + ".")
    click.echo("If you don't have a bucket yet, we'll create one for you too.")
    default_bucket = "thampi-" + ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(9))
    bucket = input("What do you want to call your bucket? (default '%s'): " % default_bucket) or default_bucket
    return bucket


def get_profile_name_and_region():
    click.echo('-----------------')
    # Detect AWS profiles and regions
    # If anyone knows a more straightforward way to easily detect and parse AWS profiles I'm happy to change this, feels like a hack
    import botocore
    session = botocore.session.Session()
    config = session.full_config
    profiles = config.get("profiles", {})
    profile_names = list(profiles.keys())
    click.echo("\nAWS Lambda and API Gateway are only available in certain regions. " \
               "Let's check to make sure you have a profile set up in one that will work.")
    if not profile_names:
        profile_name, profile = None, None
        click.echo(
            "We couldn't find an AWS profile to use. Before using Zappa, you'll need to set one up. See here for more info: {}"
                .format(click.style(BOTO3_CONFIG_DOCS_URL, fg="blue", underline=True)))
    elif len(profile_names) == 1:
        profile_name = profile_names[0]
        profile = profiles[profile_name]
        click.echo("Okay, using profile {}!".format(click.style(profile_name, bold=True)))
    else:
        if "default" in profile_names:
            default_profile = [p for p in profile_names if p == "default"][0]
        else:
            default_profile = profile_names[0]

        while True:
            profile_name = input("We found the following profiles: {}, and {}. " \
                                 "Which would you like us to use? (default '{}'): "
                .format(
                ', '.join(profile_names[:-1]),
                profile_names[-1],
                default_profile
            )) or default_profile
            if profile_name in profiles:
                profile = profiles[profile_name]
                break
            else:
                click.echo("Please enter a valid name for your AWS profile.")
    profile_region = profile.get("region") if profile else None
    return profile_name, profile_region


def get_package_manager():
    click.echo('-----------------')
    default_manager = api.default_package_manager()
    supported_managers = api.supported_package_manager()
    while True:

        package_manager = input(
            f"Enter package manager:{supported_managers}(default: {default_manager}):") or default_manager
        if package_manager in supported_managers:
            return package_manager
        else:
            click.echo(f"Only {supported_managers} are supported")


def get_model_name():
    while True:
        click.echo("Welcome to Thampi!")
        click.echo('-------------')
        click.echo(
            "Enter Model Name. If your model name is 'mymodel', the predict endpoint will be myendpoint.com/mymodel/predict")
        model_name = input("What do you want to call your model: ")
        assert model_name, 'Model Name is required'
        try:
            api.match_str(model_name, api.name_pattern)
            break
        except ValueError:
            click.echo(click.style(f"Model Name must match {api.name_pattern.pattern}", fg="red"))
    return model_name


def get_zappa_settings_filename(model_name: str) -> str:
    click.echo('-------------')
    default_file_name = model_name + '_settings.json'
    file_name = input(f"Enter Zappa Settings File(default: {default_file_name}):") or default_file_name
    assert file_name, 'Settings file name required'

    return file_name


# @click.command()
# @click.argument('environment')
# def deploy(environment):  # pragma: no cover
#     """
#     Main program execution handler.
#     """
#     try:
#         api.deploy(environment)
#     except SystemExit as e:  # pragma: no cover
#         sys.exit(e.code)
#     except KeyboardInterrupt:  # pragma: no cover
#         sys.exit(130)
#     except Exception as e:
#
#         click.echo("Oh no! An " + click.style("error occurred", fg='red', bold=True) + "! :(")
#         click.echo("\n==============\n")
#         import traceback
#         traceback.print_exc()
#         click.echo("\n==============\n")
#
#         sys.exit(-1)


@click.command()
@click.argument('environment', required=False)
# @click.argument('--model_dir')
@click.option('--model_dir', required=True, help='path to directory containing the model.pkl file')
@click.option('--utc_time_served', required=False,
              help='Time in UTC when you want to show as served. E.g. "2018-05-25T17:28:53.354"')
@click.option('--dependency_file', required=True,
              help='Path to pip requirements file or manually cleaned conda yaml file. See https://conda.io/docs/user-guide/tasks/manage-environments.html#creating-an-environment-file-manually')
@click.option('--zappa_settings_file', required=False,
              help='Path to zappa_settings.json settings file. If not provided, it is assumed to be in the current working directory.')
@click.option('--project_dir', required=False,
              help='Path to the project root where your code is. If not provided, it is assumed to be  the current working directory.')
def serve(environment: str,
          model_dir: str,
          utc_time_served: str = None,
          dependency_file: str = None,
          zappa_settings_file: str = None,
          project_dir: str = None):  # pragma: no cover

    click.echo('..Waking up The Whale. This will take a while...')
    check_environment_provided(environment=environment)
    try:
        if utc_time_served:
            utc_time_served_dt = util.parse_isoformat_str(utc_time_served)
        else:
            utc_time_served_dt = None
        api.serve(environment,
                  model_dir,
                  utc_time_served=utc_time_served_dt,
                  dependency_file=dependency_file,
                  zappa_settings_file=zappa_settings_file,
                  project_dir=project_dir)
    except SystemExit as e:  # pragma: no cover
        sys.exit(e.code)
    except KeyboardInterrupt:  # pragma: no cover
        sys.exit(130)
    except Exception as e:

        click.echo("Oh no! An " + click.style("error occurred", fg='red', bold=True) + "! :(")
        click.echo("\n==============\n")
        import traceback
        traceback.print_exc()
        click.echo("\n==============\n")

        sys.exit(-1)


@click.command()
@click.argument('environment')
@click.option('--data')
def predict(environment: str, data):  # pragma: no cover

    try:
        # split_args = args.split(',')
        # dict_data = dict([s.split('=') for s in split_args])
        import json
        dict_data = json.loads(data)
        result = api.predict(environment, dict_data)
        from pprint import pprint
        pprint(result)
    except SystemExit as e:  # pragma: no cover
        sys.exit(e.code)
    except KeyboardInterrupt:  # pragma: no cover
        sys.exit(130)
    except Exception as e:

        click.echo("Oh no! An " + click.style("error occurred", fg='red', bold=True) + "! :(")
        click.echo("\n==============\n")
        import traceback
        traceback.print_exc()
        click.echo("\n==============\n")

        sys.exit(-1)


@click.command()
@click.argument('environment')
def info(environment: str):  # pragma: no cover

    try:
        result = api.info(environment)
        from pprint import pprint
        pprint(result)
    except SystemExit as e:  # pragma: no cover
        sys.exit(e.code)
    except KeyboardInterrupt:  # pragma: no cover
        sys.exit(130)
    except Exception as e:

        click.echo("Oh no! An " + click.style("error occurred", fg='red', bold=True) + "! :(")
        click.echo("\n==============\n")
        import traceback
        traceback.print_exc()
        click.echo("\n==============\n")

        sys.exit(-1)


def check_environment_provided(environment: str) -> ValueError:
    if not environment:
        raise ValueError('Environment required. Refer to docs.')
