import click
import sys
from thampi.core import api


# @click.command()
# @click.option('--config_file', required=False, help='Path to .conf file with AWS credentials etc.')
# @click.option('--file', required=True, help='Path to file which contains the pipeline')
# @click.option('--pipeline', required=True, help='Name of the pipeline')
# @click.option('--function', required=False, help='Path to file which contains the pipeline')
# @click.option('--qualify_lambda_name/--do_not_qualify_lambda_name', default=True)
# def deploy(config_file, file, pipeline, qualify_lambda_name, function):  # pragma: no cover
#     """
#     Main program execution handler.
#     """
#     try:
#
#         deploy_file(config_file, file, pipeline, qualify_lambda_name, function)
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


# @click.command()
# # @click.option('--config_file', required=False, help='Path to .conf file with AWS credentials etc.')
# # @click.option('--file', required=True, help='Path to file which contains the pipeline')
# # @click.option('--pipeline', required=True, help='Name of the pipeline')
# # @click.option('--function', required=False, help='Path to file which contains the pipeline')
# # @click.option('--qualify_lambda_name/--do_not_qualify_lambda_name', default=True)
# def init():  # pragma: no cover
#     """
#     Main program execution handler.
#     """
#     try:
#         api.init()
#
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
