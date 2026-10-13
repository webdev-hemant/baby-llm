"""Baby LLM: Privacy-First, Self-Evolving Local Memory & Life Success Engine."""

import os
import warnings

# Suppress unauthenticated Hugging Face Hub rate-limit warnings for public models
os.environ.setdefault("HF_HUB_VERBOSITY", "error")
os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING", "1")
warnings.filterwarnings("ignore", message=".*unauthenticated requests.*")

try:
    from huggingface_hub.utils import logging as hf_logging
    hf_logging.set_verbosity_error()
except Exception:
    pass

__version__ = "0.1.0"
