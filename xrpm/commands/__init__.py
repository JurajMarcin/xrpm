from argparse import ArgumentParser, Namespace, REMAINDER
from os import X_OK, access, getenv
from pathlib import Path
import re
import shlex
from sys import stderr

from xrpm.data import Display, Output, Profile, Profiles
from xrpm.utils import detect_profile, profile_args, run_command, run_xrandr


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


def cmd_status(
    profiles: Profiles, outputs: list[Output], _: Namespace
) -> None:
    detected = detect_profile(profiles, outputs)
    for name, profile in profiles.items():
        detected_mark = "*" if detected == name else " "
        print(f"{detected_mark} {name} {profile}")


args_parser.set_defaults(exec=cmd_status)
cmd_parser = args_parser.add_subparsers()
status_args_parser = cmd_parser.add_parser("status")
status_args_parser.set_defaults(exec=cmd_status)


def cmd_save(
    profiles: Profiles, outputs: list[Output], args: Namespace
) -> None:
    new_profile = Profile(
        serial=args.serial is True,
        match_outputs=args.match_outputs is True,
        global_args=[],
        displays={
            output.name: output.display
            for output in outputs
            if output.connected
        },
    )
    arg_output = False
    selected_output = ""
    for arg in args.xrandr_args:
        if arg_output:
            selected_output = arg
            arg_output = False
        elif arg == "--output":
            arg_output = True
        elif selected_output == "":
            new_profile.global_args.append(arg)
        elif selected_output in new_profile.displays:
            new_profile.displays[selected_output].args.append(arg)
        else:
            print(f"Ignored XRandr argument: {arg}", file=stderr)
    profiles[args.name] = new_profile
    print(f"Created profile {args.name} {new_profile}")


save_args_parser = cmd_parser.add_parser("save")
save_args_parser.add_argument(
    "name",
    action="store",
    help="name of the profile",
)
save_args_parser.add_argument(
    "xrandr_args",
    action="store",
    help="XRandr arguments",
    nargs=REMAINDER,
)
save_args_parser.add_argument(
    "-s",
    "--serial",
    action="store_true",
    help="match by serial number, not name of the monitor",
)
save_args_parser.add_argument(
    "-o",
    "--match-outputs",
    action="store_true",
    help="also match same outputs as current ones",
)
save_args_parser.set_defaults(exec=cmd_save)


def cmd_set(
    profiles: Profiles, outputs: list[Output], args: Namespace
) -> None:
    if not args.name:
        name = detect_profile(profiles, outputs)
    elif args.name not in profiles:
        raise ValueError(f"Profile {args.name} not found")
    else:
        name = args.name
    if name:
        print(f"Setting profile {name}")
        run_xrandr(profile_args(profiles[name], outputs), args.dry_run)
    else:
        print("No profile detected, using auto profile")
        run_xrandr(["--auto"], args.dry_run)
    if access(args.post_set, X_OK):
        print("Running post set scripts")
        run_command([args.post_set], args.dry_run)


set_args_parser = cmd_parser.add_parser("set")
set_args_parser.add_argument(
    "name", action="store", help="name of the profile", default="", nargs="?"
)
set_args_parser.set_defaults(exec=cmd_set)


def cmd_delete(profiles: Profiles, _: list[Output], args: Namespace) -> None:
    if args.name not in profiles:
        raise ValueError(f"Profile {args.name} not found")
    profile = profiles.pop(args.name)
    print(f"Deleted profile {args.name} {profile}")


delete_args_parser = cmd_parser.add_parser("delete")
delete_args_parser.add_argument(
    "name",
    action="store",
    help="name of the profile",
)
delete_args_parser.set_defaults(exec=cmd_delete)


def parse_args() -> Namespace:
    return args_parser.parse_args()


__all__ = [
    "parse_args",
]
