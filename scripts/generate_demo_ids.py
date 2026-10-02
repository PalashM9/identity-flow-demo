from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

OUTPUT = Path("demo_data")
OUTPUT.mkdir(exist_ok=True)

people = [
    {
        "file": "ava_schneider.png",
        "name": "Ava Schneider",
        "dob": "1993-05-14",
        "doc": "DEMO-A1B2C3",
        "expiry": "2031-05-14",
    },
    {
        "file": "noah_weber.png",
        "name": "Noah Weber",
        "dob": "1988-11-02",
        "doc": "DEMO-D4E5F6",
        "expiry": "2030-11-02",
    },
    {
        "file": "mia_fischer_expired.png",
        "name": "Mia Fischer",
        "dob": "1995-03-27",
        "doc": "DEMO-X9Y8Z7",
        "expiry": "2024-03-27",
    },
]

for person in people:
    image = Image.new("RGB", (1200, 700), "#EAF2FF")
    draw = ImageDraw.Draw(image)

    draw.rectangle((30, 30, 1170, 670), outline="#1E3A5F", width=6)
    draw.rectangle((70, 140, 310, 460), fill="#C8D8EF", outline="#1E3A5F", width=3)

    draw.text((85, 80), "DEMO IDENTITY CARD — NOT A REAL ID", fill="#B91C1C")
    draw.text((360, 160), f"Name: {person['name']}", fill="#111827")
    draw.text((360, 235), f"Date of Birth: {person['dob']}", fill="#111827")
    draw.text((360, 310), f"Document Number: {person['doc']}", fill="#111827")
    draw.text((360, 385), "Country: DE", fill="#111827")
    draw.text((360, 460), f"Expiry Date: {person['expiry']}", fill="#111827")
    draw.text((360, 550), "Fictional test data only", fill="#6B7280")

    image.save(OUTPUT / person["file"])

print(f"Created demo files in: {OUTPUT.resolve()}")