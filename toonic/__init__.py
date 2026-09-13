"""
Toonic — Universal TOON Format Platform
========================================

Converts any structured file into compact, LLM-optimized TOON representations.
Supports code, documents, data, config, API specs, infrastructure, video, and audio.

Usage:
    from toonic import Pipeline

    # File → TOON spec
    spec = Pipeline.to_spec('src/models.py', fmt='toon')

    # Batch processing
    specs = Pipeline.batch('./project/', fmt='toon', output_dir='./specs/')

    # Available formats
    info = Pipeline.formats()
"""

__version__ = "1.0.19"

from toonic.core import (
    FileLogic,
    FileHandler,
    BaseHandlerMixin,
    FormatRegistry,
    SpecDetector,
    CodeLogicBase,
)
from toonic.pipeline import Pipeline, ReproductionResult

__all__ = [
    "Pipeline",
    "ReproductionResult",
    "FileLogic",
    "FileHandler",
    "BaseHandlerMixin",
    "FormatRegistry",
    "SpecDetector",
    "CodeLogicBase",
]
