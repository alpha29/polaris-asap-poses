import os
import subprocess
import webbrowser
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import List, NamedTuple, Optional

import nbformat as nbf
import typer
from typing_extensions import Annotated
from polaris_asap_poses.settings import get_settings

settings = get_settings()

POLARIS_ASAP_POSES_HOME = os.environ["POLARIS_ASAP_POSES_HOME"]
NB_DIR = Path(POLARIS_ASAP_POSES_HOME) / "notebooks"
NB_PORT = settings.notebook_port
app = typer.Typer(add_completion=False, no_args_is_help=True)


@app.command()
def up():
    """
    Start Jupyter.
    """
    cmd = f"jupyter notebook --allow-root --ip=0.0.0.0 --port={NB_PORT} --no-browser --notebook-dir=./notebooks --NotebookApp.token=''".split(
        " "
    )
    subprocess.run(cmd, check=True)


@app.command()
def open():
    """
    Open a browser, pointing to the Jupyter web interface.
    """
    webbrowser.open_new_tab(f"http://localhost:{NB_PORT}/")


@app.command()
def new(name: Annotated[Optional[str], typer.Argument()] = None):
    """
    Create a new notebook.
    """
    nb_name = write_default_notebook(name)
    typer.echo(f"Created notebook '{nb_name}'.")
    webbrowser.open_new_tab(f"http://localhost:{NB_PORT}/notebooks/{nb_name}")


class CellType(Enum):
    CODE = "code"
    MARKDOWN = "markdown"
    RAW = "raw"

    @staticmethod
    def as_list():
        return [i.value for i in CellType]

    @staticmethod
    def as_dict():
        return {i.name: i.value for i in CellType}


class NotebookCell(NamedTuple):
    name: str
    type: CellType
    content: str


def get_default_notebook_cells(module_name: str = "polaris_asap_poses") -> List[NotebookCell]:
    nb_cells = list()

    nb_cells.append(
        NotebookCell(
            name="welcome",
            type=CellType.MARKDOWN,
            content="""\
# polaris_asap_poses.\
    """,
        )
    )

    nb_cells.append(
        NotebookCell(
            name="magic",
            type=CellType.CODE,
            content="""\
%load_ext autoreload
%autoreload 2\
    """,
        )
    )

    nb_cells.append(
        NotebookCell(
            name="env_setup",
            type=CellType.CODE,
            content="""\
import os
from pathlib import Path
POLARIS_ASAP_POSES_HOME = Path(os.environ["POLARIS_ASAP_POSES_HOME"])
os.chdir(POLARIS_ASAP_POSES_HOME)\
    """,
        )
    )

#    nb_cells.append(
#        NotebookCell(
#            name="load_dj",
#            type=CellType.CODE,
#            content="""\
#os.environ["DJANGO_SETTINGS_MODULE"] = "leashbelka.settings.local"
#os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
#import django
#django.setup()\
#    """,
#        )
#    )

    nb_cells.append(
        NotebookCell(
            name="load_settings",
            type=CellType.CODE,
            content="""\
from polaris_asap_poses.settings import get_settings
settings = get_settings()\
    """,
        )
    )

    nb_cells.append(
        NotebookCell(
            name="load_logger",
            type=CellType.CODE,
            content="""\
from polaris_asap_poses.logger import logger
logger.info("hello world")\
    """,
        )
    )

    nb_cells.append(
        NotebookCell(
            name="load_default_imports",
            type=CellType.CODE,
            content="""\
import polars as pl
import numpy as np
import polars.selectors as cs
from tqdm import tqdm
from pathlib import Path\
    """,
        )
    )
    return nb_cells


def get_default_notebook() -> nbf.notebooknode.NotebookNode:
    nb = nbf.v4.new_notebook()
    for i in get_default_notebook_cells():
        if i.type == CellType.CODE:
            _ = nbf.v4.new_code_cell(i.content)
        elif i.type == CellType.MARKDOWN:
            _ = nbf.v4.new_markdown_cell(i.content)
        elif i.type == CellType.RAW:
            _ = nbf.v4.new_raw_cell(i.content)
        else:
            raise Exception(f"Invalid type {i.type} for cell {i.name}.")
        nb["cells"].append(_)
    return nb


def write_default_notebook(name: str = None) -> str:
    if name is None:
        now = datetime.now().strftime("%Y%m%d_%H%M%S")
        name = f"default_{now}"
    nb = get_default_notebook()
    notebook_filepath = NB_DIR / f"{name}.ipynb"
    nbf.write(nb, notebook_filepath)
    return name
