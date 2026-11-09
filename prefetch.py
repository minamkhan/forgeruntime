"""Download model weights into the image at build time (HF_HOME=/opt/hf), so pods never fetch them."""

from huggingface_hub import snapshot_download

# Chatterbox (MIT): the files ChatterboxTTS.from_pretrained() loads.
snapshot_download(
    "ResembleAI/chatterbox",
    allow_patterns=["ve.safetensors", "t3_cfg.safetensors", "s3gen.safetensors", "tokenizer.json", "conds.pt"],
)
print("prefetch: chatterbox weights cached")
