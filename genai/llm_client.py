# -*- coding: utf-8 -*-
"""Thin wrapper around the Gemini API for text generation."""

import os
from google import genai

MODEL = "gemini-flash-latest"


def _get_client():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY no configurada en el entorno (.env)")
    return genai.Client(api_key=api_key)


def generate_text(prompt, model=MODEL):
    client = _get_client()
    resp = client.models.generate_content(model=model, contents=prompt)
    return resp.text
