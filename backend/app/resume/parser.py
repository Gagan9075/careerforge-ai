import re


SECTION_NAMES = [
    "professional summary",
    "summary",
    "objective",
    "skills",
    "technical skills",
    "experience",
    "work experience",
    "professional experience",
    "education",
    "projects",
    "certifications",
]


def normalize_section_name(section_name: str) -> str:
    name = section_name.lower().strip()

    if name in {"professional summary", "summary", "objective"}:
        return "summary"

    if name in {
        "experience",
        "work experience",
        "professional experience",
    }:
        return "experience"

    if name in {"skills", "technical skills"}:
        return "skills"

    return name


def extract_email(text: str) -> str | None:
    match = re.search(
        r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
        text,
    )

    return match.group(0) if match else None


def extract_phone(text: str) -> str | None:
    match = re.search(
        r"(?:\+?\d[\d\s().-]{8,}\d)",
        text,
    )

    if not match:
        return None

    phone = match.group(0).strip()

    # Avoid treating very long numbers as phone numbers.
    digits = re.sub(r"\D", "", phone)

    if 10 <= len(digits) <= 15:
        return phone

    return None


def extract_contact_information(header: str) -> dict:
    lines = [line.strip() for line in header.splitlines() if line.strip()]

    email = extract_email(header)
    phone = extract_phone(header)

    name = lines[0] if lines else None

    location = None

    for line in lines:
        # The contact line contains email/phone and usually
        # has the location before the first "|".
        if email and email in line:
            parts = [part.strip() for part in line.split("|")]

            for part in parts:
                if email not in part and (
                    not phone or phone not in part
                ):
                    if part:
                        location = part
                        break

            if location:
                break

    return {
        "name": name,
        "email": email,
        "phone": phone,
        "location": location,
    }


def parse_resume_text(text: str) -> dict:
    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    sections = {}
    current_section = "header"
    sections[current_section] = []

    for line in lines:
        normalized = line.lower().strip()

        if normalized in SECTION_NAMES:
            current_section = normalize_section_name(normalized)

            if current_section not in sections:
                sections[current_section] = []

            continue

        sections[current_section].append(line)

    header = "\n".join(sections.get("header", []))

    contact = extract_contact_information(header)

    return {
        "header": header,
        "name": contact["name"],
        "email": contact["email"],
        "phone": contact["phone"],
        "location": contact["location"],
        "summary": "\n".join(sections.get("summary", [])),
        "skills": "\n".join(sections.get("skills", [])),
        "experience": "\n".join(sections.get("experience", [])),
        "education": "\n".join(sections.get("education", [])),
        "projects": "\n".join(sections.get("projects", [])),
        "certifications": "\n".join(
            sections.get("certifications", [])
        ),
    }