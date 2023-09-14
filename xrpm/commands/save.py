from argparse import REMAINDER, ArgumentParser, Namespace
from sys import stderr

from xrpm.data import Output, Profile, Profiles


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


args_save = ArgumentParser()
args_save.add_argument(
    "name",
    action="store",
    help="name of the profile",
)
args_save.add_argument(
    "xrandr_args",
    action="store",
    help="XRandr arguments",
    nargs=REMAINDER,
)
args_save.add_argument(
    "-s",
    "--serial",
    action="store_true",
    help="match by serial number, not name of the monitor",
)
args_save.add_argument(
    "-o",
    "--match-outputs",
    action="store_true",
    help="also match same outputs as current ones",
)
args_save.set_defaults(exec=cmd_save)


__all__ = [
    "cmd_save",
    "args_save",
]
