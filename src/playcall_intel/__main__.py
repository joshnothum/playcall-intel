from __future__ import annotations
import argparse
import os

from playcall_intel.game_report import write_game_report


def main():
    parser = argparse.ArgumentParser(description="Playcall-Intel CLI")
    parser.add_argument("--game-id", help="Generate a game report for this game_id")

    args = parser.parse_args()

    if args.game_id:
        path = write_game_report(args.game_id)
        print(f"Wrote {path}")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
