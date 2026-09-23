# V9 continuous bed balance

Operator rejected the music jumping up before dialogue/crowd reactions, then disappearing underneath them. Removed foreground-triggered sidechain compression everywhere, not only at the interview. Crowd “ohh” peaks no longer control the bed gain.

- Music target reduced from -27 to -30 LUFS, with gentle compression driven only by the music itself, and existing entrance/ending fades. No speech- or crowd-triggered music gain changes.
- Interview foreground eased down 3 dB, with 167 ms approach and 200 ms release ramps. All other foreground unchanged.
- Bed one-second RMS windows before/during/after interview: -34.6 / -31.0 / -31.1 dBFS. No interview-induced dip; remaining variation comes from the track itself.
- Final master peak -1.0 dBFS, mean -19.6 dBFS. Local small.en ASR of actual final MP4 interview returns “This guy raped a woman.”
- Full final MP4 decode passed. Video stream copied without encoding or timing changes; v8/v9 encoded stream hashes match: `67e95fc13ca59ca1a5e723c1f521469cc6ca6e3cf66fab77b6fbd9c7051815f5`.
- Final: `../assembly-v9/build/render/knockout-brain-matchcut-001-v9.mp4`.
- SHA-256: `1ae133b70d7d634764d4403ed544fcc5c994b79fa1bcb12657ecddc858b666ea`.

No publication. Prior versions preserved. This audio-only remux does not change or reclassify existing visual gate results. Rebuild command: `python production/edit-v9/mix.py` from project root.
