import importlib
import traceback
from pathlib import Path

import sstimap
import sstimap.data_types
import sstimap.plugins

from .core import checks
from .core.interactive import InteractiveShell
from .utils import cliparser
from .utils.config import config_args, version
from .utils.loggers import log

PROJECT_ROOT = Path(sstimap.__file__).resolve().parent
PLUGINS_DIR = Path(sstimap.plugins.__file__).resolve().parent
DATA_TYPES_DIR = Path(sstimap.data_types.__file__).resolve().parent


def main():
    args = vars(cliparser.options)
    args = config_args(args)
    args["version"] = version
    from .utils.loggers import no_colour, setup_logging

    is_color_enabled = args.get("colour", True)

    setup_logging(color=is_color_enabled)

    if is_color_enabled:
        print(cliparser.banner())
    else:
        print(no_colour(cliparser.banner()))
    load_plugins()
    from .core.plugin import loaded_plugins

    log.log(
        26,
        f"Loaded plugins by categories: {'; '.join([f'{x}: {len(loaded_plugins[x])}' for x in loaded_plugins])}",
    )
    load_data_types()
    from .core.data_type import loaded_data_types

    log.log(26, f"Loaded request body types: {len(loaded_data_types)}\n")
    if not (
        args["url"]
        or args["interactive"]
        or args["load_urls"]
        or args["load_forms"]
        or args["module"]
    ):
        # no target specified
        log.log(
            22,
            "SSTImap requires target URL (-u, --url), URLs/forms file (--load-urls / --load-forms) "
            "or interactive mode (-i, --interactive)",
        )
    elif args["module"]:
        # module list / help
        checks.module_info("" if args["module"] == "list" else args["module"])
    elif args["interactive"]:
        # interactive mode
        log.log(
            23, "Starting SSTImap in interactive mode. Type 'help' to see the details."
        )
        InteractiveShell(args).cmdloop()
    else:
        # predetermined mode
        checks.scan_website(args)


def autoload_modules(path: Path, root: Path):
    """
    Load all Python modules found in a given path
    """
    importlib.invalidate_caches()

    for item in path.rglob("*.py"):
        path_parts = str(item.relative_to(root)).split("/")
        path_parts[-1] = path_parts[-1][:-len(item.suffix)]  # strip file suffix

        # Skip hidden directories and _private modules
        if any(_is_hidden_module(p) for p in path_parts):
            continue

        module_name = ".".join(path_parts)
        importlib.import_module(module_name)


def _is_hidden_module(name: str):
    return name.startswith((".", "_"))



def load_plugins():
    autoload_modules(PLUGINS_DIR, PROJECT_ROOT.parent)


def load_data_types():
    autoload_modules(DATA_TYPES_DIR, PROJECT_ROOT.parent)


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print()
        log.log(22, "Exiting")
    except Exception as e:
        log.critical("Error: {}".format(e))
        log.debug(traceback.format_exc())
        raise e
