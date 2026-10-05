SUPPORTED_AUDIO = {"mp3", "wav", "m4a", "aac", "ogg", "flac", "webm"}
SUPPORTED_DOCUMENTS = {"pdf", "txt", "md", "markdown"}
MAX_FILE_BYTES = 100 * 1024 * 1024

def validate_upload(name: str, size: int):
    suffix = name.lower().rsplit(".", 1)[-1] if "." in name else ""
    if suffix not in SUPPORTED_AUDIO | SUPPORTED_DOCUMENTS:
        return f"Unsupported file type .{suffix}. Use audio, PDF, TXT, or Markdown."
    if size > MAX_FILE_BYTES:
        return "This file is larger than CoCoa's 100 MB limit."
    return None
