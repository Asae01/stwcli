import subprocess
from dataclasses import dataclass

from .models import Command
from .policy import check

TIMEOUT_SECONDS = 10


@dataclass(frozen=True)
class Result:
    stdout: str
    stderr: str
    returncode: int  # -1 means "we never got a real exit code"


def run(command: Command, timeout: float = TIMEOUT_SECONDS) -> Result:
    """Run a Command safely. Never raises for normal failures."""
    # second lock: refuse anything the policy layer would block
    if check(command).action == "blocked":
        return Result("", "Refused by policy", -1)

    try:
        done = subprocess.run(
            command.argv,
            capture_output=True,
            text=True,
            errors="replace",
            timeout=timeout,
            shell=False,
            stdin=subprocess.DEVNULL,
        )
    except subprocess.TimeoutExpired:
        return Result("", f"Timed out after {timeout} seconds", -1)
    except FileNotFoundError:
        return Result("", f"Program not found: {command.argv[0]}", -1)
    except OSError as error:
        return Result("", f"Could not run command: {error}", -1)

    return Result(done.stdout, done.stderr, done.returncode)