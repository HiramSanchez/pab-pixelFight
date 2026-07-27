import argparse
import os
from pathlib import Path
import subprocess
import time


def main():
    parser = argparse.ArgumentParser(
        description="Check that the packaged game remains running after startup."
    )
    parser.add_argument("executable", type=Path)
    args = parser.parse_args()

    environment = os.environ.copy()
    environment["SDL_VIDEODRIVER"] = "dummy"
    environment["SDL_AUDIODRIVER"] = "dummy"
    environment["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

    process = subprocess.Popen(
        [str(args.executable.resolve())],
        cwd=args.executable.resolve().parent,
        env=environment,
    )
    try:
        time.sleep(2)
        return_code = process.poll()
        if return_code is not None:
            raise SystemExit(
                f"Packaged startup failed with exit code {return_code}."
            )
        print("Packaged startup: PASS")
    finally:
        if process.poll() is None:
            process.terminate()
            process.wait(timeout=10)


if __name__ == "__main__":
    main()
