from argparse import ArgumentParser, Namespace
from pathlib import Path
from re import VERBOSE, match
from shlex import split
from sys import stderr

from xrpm.commands.save import cmd_save
from xrpm.data import Display, Output, Profiles

OLD_PROFILE_RE = r"""
^(?:(?P<type>name|serial)\s+)?
(?P<name>[\w-]+)\s+
(?P<edids>(?:[0-9a-z]+,?)+)\s+
(?P<args>.*)$
"""


def cmd_convert(profiles: Profiles, _: list[Output], args: Namespace) -> None:
    with open(args.old_config, "r") as old_config:
        for line in old_config:
            line_match = match(OLD_PROFILE_RE, line.strip(), VERBOSE)
            if line_match is None:
                print(
                    f"Skipping invalid profile '{line.strip()}'", file=stderr
                )
                continue
            name = line_match.group("name")
            print(f"Converting profile {name}")
            xrandr_args = split(line_match.group("args"))
            displays = {
                str(i): Display(edid=edid)
                for i, edid in enumerate(
                    set(line_match.group("edids").split(",")), start=1
                )
            }
            outputs: list[Output] = []
            for i in range(1, len(xrandr_args)):
                if xrandr_args[i - 1] != "--output":
                    continue
                for selection, display in displays.items():
                    print(f"{selection}: {display}")
                output = xrandr_args[i]
                while (
                    key := input(f"Choose display for output {output}: ")
                ) not in displays:
                    pass
                outputs.append(
                    Output(
                        name=output, connected=True, display=displays.pop(key)
                    )
                )
            cmd_save(
                profiles,
                outputs,
                Namespace(
                    serial=line_match.group("type") == "serial",
                    match_outputs=False,
                    xrandr_args=xrandr_args,
                    name=name,
                    dry_run=args.dry_run,
                    config=args.config,
                    post_set=args.post_set,
                ),
            )


args_convert = ArgumentParser()
args_convert.add_argument(
    "old_config",
    action="store",
    help="old config path",
    default=str(Path.home().joinpath("./.xrpm/profiles")),
    nargs="?",
)
args_convert.set_defaults(exec=cmd_convert)



__all__ = [
    "cmd_convert",
    "args_convert",
]
