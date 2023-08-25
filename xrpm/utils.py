from subprocess import run
from itertools import chain

from xrpm.data import Display, Output, Profile, Profiles


def run_xrandr(argv: list[str], dry_run: bool = False) -> None:
    if dry_run:
        print("+ xrandr", " ".join(argv))
    else:
        run(["xrandr"] + argv, check=True)


def _profile_display_set(profile: Profile) -> set[tuple[str, str] | str]:
    display_dict = {
        output: display.serial() if profile.serial else display.name()
        for output, display in profile.displays.items()
    }
    return set(
        display_dict.items() if profile.match_outputs else display_dict.values()
    )


def _outputs_display_set(profile: Profile, outputs: list[Output]) \
        -> set[tuple[str, str] | str]:
    output_dict = {
        output.name: output.display.serial()
                     if profile.serial
                     else output.display.name()
        for output in outputs if output.connected
    }
    return set(
        output_dict.items() if profile.match_outputs else output_dict.values()
    )


def detect_profile(profiles: Profiles, outputs: list[Output]) -> str | None:
    for name, profile in profiles.items():
        if _profile_display_set(profile) \
                == _outputs_display_set(profile, outputs):
            return name
    return None


def _find_output(outputs: list[Output], display: Display) -> Output:
    return next(chain(
        (output for output in outputs
         if output.connected and output.display.serial() == display.serial()),
        (output for output in outputs
         if output.connected and output.display.name() == display.name()),
    ))


def profile_args(profile: Profile, outputs: list[Output]) -> list[str]:
    args = list(profile.global_args)
    for display in profile.displays.values():
        try:
            output = _find_output(outputs, display)
        except StopIteration:
            raise Exception(f"Monitor {display} not connected")
        args.extend(("--output", output.name))
        args.extend(display.args)
    for output in outputs:
        if output.name not in profile.displays:
            args.extend(("--output", output.name, "--off"))
    return args


__all__ = [
    "run_xrandr",
    "detect_profile",
    "profile_args",
]
