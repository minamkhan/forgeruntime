# ForgeRuntime v0: the voice runtime for CineForge GPU sessions.
#
# Everything a voice job needs is installed and the Chatterbox weights are baked in,
# so a pod goes from "started" to "working" without pip installs or model downloads.
# Video models (ComfyUI + Wan 2.2 / Z-Image) arrive in v1.
#
# Built in the cloud by bitbucket-pipelines.yml (this PC has no Docker) and pushed to
# a private Docker Hub repo. Pinned for reproducibility: base image by tag, Python
# packages by version, and the full `pip freeze` is saved inside the image.

FROM pytorch/pytorch:2.6.0-cuda12.4-cudnn9-runtime

ENV DEBIAN_FRONTEND=noninteractive \
    PIP_NO_CACHE_DIR=1 \
    PYTHONUNBUFFERED=1 \
    HF_HOME=/opt/hf \
    FORGERUNTIME_VERSION=0.1.0

RUN apt-get update \
 && apt-get install -y --no-install-recommends ffmpeg curl ca-certificates \
 && rm -rf /var/lib/apt/lists/*

COPY requirements-voice.txt /opt/forgeruntime/requirements-voice.txt
RUN pip install -r /opt/forgeruntime/requirements-voice.txt \
 && pip freeze > /opt/forgeruntime/pip-freeze.txt

# Bake the model weights (MIT licence) so sessions never download them.
COPY prefetch.py /opt/forgeruntime/prefetch.py
RUN python /opt/forgeruntime/prefetch.py

# The token-protected job server + self-delete timer used by tools/gpu/session.py.
COPY boot.py /opt/forgeruntime/boot.py

WORKDIR /work
CMD ["python3", "-u", "/opt/forgeruntime/boot.py"]
