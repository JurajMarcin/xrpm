from sys import stderr

from xrpm.commands import parse_args
from xrpm.data import Output, Profile


def main() -> int:
    args = parse_args()
    try:
        profiles = Profile.load(args.config)
        outputs = Output.load_outputs()
        args.exec(profiles, outputs, args)
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
