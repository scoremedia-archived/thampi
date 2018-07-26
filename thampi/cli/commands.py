import click
import sys
from thampi.core import api
from thampi.lib import util


@click.command()
def init():  # pragma: no cover
    """
    Main program execution handler.
    """
    try:
        api.init()
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
@click.argument('environment')
# @click.argument('--model_file')
@click.option('--model_file', required=True, help='path to Python pickled model file')
@click.option('--name', required=True, help='Name of model. e.g LinearRegression, HybridRecommender')
@click.option('--version', required=True, help='Version of model. e.g "0.1", "1.0-alpha"')
@click.option('--training_time_utc', required=False,
              help='Time in UTC when it was trained. E.g. "2018-05-25T17:28:53.354"')
@click.option('--instance_id', required=False,
              help='An unique id to identify a trained instance of a model of the same name and version')
@click.option('--dependency_file', required=False,
              help='Path to file with all the project dependencies. This could be a requirements file')
@click.option('--zappa_settings_file', required=False,
              help='Path to zappa_settings.json. If not provided, it is assumed to be in the current working directory')
@click.option('--project_dir', required=False,
              help='Path to the project root where your code is. If not provided, it is assumed to be  the current working directory')
# @click.option('--tags', required=False, help='JSON String. e.g. \'{ "region": "us-east-1", "author": "Raj"}\'')
def serve(environment: str,
          model_file: str,
          name: str,
          version: str,
          training_time_utc: str = None,
          instance_id: str = None,
          dependency_file: str = None,
          zappa_settings_file: str = None,
          project_dir: str = None):  # pragma: no cover

    try:
        if training_time_utc:
            training_time_utc_dt = util.parse_isoformat_str(training_time_utc)
        else:
            training_time_utc_dt = None
        api.serve(environment,
                  model_file,
                  name=name,
                  version=version,
                  training_time_utc=training_time_utc_dt,
                  instance_id=instance_id,
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
@click.option('--args')
def predict(environment: str, args):  # pragma: no cover

    try:
        # split_args = args.split(',')
        # dict_args = dict([s.split('=') for s in split_args])
        import json
        dict_args = json.loads(args)
        result = api.predict(environment, dict_args)
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
