import click
# from thampi.cli.init import commands
# from thampi.cli.deploy import commands as deploy_commands
# from thampi.cli.serve import commands as serve_commands

from thampi.cli.commands import init, serve, predict, info


@click.group()
def main():
    pass


# main.add_command(commands.init)
# main.add_command(deploy_commands.deploy)
# main.add_command(serve_commands.serve)


[main.add_command(c) for c in [init, serve, predict, info]]
if __name__ == '__main__':  # pragma: no cover
    main()
