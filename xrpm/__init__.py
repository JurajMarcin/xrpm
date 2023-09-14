from sys import stderr

from xrpm.commands import parse_args
from xrpm.data import Output, Profile


def main() -> int:
    args = parse_args()
    try:
        profiles = Profile.load(args.config)
        outputs = Output.load_outputs()
        if args.debug:
            print(args)
        args.exec(profiles, outputs, args)
        if args.dry_run:
            print(f"Would save profiles to {args.config}:")
            for name, profile in profiles.items():
                print(f"{name}: {profile.pretty_print()}")
        else:
            Profile.save(profiles, args.config)
        return 0
    # pylint: disable=broad-exception-caught
    except Exception as ex:
        if args.debug:
            raise
        print(ex, file=stderr)
        return 1


__all__ = [
    "main",
]
