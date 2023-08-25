from sys import stderr
from xrpm.commands import parse_args
from xrpm.data import Output, Profile


def main() -> int:
    args = parse_args()
    print(args)
    try:
        profiles = Profile.load(args.config)
        outputs = Output.load_outputs()
        args.exec(profiles, outputs, args)
        Profile.save(profiles, args.config)
        return 0
    except Exception as e:
        if args.debug:
            raise
        print(e, file=stderr)
        return 1


__all__ = [
    "main",
]
