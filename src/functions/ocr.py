import pytesseract
from PIL import Image
from io import BytesIO

async def recognize_sticker(image_data: bytes) -> str:
    img = Image.open(BytesIO(image_data))
    text = pytesseract.image_to_string(img, lang='eng+rus')
    return text.strip()