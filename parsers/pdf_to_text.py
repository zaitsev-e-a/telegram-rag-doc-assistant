import pymupdf
from pdf2image import convert_from_path
import pytesseract
from PIL import Image
import numpy as np
import cv2
from pathlib import Path
from pypdf import PdfReader
from core.config import settings


def validate_pdf(pdf_path):
    path = Path(pdf_path)

    try:
        with open(path, 'rb') as f:
            header = f.read(5)
            if header != b'%PDF-':
                return False
    except (IOError, OSError) as e:
        return False

    try:
        reader = PdfReader(str(path))
        _ = reader.trailer

        if len(reader.pages) == 0:
            return False
    except Exception as e:
        return False

    return True


def extract_text_from_pdf(pdf_path):
    doc = pymupdf.open(pdf_path)
    all_text = []

    for page in doc:
        text = page.get_text()
        if text:
            all_text.append(text)

    doc.close()
    return '\n'.join(all_text)


def preprocess_image(pil_img):
    open_cv_image = np.array(pil_img.convert('RGB'))
    gray = cv2.cvtColor(open_cv_image, cv2.COLOR_RGB2GRAY)

    binary = cv2.adaptiveThreshold(
        gray,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        blockSize=15,
        C=10,
    )

    processed_pil = Image.fromarray(binary)
    return processed_pil


def pdf_to_text(pdf_path):
    if not validate_pdf(pdf_path):
        return False

    try:
        text = extract_text_from_pdf(pdf_path)
    except Exception as e:
        return False

    if text:
        return text

    try:
        images = convert_from_path(pdf_path, dpi=settings.PDF_DPI)
    except Exception as e:
        return False

    full_text = []

    for i, img in enumerate(images, start=1):
        img = preprocess_image(img)

        try:
            text = pytesseract.image_to_string(
                img,
                lang=settings.PDF_LANG
            )
        except pytesseract.TesseractError as e:
            text = ""

        full_text.append(
            f'{text.strip()}'
        )

    return "\n".join(full_text)