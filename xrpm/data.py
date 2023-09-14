from collections.abc import Iterable
from json import dumps, load
from re import MULTILINE, VERBOSE, finditer, sub
from subprocess import PIPE, run
from sys import stderr
from typing import Any

from pydantic import BaseModel, Field, ValidationError
from pyedid import Edid, parse_edid


XRANDR_OUTPUT_REGEX = r"""
^\s*
(?P<name>[^ ]+)\s*
(?P<state>connected|disconnected|unknown\ connection).*[\r\n]+
(?:^\t(?:
EDID:\s*(?P<edid>(?:\t{2}[a-z0-9]+[\r\n]+)+) |
[\w\- ]+:\s*.*[\r\n]+
(?:\t\tsupported:\s*.*[\r\n]+)?
(?:\t\trange:\s*.*[\r\n]+)?
))+
(?:^(?:\s+\d+x\d+.*)+)?
"""


class Display(BaseModel):
    edid: str
    args: list[str] = Field(default_factory=list)

    @property
    def parsed_edid(self) -> Edid:
        return parse_edid(self.edid)

    def name(self) -> str:
        name = self.parsed_edid.name
        return name if name else self.serial()

    def serial(self) -> str:
        return f"#{self.parsed_edid.serial}"

    def __str__(self) -> str:
        return f"{self.name()}({self.serial()})"


class Output(BaseModel):
    name: str
    connected: bool
    display: Display

    def __str__(self) -> str:
        if self.connected:
            return f"{self.name} -> {self.display}"
        return f"{self.name} -> X"

    def __repr__(self) -> str:
        return str(self)

    @staticmethod
    def _parse_outputs(text: str) -> Iterable["Output"]:
        matches = finditer(XRANDR_OUTPUT_REGEX, text, MULTILINE | VERBOSE)
        for match in matches:
            name, state, edid = match.group("name", "state", "edid")
            connected = state == "connected"
            if connected and not edid:
                print(
                    f"Output {name} is connected, but EDID is unknown",
                    file=stderr,
                )
            edid = sub(r"\s", "", edid) if edid else ""
            yield Output(
                name=name, connected=connected, display=Display(edid=edid)
            )

    @staticmethod
    def load_outputs() -> list["Output"]:
        proc = run(
            ["xrandr", "--properties"], stdout=PIPE, text=True, check=True
        )
        return list(Output._parse_outputs(str(proc.stdout)))


Profiles = dict[str, "Profile"]


class Profile(BaseModel):
    serial: bool = False
    match_outputs: bool = False
    global_args: list[str] = Field(default_factory=list)
    displays: dict[str, Display]

    def __str__(self) -> str:
        displays = {
            output: display.name() if not self.serial else display.serial()
            for output, display in self.displays.items()
        }
        if self.match_outputs:
            displays = [f"{output}: {display}" for output, display in displays]
        else:
            displays = displays.values()
        return ", ".join(displays)

    def pretty_print(self) -> str:
        displays = "\n\t".join(
            [
                f"{output}: {display} ({display.args})"
                for output, display in self.displays.items()
            ]
        )
        return (
            f"{self.serial=}, {self.match_outputs=}, {self.global_args=}\n"
            f"\t{displays}"
        )

    @staticmethod
    def load(path: str) -> Profiles:
        try:
            with open(path, "r") as file:
                data: dict[str, Any] | list[Any] = load(file)
                if not isinstance(data, dict):
                    raise ValueError("Invalid config: invalid root dict")
                try:
                    return {
                        str(name): Profile(**profile_data)
                        for name, profile_data in data.items()
                    }
                except ValidationError as ex:
                    raise ValueError(f"Invalid config: {ex}") from ex
        except FileNotFoundError:
            return {}

    @staticmethod
    def save(profiles: Profiles, path: str) -> None:
        content = dumps(
            {name: profile.dict() for name, profile, in profiles.items()},
            indent=4,
        )
        with open(path, "w") as file:
            file.write(content)


__all__ = [
    "Display",
    "Output",
    "Profile",
    "Profiles",
]
