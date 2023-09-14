from argparse import ArgumentParser, Namespace
from os import getenv
from pathlib import Path
from xrpm.commands.status import cmd_status, args_status
from xrpm.commands.convert import args_convert
from xrpm.commands.delete import args_delete
from xrpm.commands.save import args_save
from xrpm.commands.set import args_set


args_parser = ArgumentParser(prog="xrpm", description="XRandr Profile Manager")
args_parser.add_argument(
    "-n",
    "--dry-run",
    action="store_true",
    help="do not run any XRandr commands, only print them",
)
args_parser.add_argument(
    "-c",
    "--config",
    action="store",
    default=getenv(
        "XRPM_CONFIG", str(Path.home().joinpath("./.xrpm/profiles.json"))
    ),
    help="load saved profiles from file (can be changed with XRPM_CONFIG "
    "environment variable)",
)
args_parser.add_argument(
    "-p",
    "--post-set",
    action="store",
    default=getenv("XRPM_POST", str(Path.home().joinpath("./.xrpm/post"))),
    help="script to run after setting profile (can be changes with "
    "XRPM_POST environment variable)",
)
args_parser.add_argument("--debug", action="store_true")

args_parser.set_defaults(exec=cmd_status)
commands = args_parser.add_subparsers()
commands.add_parser("convert", parents=[args_convert], add_help=False)
commands.add_parser("delete", parents=[args_delete], add_help=False)
commands.add_parser("save", parents=[args_save], add_help=False)
commands.add_parser("set", parents=[args_set], add_help=False)
commands.add_parser("status", parents=[args_status], add_help=False)


def parse_args() -> Namespace:
    return args_parser.parse_args()


__all__ = [
    "parse_args",
]
