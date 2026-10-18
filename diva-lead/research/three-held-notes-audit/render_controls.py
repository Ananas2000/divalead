"""Render the published v57 performance and a three-held-note control in Diva.

Requires Linux/Wine, the user's Diva binary, and a compiled copy of the v57
analysis/diva_source_render_host.c. No audio processing or parameter search.
"""
from pathlib import Path
import argparse
import hashlib
import json
import os
import subprocess

import numpy as np
import soundfile as sf


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("plugin", "host", "wine", "wine-prefix", "wine-dll-path", "output"):
        parser.add_argument("--" + name, required=True, type=Path)
    args = parser.parse_args()
    release = Path(__file__).resolve().parents[2] / "v57-wip"
    args.output.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env.update(WINEPREFIX=str(args.wine_prefix.resolve()),
               WINEDLLPATH=str(args.wine_dll_path.resolve()), WINEDEBUG="-all")

    def win(path):
        return "Z:" + str(Path(path).resolve()).replace("/", "\\")

    timing = json.loads((release / "render_timing_180BPM.json").read_text())
    report = {"match_reached": False, "held_control_is_an_improved_candidate": False,
              "sample_rate": 48000, "warmup_blocks": 128, "block_size": 512,
              "Diva_ARP": "Off", "Finish_used": False,
              "held_root_velocities": [96, 96, 101], "renders": {}}
    for mode in ("expanded-v57-control", "held-three-no-arp"):
        if mode == "expanded-v57-control":
            commands = ["pattern 8 0 8",
                        "timing {} {}".format(timing["host_swing"], timing["host_default_gate"])]
            for command, values in (
                ("stepvel", timing["velocities"]),
                ("stepgrid", timing["offsets"] + timing["gates"]),
                ("secondvel", timing["second_velocities"]),
                ("secondgrid", timing["second_offsets"] + timing["second_gates"])):
                commands.append(command + " " + " ".join(map(str, values)))
        else:
            commands = ["pattern 3 0 8", "velocities 96 96 101"]
        wav = args.output / (mode + ".wav")
        commands += ["warmblocks 128", "preludes 0", "render " + win(wav), "quit"]
        command_text = "\n".join(commands) + "\n"
        (args.output / (mode + "-commands.txt")).write_text(command_text)
        logfile = args.output / (mode + ".log")
        with logfile.open("w") as log:
            subprocess.run([str(args.wine), str(args.host), win(args.plugin),
                            win(release / "Diva_Lead_v57_WIP.h2p")],
                           input=command_text, text=True, env=env, stdout=log,
                           stderr=log, timeout=90, check=True)
        log_text = logfile.read_text()
        assert "ERROR " not in log_text
        audio, rate = sf.read(wav, dtype="float32")
        assert rate == 48000 and audio.shape == (288000, 2) and np.isfinite(audio).all()
        events = [list(map(int, line.split()[1:])) for line in log_text.splitlines()
                  if line.startswith("NOTE ")]
        (args.output / (mode + "-notes.json")).write_text(json.dumps(events, indent=2) + "\n")
        result = {"note_on_count": sum(e[1] == 144 for e in events),
                  "WAV_SHA256": hashlib.sha256(wav.read_bytes()).hexdigest(),
                  "decoded_float32_SHA256": hashlib.sha256(audio.tobytes()).hexdigest()}
        if mode == "expanded-v57-control":
            published, _ = sf.read(release / "Diva_SOURCE_FROZEN_48k.wav", dtype="float32")
            assert np.array_equal(audio, published), "Published raw source not reproduced"
            expected = json.loads((release / "verification/MIDI_note_events_48k.json").read_text())
            assert events == [[e[k] for k in ("frame", "status", "pitch", "velocity")]
                              for e in expected["events"]]
            result["published_raw_samples_and_MIDI_exact"] = True
        else:
            assert [e[2] for e in events if e[1] == 144] == [41, 37, 36] * 2
        report["renders"][mode] = result
    (args.output / "verification.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
