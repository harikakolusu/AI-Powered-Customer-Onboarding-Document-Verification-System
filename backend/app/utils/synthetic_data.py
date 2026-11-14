import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import random
from backend.app.config import SAMPLE_DATA_DIR

def get_font(size: int = 20, bold: bool = False):
    try:
        # Standard Windows fonts
        font_name = "arialbd.ttf" if bold else "arial.ttf"
        return ImageFont.truetype(font_name, size)
    except Exception:
        return ImageFont.load_default()

def draw_pan_card(
    name: str,
    pan_number: str,
    dob: str,
    father_name: str,
    output_path: Path,
    blur: bool = False
):
    """Generates a synthetic PAN card image"""
    width, height = 900, 560
    # Soft sky-blue gradient-like card background
    img = Image.new("RGB", (width, height), color=(228, 240, 248))
    draw = ImageDraw.Draw(img)

    # Top Header Band
    draw.rectangle([(0, 0), (width, 85)], fill=(34, 112, 147))
    header_font = get_font(26, bold=True)
    sub_header_font = get_font(16, bold=True)
    draw.text((30, 15), "INCOME TAX DEPARTMENT", fill=(255, 255, 255), font=header_font)
    draw.text((30, 48), "GOVT. OF INDIA", fill=(220, 240, 255), font=sub_header_font)
    draw.text((620, 30), "PERMANENT ACCOUNT NUMBER", fill=(255, 255, 255), font=get_font(18, bold=True))

    # Photo Box
    draw.rectangle([(50, 120), (220, 330)], fill=(200, 215, 225), outline=(100, 130, 150), width=2)
    draw.text((85, 210), "[ PHOTO ]", fill=(90, 110, 125), font=get_font(20, bold=True))

    # QR Code placeholder
    draw.rectangle([(700, 120), (840, 260)], fill=(255, 255, 255), outline=(0, 0, 0), width=2)
    for i in range(710, 830, 15):
        for j in range(130, 250, 15):
            if (i + j) % 2 == 0:
                draw.rectangle([(i, j), (i + 10, j + 10)], fill=(0, 0, 0))

    # Details
    lbl_font = get_font(14, bold=False)
    val_font = get_font(20, bold=True)

    draw.text((260, 120), "Name / नाम", fill=(70, 70, 70), font=lbl_font)
    draw.text((260, 142), name.upper(), fill=(10, 25, 45), font=val_font)

    draw.text((260, 185), "Father's Name / पिता का नाम", fill=(70, 70, 70), font=lbl_font)
    draw.text((260, 207), father_name.upper(), fill=(10, 25, 45), font=val_font)

    draw.text((260, 250), "Date of Birth / जन्म तिथि", fill=(70, 70, 70), font=lbl_font)
    draw.text((260, 272), dob, fill=(10, 25, 45), font=val_font)

    # PAN Number Box
    draw.rectangle([(250, 330), (620, 390)], fill=(245, 250, 255), outline=(34, 112, 147), width=2)
    pan_font = get_font(32, bold=True)
    draw.text((275, 340), pan_number.upper(), fill=(180, 20, 20), font=pan_font)

    # Signature Box
    draw.rectangle([(670, 330), (850, 400)], fill=(255, 255, 255), outline=(150, 150, 150), width=1)
    draw.text((700, 360), name.split()[0], fill=(20, 30, 100), font=get_font(22, bold=True))
    draw.text((700, 410), "Signature / हस्ताक्षर", fill=(100, 100, 100), font=lbl_font)

    # Bottom Decorative Bar
    draw.rectangle([(0, height - 30), (width, height)], fill=(34, 112, 147))

    if blur:
        # Heavily blur for Scenario 2
        for _ in range(7):
            img = img.filter(ImageFilter.GaussianBlur(radius=9))

    img.save(output_path, "PNG")
    return output_path

