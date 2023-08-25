from os import getenv
from pathlib import Path
from argparse import REMAINDER, ArgumentParser, Namespace
from sys import stderr

from xrpm.data import Output, Profile, Profiles
from xrpm.utils import detect_profile, profile_args, run_xrandr


arg = ArgumentParser(prog="xrpm", description="XRandr Profile Manager")
arg.add_argument(
    "-n", "--dry-run",
    action="store_true",
    help="do not run any XRandr commands, only print them",
)
arg.add_argument(
    "-c", "--config",
    action="store",
    default=getenv("XRPM_CONFIG",
                   str(Path.home().joinpath("./.xrpm/profiles.json"))),
    help="load saved profiles from file (can be changed with XRPM_CONFIG "
         "environment variable)",
)
arg.add_argument(
    "-p", "--post-run",
    action="store",
    default=getenv("XRPM_AFTER", str(Path.home().joinpath("./.xrpm/after"))),
    help="script to run after setting profile (can be changes with "
         "XRPM_POST_RUN environment variable)",
)
arg.add_argument("--debug", action="store_true")


def cmd_status(profiles: Profiles, outputs: list[Output], _: Namespace) \
        -> None:
    detected = detect_profile(profiles, outputs)
    for name, profile in profiles.items():
        detected_mark = "*" if detected == name else " "
        print(f"{detected_mark} {name} {profile}")


arg.set_defaults(exec=cmd_status)
cmd = arg.add_subparsers()
status_arg = cmd.add_parser("status")
status_arg.set_defaults(exec=cmd_status)


def cmd_save(profiles: Profiles, outputs: list[Output], args: Namespace) \
        -> None:
    new_profile = Profile(
        serial=args.serial == True,
        match_outputs=args.match_outputs == True,
        global_args=[],
        displays={
            output.name: output.display
            for output in outputs if output.connected
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


save_arg = cmd.add_parser("save")
save_arg.add_argument(
    "name",
    action="store",
    help="name of the profile",
)
save_arg.add_argument(
    "xrandr_args",
    action="store",
    help="XRandr arguments",
    nargs=REMAINDER,
)
save_arg.add_argument(
    "-s", "--serial",
    
    action="store_true",
    help="match by serial number, not name of the monitor",
)
save_arg.add_argument(
    "-o", "--match-outputs",
    action="store_true",
    help="also match same outputs as current ones",
)
save_arg.set_defaults(exec=cmd_save)


def cmd_set(profiles: Profiles, outputs: list[Output], args: Namespace) -> None:
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


set_arg = cmd.add_parser("set")
set_arg.add_argument(
    "name",
    action="store",
    help="name of the profile",
    default="",
    nargs="?"
)
set_arg.set_defaults(exec=cmd_set)


def cmd_delete(profiles: Profiles, _: list[Output], args: Namespace) -> None:
    if args.name not in profiles:
        raise ValueError(f"Profile {args.name} not found")
    profile = profiles.pop(args.name)
    print(f"Deleted profile {args.name} {profile}")


delete_arg = cmd.add_parser("delete")
delete_arg.add_argument(
    "name",
    action="store",
    help="name of the profile",
)
delete_arg.set_defaults(exec=cmd_delete)


def parse_args() -> Namespace:
    return arg.parse_args()


__all__ = [
    "parse_args",
]
