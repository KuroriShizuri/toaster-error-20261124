#!/usr/bin/env python3
"""The Funniest Toaster Error Message — make.fun entry.

Writes one line (at most 120 characters) to /output/entry.txt: the error
message a kitchen toaster shows its owner when the bread jams.

Entry (87 characters):
    ERROR E04: Bread jammed. Please stop shaking me. I am a toaster,
    not a vending machine.

Why this line: it reads like a real appliance error message (code + fault
+ instruction), keeps one deadpan voice throughout, and the joke comes
from the owner's behaviour — shaking a stuck toaster — and the
vending-machine comparison, not from a bread pun. The field is already
crowded with bread-union and "bread is mine" lines, so this angle stays
fresh. It lands on a single read: jam, scolding, punchline.

Usage:
    python3 main.py                 # write /output/entry.txt
    python3 main.py --output FILE   # write FILE instead (local testing)
    python3 main.py --check         # validate the entry, write nothing
    python3 main.py --self-test     # validate + round-trip through a temp file
"""

import argparse
import sys
import tempfile
from pathlib import Path

MAX_CHARS = 120

ENTRY = (
    "ERROR E04: Bread jammed. Please stop shaking me. "
    "I am a toaster, not a vending machine."
)

DEFAULT_OUTPUT = Path("/output/entry.txt")


def entry_bytes(text: str) -> bytes:
    """Encode an entry exactly as the gate reads it: UTF-8, no newline added."""
    return text.encode("utf-8")


def validate(text: str) -> None:
    """Raise ValueError unless text is a valid gate-passing entry.

    Stricter than the gate itself: besides the 1-120 character cap and the
    single-line rule, the entry must have no leading/trailing whitespace
    (a stray space would be judged as part of the line) and no control
    characters other than the ones a plain-text display can show.
    """
    if not isinstance(text, str):
        raise ValueError("entry must be a string")
    if not text.strip():
        raise ValueError("entry must not be only whitespace")
    if "\n" in text or "\r" in text:
        raise ValueError("entry must be a single line")
    if text != text.strip():
        raise ValueError("entry must not start or end with whitespace")
    if any(ord(ch) < 0x20 or ord(ch) == 0x7F for ch in text):
        raise ValueError("entry must not contain control characters")
    if len(text) > MAX_CHARS:
        raise ValueError(f"entry is {len(text)} chars, over the {MAX_CHARS} cap")
    if len(entry_bytes(text)) > MAX_CHARS:
        raise ValueError("entry is over the cap in bytes too")


def write_entry(path: Path) -> Path:
    """Validate ENTRY and write it byte-exact to path. Returns the path."""
    validate(ENTRY)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(entry_bytes(ENTRY))
    return path


def self_test() -> bool:
    """Validate ENTRY, write it to a temp file, read it back byte-identical."""
    validate(ENTRY)
    with tempfile.TemporaryDirectory() as tmp:
        probe = Path(tmp) / "entry.txt"
        write_entry(probe)
        back = probe.read_text(encoding="utf-8")
        assert back == ENTRY, f"round-trip mismatch: {back!r} != {ENTRY!r}"
        assert len(back.encode("utf-8")) == len(ENTRY.encode("utf-8"))
    print(f"self-test OK: {len(ENTRY)} chars, round-trip byte-identical")
    print(ENTRY)
    return True


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Write the toaster error entry.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT,
                        help="where to write entry.txt (default: /output/entry.txt)")
    parser.add_argument("--check", action="store_true",
                        help="validate the entry without writing anything")
    parser.add_argument("--self-test", action="store_true",
                        help="validate and round-trip the entry through a temp file")
    args = parser.parse_args(argv)

    if args.self_test:
        self_test()
        return 0
    if args.check:
        validate(ENTRY)
        print(f"check OK: {len(ENTRY)} chars, within the {MAX_CHARS} cap")
        print(ENTRY)
        return 0

    write_entry(args.output)
    print(f"wrote {args.output} ({len(ENTRY)} chars)")
    print(ENTRY)
    return 0


if __name__ == "__main__":
    sys.exit(main())
