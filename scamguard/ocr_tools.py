def ocr_image(image):
    try:
        import pytesseract
        text = pytesseract.image_to_string(image)
        return {"available": True, "text": text.strip(), "error": None}
    except Exception as e:
        return {"available": False, "text": "", "error": str(e)}
