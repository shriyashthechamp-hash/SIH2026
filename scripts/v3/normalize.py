import argparse
import os
import re
import pandas as pd


REQUIRED_COLUMNS = [
    "source_image",
    "preprocess_variant",
    "psm",
    "raw_text",
    "clean_text",
    "ocr_confidence",
]


# Conservative OCR confusion map.
# The substitutions are applied only according to character position.
CONFUSIONS = {
    "O": "0",
    "I": "1",
    "L": "1",
    "Z": "2",
    "S": "5",
    "B": "8",
    "G": "6",
    "T": "7",
    "Q": "0",
}


def clean_input_text(value):
    """Return a safe uppercase alphanumeric OCR string."""
    if pd.isna(value):
        return ""
    return re.sub(r"[^A-Z0-9]", "", str(value).upper())


def position_is_numeric(position, length):
    """
    Indian registration plates generally have:
        STATE + DISTRICT + SERIES + NUMBER

    This is intentionally tolerant.

    For common 8-10 character plates:
        positions 0-1: state letters
        positions 2-3: district/RTO digits
        middle positions: series letters
        final 4 positions: registration number digits
    """
    if position in (2, 3):
        return True

    # Final four positions are normally numeric.
    if length >= 8 and position >= length - 4:
        return True

    return False


def normalize_candidate(text):
    """
    Conservatively normalize OCR text.

    Returns:
        normalized_text,
        normalization_applied,
        normalization_reason,
        alternatives
    """
    text = clean_input_text(text)

    if not text:
        return "", False, "empty_candidate", ""

    # Very short OCR outputs are not useful candidates for normalization.
    if len(text) < 5:
        return text, False, "too_short_for_normalization", ""

    chars = list(text)
    changes = []

    for i, char in enumerate(chars):
        # Numeric-position correction.
        if position_is_numeric(i, len(chars)):
            if char in CONFUSIONS:
                replacement = CONFUSIONS[char]

                if replacement != char:
                    chars[i] = replacement
                    changes.append(
                        f"{char}->{replacement}@{i}"
                    )

    normalized = "".join(chars)

    if not changes:
        return normalized, False, "no_safe_normalization", ""

    # Keep the alternative original candidate.
    alternatives = text

    return (
        normalized,
        True,
        "contextual_numeric_position:" + ",".join(changes),
        alternatives,
    )


def process(input_path, output_path):
    if not os.path.exists(input_path):
        raise FileNotFoundError(
            f"Input file does not exist: {input_path}"
        )

    df = pd.read_csv(input_path)

    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]

    if missing:
        raise ValueError(
            f"Missing required columns: {missing}"
        )

    print(f"Input rows: {len(df)}")

    results = df["clean_text"].apply(normalize_candidate)

    df["normalized_text"] = results.apply(lambda x: x[0])
    df["normalization_applied"] = results.apply(lambda x: x[1])
    df["normalization_reason"] = results.apply(lambda x: x[2])
    df["normalization_candidates"] = results.apply(lambda x: x[3])

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

    df.to_csv(output_path, index=False)

    changed = int(df["normalization_applied"].sum())

    print(f"Output rows: {len(df)}")
    print(f"Rows normalized: {changed}")
    print(f"Rows unchanged: {len(df) - changed}")
    print(f"Output: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="ANVAY V3 — conservative OCR normalization"
    )

    parser.add_argument(
        "--input",
        required=True,
        help="Path to Phase 7 OCR candidates CSV",
    )

    parser.add_argument(
        "--output",
        required=True,
        help="Path for normalized candidates CSV",
    )

    args = parser.parse_args()

    process(args.input, args.output)


if __name__ == "__main__":
    main()
