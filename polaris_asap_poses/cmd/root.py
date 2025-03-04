import typer

from polaris_asap_poses import __version__
from polaris_asap_poses.cmd.nb import app as nb_app

# typer autocompletion does weird crap to your shell, so we're turning it off
app = typer.Typer(add_completion=False, no_args_is_help=True)
app.add_typer(nb_app, name="nb", help="Manage local Jupyter instance.")


@app.command()
def version():
    """
    Show the version and exit.
    """
    typer.echo(f"polaris-asap-poses {__version__}")



def main():
    app()
