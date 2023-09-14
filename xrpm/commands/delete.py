from argparse import ArgumentParser, Namespace

from xrpm.data import Output, Profiles


def cmd_delete(profiles: Profiles, _: list[Output], args: Namespace) -> None:
    if args.name not in profiles:
        raise ValueError(f"Profile {args.name} not found")
    profile = profiles.pop(args.name)
    print(f"Deleted profile {args.name} {profile}")


args_delete = ArgumentParser()
args_delete.add_argument(
    "name",
    action="store",
    help="name of the profile",
)
args_delete.set_defaults(exec=cmd_delete)


__all__ = [
    "cmd_delete",
    "args_delete",
]
