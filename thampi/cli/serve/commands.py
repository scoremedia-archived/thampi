# import click
# import sys
# from thampi.core import api
#
#
# @click.command()
# @click.argument('environment')
# # @click.argument('--model_file')
# @click.option('--model_file', required=True, help='path to Python pickled model file')
# @click.option('--name', required=True, help='Name of model. e.g LinearRegression, HybridRecommender')
# @click.option('--version', required=True, help='Version of model. e.g "0.1", "1.0-alpha"')
# @click.option('--training_time_utc', required=False,
#               help='Time in UTC when it was trained. E.g. "2018-05-25T17:28:53.354"')
# @click.option('--instance_id', required=False,
#               help='An unique id to identify a trained instance of a model of the same name and version')
# # @click.option('--tags', required=False, help='JSON String. e.g. \'{ "region": "us-east-1", "author": "Raj"}\'')
# def serve(environment: str,
#           model_file: str,
#           name: str,
#           version: str,
#           training_time_utc: str = None,
#           instance_id: str = None):  # pragma: no cover
#
#     try:
#         api.serve(environment,
#                   model_file,
#                   name=name,
#                   version=version,
#                   training_time_utc=training_time_utc,
#                   instance_id=instance_id)
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
