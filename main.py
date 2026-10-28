import sys

from collector import run_collector


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def main():
    run_collector()


if __name__ == "__main__":
    main()

