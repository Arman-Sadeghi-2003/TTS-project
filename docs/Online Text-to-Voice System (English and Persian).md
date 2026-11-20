# Online Text-to-Voice System (English and Persian)

Project plan for an online TTS tool built on edge-tts, kept entirely in one folder off the C: drive.

## 1. Overview

The online system uses **edge-tts**, a Python library that talks to the same Microsoft online text-to-speech service the Edge browser uses. It needs no API key and no Edge browser or Windows install. It does not synthesize anything locally: the script sends text and a voice name over a WebSocket connection and receives audio back as a stream. Your script is only a thin client, so CPU, RAM and disk needs are tiny.

The offline (local) system, planned for later with Piper TTS, is out of scope for this document.

## 2. Why edge-tts

- Free, with no account or API key
- High-quality Microsoft neural voices
- Real Persian voices and many English voices
- Very small install with few dependencies
- Actively maintained (a packaged build of version 7.2.8 appeared in May 2026)

Alternatives considered: gTTS (simpler, lower quality, can be rate-limited) and Azure Speech, Google Cloud TTS or ElevenLabs (more reliable and higher quality, but need an account or API key and may cost money).

## 3. Features

- **Language and voice selection:** choose `en` or `fa`; the script maps each to a default voice. Persian has a female and a male voice (for example fa-IR-DilaraNeural and fa-IR-FaridNeural, to be verified with `edge-tts --list-voices`), and English has many.
- **Speed, volume and pitch:** adjustable with values such as `-20%` for rate or `+10Hz` for pitch.
- **MP3 output:** audio is saved into an `output` folder. No extra tools are needed.
- **Optional subtitles:** the service returns word timing, so the script can write `.srt` or `.vtt` files next to the audio.
- **Flexible input:** text from a command-line argument, a UTF-8 `.txt` file, or interactive typing.
- **Mixed-language text:** works, but a Persian voice reads English words with a Persian accent. A later feature can split mixed content into separate Persian and English segments.
- **Retries:** network errors are caught and retried a couple of times.

## 4. Limitations

- **Internet is required.** Without a connection the call fails.
- **Unofficial service.** There is no SLA, and Microsoft could change the protocol. Updating is a simple `pip install -U edge-tts` inside the project folder.
- **No custom SSML.** Microsoft blocks SSML that Edge itself could not generate, so only rate, volume and pitch can be customized. Pauses, emphasis and phoneme tags are not available.
- **Very long texts.** Input should be split into paragraphs or sentences, generated part by part and joined, so one failure does not lose the whole job.
- **Persian text quality.** Use proper Unicode Persian letters (ی and ک rather than Arabic ي and ك) and normalize digits for a consistent reading. A small cleanup step in the script handles this.

## 5. Keeping everything off C:

Everything lives in one folder, for example `D:\tts_project`:

```
D:\tts_project\
├── venv\      Python packages (edge-tts and dependencies)
├── cache\     pip cache and temp files
├── output\    generated audio and subtitles
├── input\     optional text files
├── run.bat    sets environment variables and starts the script
└── tts.py     the script
```

Setup steps:

1. Create the virtual environment in `D:\tts_project\venv` with `python -m venv`.
2. Set `PIP_CACHE_DIR` and `TEMP`/`TMP` to the `cache` folder before installing, so pip does not write to C:.
3. Run `pip install edge-tts` inside the venv.
4. Use `run.bat` to set those variables and start the script, so they never need to be remembered.

If Python itself is installed on C:, only the interpreter stays there. To keep nothing on C: at all, use the portable "embeddable" Python zip extracted into the same folder.

## 6. Interface

A command-line tool backed by an importable function:

```
python tts.py --lang fa --text "سلام، حال شما چطور است؟"
python tts.py --lang en --file input\story.txt --rate -10% --subs
```

The importable part would be a function such as `synthesize(text, lang, voice=None, rate="+0%", out_path=...)` for use from other Python code.

## 7. Next steps

1. Confirm the project folder (for example `D:\tts_project`).
2. Generate `tts.py` and `run.bat`.
3. Test English and Persian output, with and without subtitles.
4. Later: add the offline mode with Piper TTS behind a `--mode online|offline` switch.
