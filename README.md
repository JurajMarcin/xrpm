# XRPM - XRandr Profile Manager

Simple Python script to manage your XRandr configurations for different sets of
monitors.

## Usage

```bash
xrpm
xrpm [ACTION [ACTION_ARGS...]]
```

### Actions

**status**

- show saved and detected profiles (default)

**save [--serial] NAME XRANDR_ARGS...**

- create a new profile for connected monitors (matches monitor name by default, use option `--serial` to match monitor serial numbers)

**delete NAME**

- delete the profile NAME

**set NAME**

- load profile NAME and execute after script

**auto**

- load the first detected profile and execute after script

## Files

By default xrpm stores saved profiles in `$HOME/.xrpm/profiles` and loads after
script from `$HOME/.xrpm/after` (no script is executed, if it does not exists or
is not set as executable).

These paths can be altered by setting `XRPM_CONFIG` or `XRPM_AFTER` environment
variables respectively.
