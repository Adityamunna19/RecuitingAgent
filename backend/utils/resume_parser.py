from pypdf import PdfReader
from pypdf.errors import PdfReadError, PdfStreamError


class ResumeParseError(Exception):
    pass

def extract_text(file):
    try:
        reader = PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return text
    except (PdfReadError, PdfStreamError, Exception) as exc:
        raise ResumeParseError("Invalid or corrupted PDF.") from exc
