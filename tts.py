r"""
Online text-to-speech (English / Persian) using edge-tts.

Examples (run through run.bat):
    run.bat --lang en --text "Hello world"
    run.bat --lang fa --file input\sample_fa.txt --subs
    run.bat --lang en --text "Slower voice" --rate=-20%
    run.bat --list-voices --lang fa

Note: write negative values with "=", e.g. --rate=-10% or --pitch=-5Hz,
otherwise argparse treats them as separate options.
"""

import argparse
import asyncio
import sys
from datetime import datetime
from pathlib import Path

import edge_tts

PROJECT_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = PROJECT_DIR / "output"

DEFAULT_VOICES = {
    "en": "en-US-AriaNeural",
    "fa": "fa-IR-DilaraNeural",
}

LOCALE_PREFIX = {"en": "en-", "fa": "fa-"}

MAX_RETRIES = 3


def normalize_persian(text: str) -> str:
    """Replace Arabic letter/digit variants with their Persian forms."""
    table = {
        "\u064a": "\u06cc",  # Arabic yeh -> Persian yeh
        "\u0643": "\u06a9",  # Arabic kaf -> Persian kaf
        "\u0660": "\u06f0", "\u0661": "\u06f1", "\u0662": "\u06f2",
        "\u0663": "\u06f3", "\u0664": "\u06f4", "\u0665": "\u06f5",
        "\u0666": "\u06f6", "\u0667": "\u06f7", "\u0668": "\u06f8",
        "\u0669": "\u06f9",
    }
    return text.translate(str.maketrans(table))


async def synthesize(
    text: str,
    lang: str = "en",
    voice: str | None = None,
    rate: str = "+0%",
    volume: str = "+0%",
    pitch: str = "+0Hz",
    out_path: Path | None = None,
    subtitles: bool = False,
) -> Path:
    """Convert text to an MP3 file (and optionally an .srt) and return the audio path."""
    text = text.strip()
    if not text:
        raise ValueError("The text is empty.")

    if lang == "fa":
        text = normalize_persian(text)

    voice = voice or DEFAULT_VOICES[lang]

    if out_path is None:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_path = OUTPUT_DIR / f"tts_{lang}_{stamp}.mp3"
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    last_error: Exception | None = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            communicate = edge_tts.Communicate(
                text, voice, rate=rate, volume=volume, pitch=pitch
            )
            submaker = edge_tts.SubMaker()
            with open(out_path, "wb") as audio_file:
                async for chunk in communicate.stream():
                    if chunk["type"] == "audio":
                        audio_file.write(chunk["data"])
                    elif chunk["type"] in ("WordBoundary", "SentenceBoundary"):
                        submaker.feed(chunk)

            if subtitles:
                srt_path = out_path.with_suffix(".srt")
                srt_path.write_text(submaker.get_srt(), encoding="utf-8")
            return out_path
        except Exception as exc:  # network errors, service errors, etc.
            last_error = exc
            print(f"Attempt {attempt}/{MAX_RETRIES} failed: {exc}", file=sys.stderr)
            if attempt < MAX_RETRIES:
                await asyncio.sleep(2 * attempt)

    raise RuntimeError(f"Synthesis failed after {MAX_RETRIES} attempts: {last_error}")


async def list_voices(lang: str | None) -> None:
    voices = await edge_tts.list_voices()
    prefix = LOCALE_PREFIX.get(lang) if lang else None
    for v in sorted(voices, key=lambda x: x["ShortName"]):
        if prefix and not v["Locale"].lower().startswith(prefix):
            continue
        print(f'{v["ShortName"]:<28} {v["Gender"]:<8} {v["Locale"]}')


def read_input(args: argparse.Namespace) -> str:
    if args.text:
        return args.text
    if args.file:
        # utf-8-sig also handles files saved with a BOM by Notepad
        return Path(args.file).read_text(encoding="utf-8-sig")
    print("Enter your text (finish with an empty line):")
    lines = []
    while True:
        line = input()
        if not line:
            break
        lines.append(line)
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Online TTS (English / Persian) with edge-tts")
    p.add_argument("--lang", choices=["en", "fa"], default="en", help="language (default: en)")
    p.add_argument("--text", help="text to speak")
    p.add_argument("--file", help="path to a UTF-8 text file")
    p.add_argument("--voice", help="override the default voice, e.g. fa-IR-FaridNeural")
    p.add_argument("--rate", default="+0%", help='speed, e.g. --rate=-20%% or --rate=+10%%')
    p.add_argument("--volume", default="+0%", help='volume, e.g. --volume=+20%%')
    p.add_argument("--pitch", default="+0Hz", help='pitch, e.g. --pitch=+5Hz')
    p.add_argument("--out", help="output .mp3 path (default: output\\tts_<lang>_<time>.mp3)")
    p.add_argument("--subs", action="store_true", help="also write an .srt subtitle file")
    p.add_argument("--list-voices", action="store_true", help="list voices (filtered by --lang) and exit")
    return p


def main() -> None:
    args = build_parser().parse_args()

    if args.list_voices:
        asyncio.run(list_voices(args.lang))
        return

    text = read_input(args)
    path = asyncio.run(
        synthesize(
            text,
            lang=args.lang,
            voice=args.voice,
            rate=args.rate,
            volume=args.volume,
            pitch=args.pitch,
            out_path=Path(args.out) if args.out else None,
            subtitles=args.subs,
        )
    )
    print(f"Saved: {path}")
    if args.subs:
        print(f"Subtitles: {path.with_suffix('.srt')}")


if __name__ == "__main__":
    main()
