from itertools import chain
from subprocess import run

from xrpm.data import Display, Output, Profile, Profiles


def run_command(argv: list[str], dry_run: bool = False) -> None:
    if dry_run:
        print("+", " ".join(argv))
    else:
        run(argv, check=True)


def run_xrandr(argv: list[str], dry_run: bool = False) -> None:
    run_command(["xrandr"] + argv, dry_run)


def _profile_displays(profile: Profile) -> dict[str, str]:
    return {
        output: display.serial() if profile.serial else display.name()
        for output, display in profile.displays.items()
    }


def _outputs_displays(
    profile: Profile, outputs: list[Output]
) -> dict[str, str]:
    return {
        output.name: output.display.serial()
        if profile.serial
        else output.display.name()
        for output in outputs
        if output.connected
    }


def detect_profiles(
    profiles: Profiles, outputs: list[Output]
) -> dict[str, bool]:
    detected: dict[str, bool] = {}
    for name, profile in profiles.items():
        profile_displays = _profile_displays(profile)
        outputs_displays = _outputs_displays(profile, outputs)
        if profile_displays == outputs_displays:
            detected[name] = True
        elif not profile.match_outputs and set(
            profile_displays.values()
        ) == set(outputs_displays.values()):
            detected[name] = False
    return detected


def _find_output(outputs: list[Output], display: Display) -> Output:
    return next(
        chain(
            (
                output
                for output in outputs
                if output.connected
                and output.display.serial() == display.serial()
            ),
            (
                output
                for output in outputs
                if output.connected and output.display.name() == display.name()
            ),
        )
    )


def profile_args(profile: Profile, outputs: list[Output]) -> list[str]:
    args = list(profile.global_args)
    output_map: dict[str, str] = {}
    for orig_output, display in profile.displays.items():
        if not display.args:
            continue
        try:
            output = _find_output(outputs, display)
        except StopIteration:
            # pylint: disable=raise-missing-from
            raise RuntimeError(f"Monitor {display} not connected")
        args.extend(("--output", output.name))
        args.extend(display.args)
        output_map[orig_output] = output.name
    for i in range(len(args)):
        if args[i] in output_map:
            args[i] = output_map[args[i]]
    for output in outputs:
        if output.name not in output_map.values():
            args.extend(("--output", output.name, "--off"))
    return args


__all__ = [
    "run_command",
    "run_xrandr",
    "detect_profiles",
    "profile_args",
]
