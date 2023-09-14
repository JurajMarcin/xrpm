from argparse import ArgumentParser, Namespace

from xrpm.data import Output, Profiles
from xrpm.utils import detect_profile


def cmd_status(
    profiles: Profiles, outputs: list[Output], _: Namespace
) -> None:
    detected = detect_profile(profiles, outputs)
    for name, profile in profiles.items():
        detected_mark = "*" if detected == name else " "
        print(f"{detected_mark} {name} {profile}")


args_status = ArgumentParser()
args_status.set_defaults(exec=cmd_status)


__all__ = [
    "cmd_status",
    "args_status",
]
