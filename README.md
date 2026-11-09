# ForgeRuntime

A pinned GPU runtime image for CineForge video-generation sessions on rented GPUs (RunPod).

**v0 (voice):** CUDA 12.4, PyTorch 2.6, Chatterbox TTS 0.1.7 (MIT) with its weights pre-downloaded, FFmpeg.
The full `pip freeze` is saved in the image at `/opt/forgeruntime/pip-freeze.txt`.

```
ghcr.io/minamkhan/forgeruntime:voice-latest
ghcr.io/minamkhan/forgeruntime:<version>-<commit>   # pin this one for reproducible runs
```

Built by GitHub Actions on every push to `main` (`.github/workflows/build.yml`).

The image contains only open-source software, public model weights and `boot.py`, a small token-protected
job server with a self-delete timer. No scripts, voices, data or credentials are ever baked in; jobs upload
those to each pod at run time.

This repository is published from the `forgeruntime/` folder of the CineForge project.