def draw_aadhaar_card(
    name: str,
    aadhaar_number: str,
    dob: str,
    gender: str,
    address: str,
    output_path: Path,
    blur: bool = False
):
    """Generates a synthetic Aadhaar card image"""
    width, height = 900, 560
    img = Image.new("RGB", (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)

    # Top Header Band with Saffron & Green Stripes
    draw.rectangle([(0, 0), (width, 25)], fill=(255, 153, 51)) # Saffron
    draw.rectangle([(0, 25), (width, 70)], fill=(255, 255, 255))
    draw.rectangle([(0, 70), (width, 78)], fill=(19, 136, 8))  # Green

    draw.text((30, 30), "भारत सरकार / GOVERNMENT OF INDIA", fill=(20, 40, 80), font=get_font(22, bold=True))
    draw.text((620, 30), "आधार - आम आदमी का अधिकार", fill=(180, 50, 20), font=get_font(18, bold=True))

    # Photo Box
    draw.rectangle([(50, 110), (220, 320)], fill=(240, 240, 240), outline=(150, 150, 150), width=2)
    draw.text((85, 200), "[ PHOTO ]", fill=(120, 120, 120), font=get_font(20, bold=True))

    # Details
    lbl_font = get_font(15, bold=False)
    val_font = get_font(20, bold=True)

    draw.text((250, 110), name, fill=(10, 20, 30), font=get_font(24, bold=True))
    draw.text((250, 150), f"DOB / जन्म तिथि: {dob}", fill=(50, 50, 50), font=val_font)
    draw.text((250, 185), f"Gender / लिंग: {gender}", fill=(50, 50, 50), font=val_font)
    
    draw.text((250, 225), "Address / पता:", fill=(80, 80, 80), font=lbl_font)
    # Wrap address into two lines
    if len(address) > 45:
        addr1 = address[:45]
        addr2 = address[45:]
        draw.text((250, 245), addr1, fill=(20, 20, 20), font=get_font(16, bold=False))
        draw.text((250, 270), addr2, fill=(20, 20, 20), font=get_font(16, bold=False))
    else:
        draw.text((250, 245), address, fill=(20, 20, 20), font=get_font(16, bold=False))

    # QR Code placeholder
    draw.rectangle([(710, 110), (850, 250)], fill=(255, 255, 255), outline=(0, 0, 0), width=2)
    for i in range(720, 840, 15):
        for j in range(120, 240, 15):
            if (i * j) % 3 == 0:
                draw.rectangle([(i, j), (i + 10, j + 10)], fill=(0, 0, 0))

    # Aadhaar Number Banner (Red Line)
    draw.rectangle([(50, 420), (850, 424)], fill=(200, 30, 30))
    aadhaar_font = get_font(34, bold=True)
    draw.text((280, 440), aadhaar_number, fill=(20, 30, 50), font=aadhaar_font)
    draw.text((310, 490), "मेरा आधार, मेरी पहचान", fill=(200, 30, 30), font=get_font(18, bold=True))

    if blur:
        for _ in range(7):
            img = img.filter(ImageFilter.GaussianBlur(radius=9))

    img.save(output_path, "PNG")
    return output_path

def draw_bank_statement(
    name: str,
    account_number: str,
    ifsc: str,
    bank_name: str,
    output_path: Path
):
    """Generates a synthetic Bank Statement image"""
    width, height = 900, 650
    img = Image.new("RGB", (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)

    # Top Header
    draw.rectangle([(0, 0), (width, 80)], fill=(15, 35, 75))
    draw.text((40, 25), bank_name.upper(), fill=(255, 255, 255), font=get_font(26, bold=True))
    draw.text((620, 30), "ACCOUNT STATEMENT", fill=(200, 220, 255), font=get_font(18, bold=True))

    # Account Details Grid
    draw.rectangle([(40, 110), (860, 230)], fill=(248, 250, 252), outline=(210, 220, 230), width=1)
    
    lbl_font = get_font(14, bold=False)
    val_font = get_font(16, bold=True)

    draw.text((60, 125), "Account Holder:", fill=(100, 100, 100), font=lbl_font)
    draw.text((180, 125), name.upper(), fill=(10, 20, 30), font=val_font)

    draw.text((60, 160), "Account Number:", fill=(100, 100, 100), font=lbl_font)
    draw.text((180, 160), account_number, fill=(10, 20, 30), font=val_font)

    draw.text((60, 195), "IFSC Code:", fill=(100, 100, 100), font=lbl_font)
    draw.text((180, 195), ifsc, fill=(10, 20, 30), font=val_font)

    draw.text((500, 125), "Statement Period:", fill=(100, 100, 100), font=lbl_font)
    draw.text((640, 125), "01/01/2026 - 31/03/2026", fill=(10, 20, 30), font=val_font)

    draw.text((500, 160), "Currency / Branch:", fill=(100, 100, 100), font=lbl_font)
    draw.text((640, 160), "INR / Indiranagar", fill=(10, 20, 30), font=val_font)

    # Table Header
    draw.rectangle([(40, 260), (860, 300)], fill=(230, 238, 248))
    draw.text((60, 272), "Date", fill=(15, 35, 75), font=get_font(14, bold=True))
    draw.text((160, 272), "Description / Narration", fill=(15, 35, 75), font=get_font(14, bold=True))
    draw.text((500, 272), "Withdrawals", fill=(15, 35, 75), font=get_font(14, bold=True))
    draw.text((650, 272), "Deposits", fill=(15, 35, 75), font=get_font(14, bold=True))
    draw.text((770, 272), "Balance", fill=(15, 35, 75), font=get_font(14, bold=True))

    # Sample Transactions
    txns = [
        ("02/01/2026", "SALARY CREDIT - TECHCORP PVT LTD", "-", "₹ 1,25,000.00", "₹ 1,45,200.00"),
        ("05/01/2026", "UPI/ZOMATO/ORDER_8923", "₹ 480.00", "-", "₹ 1,44,720.00"),
        ("10/01/2026", "NEFT/RENT PAYMENT INDIRANAGAR", "₹ 28,000.00", "-", "₹ 1,16,720.00"),
        ("18/01/2026", "INTEREST CREDIT Q4", "-", "₹ 1,120.00", "₹ 1,17,840.00"),
        ("25/01/2026", "ELECTRICITY BILL BESCOM", "₹ 2,350.00", "-", "₹ 1,15,490.00"),
    ]

    y = 315
    for date, desc, wdraw, dep, bal in txns:
        draw.line([(40, y + 25), (860, y + 25)], fill=(240, 240, 240))
        draw.text((60, y), date, fill=(60, 60, 60), font=lbl_font)
        draw.text((160, y), desc[:35], fill=(30, 30, 30), font=lbl_font)
        draw.text((500, y), wdraw, fill=(180, 20, 20), font=lbl_font)
        draw.text((650, y), dep, fill=(20, 140, 40), font=lbl_font)
        draw.text((770, y), bal, fill=(10, 20, 30), font=get_font(14, bold=True))
        y += 40

    img.save(output_path, "PNG")
    return output_path

def generate_all_scenario_documents():
    """Generates synthetic documents for all 5 business scenarios"""
    SAMPLE_DATA_DIR.mkdir(parents=True, exist_ok=True)
    generated = {}

    # Scenario 1: Happy Path - Clean PAN + Aadhaar + Statement
    sc1_dir = SAMPLE_DATA_DIR / "scenario_1_valid"
    sc1_dir.mkdir(exist_ok=True)
    sc1_pan = draw_pan_card(
        name="Vikramaditya Sharma",
        pan_number="ABCPS1234D",
        dob="15/08/1990",
        father_name="Suresh Sharma",
        output_path=sc1_dir / "pan_card.png"
    )
    sc1_aadhaar = draw_aadhaar_card(
        name="Vikramaditya Sharma",
        aadhaar_number="5482 9102 3847",
        dob="15/08/1990",
        gender="MALE",
        address="Flat 301, Lotus Palms, Indiranagar, Bengaluru, KA - 560038",
        output_path=sc1_dir / "aadhaar_card.png"
    )
    sc1_stmt = draw_bank_statement(
        name="Vikramaditya Sharma",
        account_number="10982736451",
        ifsc="HDFC0001234",
        bank_name="HDFC Bank",
        output_path=sc1_dir / "bank_statement.png"
    )
    generated["scenario_1"] = {
        "title": "Scenario 1: Clean & Valid Documents",
        "name": "Vikramaditya Sharma",
        "pan": str(sc1_pan),
        "aadhaar": str(sc1_aadhaar),
        "statement": str(sc1_stmt),
        "description": "All fields match across PAN, Aadhaar, and Bank Statement. Valid format and clean image quality."
    }

    # Scenario 2: Unclear / Blurry Document
    sc2_dir = SAMPLE_DATA_DIR / "scenario_2_unclear"
    sc2_dir.mkdir(exist_ok=True)
    sc2_pan = draw_pan_card(
        name="Priya Nair",
        pan_number="BKRPN9988X",
        dob="22/11/1993",
        father_name="Kishore Nair",
        output_path=sc2_dir / "blurry_pan_card.png",
        blur=True
    )
    sc2_aadhaar = draw_aadhaar_card(
        name="Priya Nair",
        aadhaar_number="8831 2940 1192",
        dob="22/11/1993",
        gender="FEMALE",
        address="House 42, Palm Meadows, Whitefield, Bengaluru - 560066",
        output_path=sc2_dir / "aadhaar_card.png"
    )
    generated["scenario_2"] = {
        "title": "Scenario 2: Unclear Document",
        "name": "Priya Nair",
        "pan": str(sc2_pan),
        "aadhaar": str(sc2_aadhaar),
        "description": "PAN card is heavily blurred (Laplacian variance < 100), triggering unreadable quality exception."
    }

    # Scenario 3: Duplicate Application (Re-submitting same PAN)
    sc3_dir = SAMPLE_DATA_DIR / "scenario_3_duplicate"
    sc3_dir.mkdir(exist_ok=True)
    sc3_pan = draw_pan_card(
        name="Vikramaditya Sharma",
        pan_number="ABCPS1234D",  # Exactly same PAN as Scenario 1
        dob="15/08/1990",
        father_name="Suresh Sharma",
        output_path=sc3_dir / "duplicate_pan_card.png"
    )
    sc3_aadhaar = draw_aadhaar_card(
        name="Vikramaditya Sharma",
        aadhaar_number="5482 9102 3847",
        dob="15/08/1990",
        gender="MALE",
        address="Flat 301, Lotus Palms, Indiranagar, Bengaluru, KA - 560038",
        output_path=sc3_dir / "aadhaar_card.png"
    )
    generated["scenario_3"] = {
        "title": "Scenario 3: Duplicate PAN Application",
        "name": "Vikramaditya Sharma",
        "pan": str(sc3_pan),
        "aadhaar": str(sc3_aadhaar),
        "description": "Customer submits an application with PAN ABCPS1234D which already exists in the system database."
    }

    # Scenario 4: Name Discrepancy / Inconsistency
    sc4_dir = SAMPLE_DATA_DIR / "scenario_4_inconsistency"
    sc4_dir.mkdir(exist_ok=True)
    sc4_pan = draw_pan_card(
        name="Ananya Rajesh Deshmukh",
        pan_number="BKRPD5678K",
        dob="12/04/1995",
        father_name="Rajesh Deshmukh",
        output_path=sc4_dir / "pan_card.png"
    )
    sc4_aadhaar = draw_aadhaar_card(
        name="Pooja Sharma",  # Completely conflicting name!
        aadhaar_number="7721 9043 5512",
        dob="05/09/1988",    # Conflicting DOB as well!
        gender="FEMALE",
        address="Sector 14, Vashi, Navi Mumbai, MH - 400703",
        output_path=sc4_dir / "aadhaar_card.png"
    )
    generated["scenario_4"] = {
        "title": "Scenario 4: Name & DOB Inconsistency Alert",
        "name": "Ananya Deshmukh",
        "pan": str(sc4_pan),
        "aadhaar": str(sc4_aadhaar),
        "description": "PAN card shows 'Ananya Rajesh Deshmukh' while Aadhaar shows 'Pooja Sharma'. AI cross-matching engine flags high-risk mismatch."
    }

    # Scenario 5: Missing Document (Address Proof omitted)
    sc5_dir = SAMPLE_DATA_DIR / "scenario_5_missing_doc"
    sc5_dir.mkdir(exist_ok=True)
    sc5_pan = draw_pan_card(
        name="Rahul Verma",
        pan_number="BNZPV9876M",
        dob="30/06/1992",
        father_name="Mahesh Verma",
        output_path=sc5_dir / "pan_card.png"
    )
    generated["scenario_5"] = {
        "title": "Scenario 5: Missing Address Proof",
        "name": "Rahul Verma",
        "pan": str(sc5_pan),
        "aadhaar": None,  # Intentionally omitted!
        "description": "Applicant uploads PAN card but omits mandatory Address Proof (Aadhaar). System halts and requests missing document."
    }

    return generated

if __name__ == "__main__":
    generate_all_scenario_documents()
    print("All synthetic scenario documents generated successfully in storage/sample_data!")

