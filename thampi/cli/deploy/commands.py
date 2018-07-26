# import click
# import sys
# from thampi.core import api
#
#
# @click.command()
# @click.argument('environment')
# def deploy(environment):  # pragma: no cover
#     """
#     Main program execution handler.
#     """
#     try:
#         # api.init()
#         api.deploy(environment)
#         # print('Environment:' + environment)
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
