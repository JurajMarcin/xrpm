# XRPM - XRandr Profile Manager

(Once) Simple Python script to manage your XRandr configurations for different sets of
monitors.

## Usage

```bash
xrpm [GLOBAL OPTIONS] [ACTION [ACTION OPTIONS] [ACTION ARGS...]]
```

More detailed help can be displayed with:
```bash
xrpm --help
```

or for subcommand:
```bash
xrpm subcommand --help
```

### Example

Show saved profiles, `+` marks detected profiles.

```bash
xrpm status
```

Set detected profile. If multiple are detected, the first one is set.

```bash
xrpm set
```

Create a new profile with 2 monitors, stacked vertically, center aligned with different resolutions and modes.

```bash
xrpm save test_profile --output eDP-1 --auto --pos 760x1440 --output DP-1 --mode 2560x1440 --rate 165 --pos 0x0
```

## Files

By default xrpm stores saved profiles in `$HOME/.xrpm/profiles.json` and loads post set
script from `$HOME/.xrpm/post` (no script is executed, if it does not exists or
is not set as executable).

These paths can be altered by setting `XRPM_CONFIG` or `XRPM_POST` environment
variables respectively or using command line options
