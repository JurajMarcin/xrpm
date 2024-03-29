from argparse import ArgumentParser, Namespace
from os import X_OK, access

from xrpm.data import Output, Profiles
from xrpm.utils import detect_profiles, profile_args, run_command, run_xrandr


def _auto_profile(profiles: Profiles, outputs: list[Output]) -> str | None:
    detected = detect_profiles(profiles, outputs)
    sorted_detected = sorted(
        detected.items(), key=lambda kv: (not kv[1], kv[0])
    )
    return sorted_detected[0][0] if sorted_detected else None


def cmd_set(
    profiles: Profiles, outputs: list[Output], args: Namespace
) -> None:
    if not args.name:
        name = _auto_profile(profiles, outputs)
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


args_set = ArgumentParser()
args_set.add_argument(
    "name", action="store", help="name of the profile", default="", nargs="?"
)
args_set.set_defaults(exec=cmd_set)

__all__ = [
    "cmd_set",
    "args_set",
]
