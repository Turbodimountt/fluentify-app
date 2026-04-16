"""
Fluentify — Writing/Vision Service
RF-24 to RF-27: Stroke recognition for Kanji, Cyrillic, and Arabic alphabets.
Uses a lightweight classifier for character recognition.
Target: < 500ms response time (RNF-02).
"""
import time
import uuid
from typing import Optional


# ============================================================
# Stroke Data Structures
# ============================================================
class StrokePoint:
    def __init__(self, x: float, y: float, timestamp: float = 0, pressure: float = 1.0):
        self.x = x
        self.y = y
        self.timestamp = timestamp
        self.pressure = pressure


# ============================================================
# Character Recognition
# ============================================================
async def analyze_strokes(
    strokes: list[list[dict]],
    target_character: str,
    writing_system: str = "kanji",
    cefr_level: str = "A1",
) -> dict:
    """
    RF-24: Analyze handwritten strokes against target character.
    
    Args:
        strokes: List of stroke paths, each being a list of {x, y, t, pressure} points
        target_character: The character the user is trying to write
        writing_system: "kanji", "cyrillic", "arabic", "hangul"
        cefr_level: User's level for difficulty calibration
        
    Returns:
        Analysis result with score, feedback, and stroke order info.
    """
    start_time = time.time()

    # Extract stroke features
    features = _extract_stroke_features(strokes)
    
    # Get reference data for the target character
    reference = _get_character_reference(target_character, writing_system)
    
    # Compare strokes against reference
    analysis = _compare_strokes(features, reference, target_character)
    
    # Generate feedback
    feedback = _generate_writing_feedback(analysis, cefr_level, writing_system)
    
    processing_ms = (time.time() - start_time) * 1000

    return {
        "id": str(uuid.uuid4()),
        "target_character": target_character,
        "writing_system": writing_system,
        "accuracy_score": analysis["accuracy"],
        "stroke_order_correct": analysis["stroke_order_correct"],
        "stroke_count_expected": reference.get("stroke_count", 0),
        "stroke_count_actual": len(strokes),
        "feedback": feedback,
        "stroke_details": analysis.get("stroke_details", []),
        "processing_ms": round(processing_ms, 1),
    }


def _extract_stroke_features(strokes: list[list[dict]]) -> dict:
    """Extract geometric features from raw stroke data."""
    if not strokes:
        return {"stroke_count": 0, "total_length": 0, "bounding_box": None}

    all_points = []
    stroke_lengths = []
    stroke_directions = []

    for stroke in strokes:
        if len(stroke) < 2:
            stroke_lengths.append(0)
            stroke_directions.append("dot")
            continue

        length = 0
        for i in range(1, len(stroke)):
            dx = stroke[i].get("x", 0) - stroke[i - 1].get("x", 0)
            dy = stroke[i].get("y", 0) - stroke[i - 1].get("y", 0)
            length += (dx ** 2 + dy ** 2) ** 0.5

        stroke_lengths.append(length)
        
        # Determine primary direction
        start = stroke[0]
        end = stroke[-1]
        dx = end.get("x", 0) - start.get("x", 0)
        dy = end.get("y", 0) - start.get("y", 0)
        
        if abs(dx) > abs(dy):
            direction = "right" if dx > 0 else "left"
        else:
            direction = "down" if dy > 0 else "up"
        stroke_directions.append(direction)

        all_points.extend(stroke)

    # Calculate bounding box
    xs = [p.get("x", 0) for p in all_points]
    ys = [p.get("y", 0) for p in all_points]

    return {
        "stroke_count": len(strokes),
        "total_length": sum(stroke_lengths),
        "stroke_lengths": stroke_lengths,
        "stroke_directions": stroke_directions,
        "bounding_box": {
            "x_min": min(xs) if xs else 0,
            "x_max": max(xs) if xs else 0,
            "y_min": min(ys) if ys else 0,
            "y_max": max(ys) if ys else 0,
        },
        "aspect_ratio": (max(xs) - min(xs)) / max(max(ys) - min(ys), 1) if xs and ys else 1,
    }


def _get_character_reference(character: str, writing_system: str) -> dict:
    """Get reference stroke data for a character."""
    # Basic reference database for common characters
    references = {
        "kanji": {
            "一": {"stroke_count": 1, "directions": ["right"], "name": "ichi (one)"},
            "二": {"stroke_count": 2, "directions": ["right", "right"], "name": "ni (two)"},
            "三": {"stroke_count": 3, "directions": ["right", "right", "right"], "name": "san (three)"},
            "人": {"stroke_count": 2, "directions": ["left-down", "right-down"], "name": "hito (person)"},
            "大": {"stroke_count": 3, "directions": ["right", "left-down", "right-down"], "name": "dai (big)"},
            "日": {"stroke_count": 4, "directions": ["down", "down-right", "right", "right"], "name": "nichi (day)"},
            "月": {"stroke_count": 4, "directions": ["down-left", "down", "right", "right"], "name": "tsuki (moon)"},
            "水": {"stroke_count": 4, "directions": ["down-left", "down", "left-down", "right-down"], "name": "mizu (water)"},
            "火": {"stroke_count": 4, "directions": ["dot", "dot", "left-down", "right-down"], "name": "hi (fire)"},
            "山": {"stroke_count": 3, "directions": ["down", "down-up", "down"], "name": "yama (mountain)"},
        },
        "cyrillic": {
            "А": {"stroke_count": 3, "directions": ["up-right", "down-right", "right"], "name": "A"},
            "Б": {"stroke_count": 3, "directions": ["right", "down", "right-curve"], "name": "B"},
            "В": {"stroke_count": 3, "directions": ["down", "right-curve", "right-curve"], "name": "V"},
            "Г": {"stroke_count": 2, "directions": ["right", "down"], "name": "G"},
            "Д": {"stroke_count": 3, "directions": ["up-right", "down-right", "right"], "name": "D"},
        },
        "hangul": {
            "ㄱ": {"stroke_count": 2, "directions": ["right", "down"], "name": "giyeok"},
            "ㄴ": {"stroke_count": 2, "directions": ["down", "right"], "name": "nieun"},
            "ㄷ": {"stroke_count": 3, "directions": ["right", "down", "right"], "name": "digeut"},
            "ㅁ": {"stroke_count": 4, "directions": ["down", "right", "down", "right"], "name": "mieum"},
        },
    }

    system_refs = references.get(writing_system, {})
    return system_refs.get(character, {"stroke_count": 0, "directions": [], "name": character})


def _compare_strokes(features: dict, reference: dict, target: str) -> dict:
    """Compare extracted features against the reference."""
    expected_count = reference.get("stroke_count", 0)
    actual_count = features.get("stroke_count", 0)

    # Stroke count score
    if expected_count == 0:
        count_score = 0.7  # Unknown character, give partial credit
    elif actual_count == expected_count:
        count_score = 1.0
    else:
        diff = abs(actual_count - expected_count)
        count_score = max(0, 1.0 - diff * 0.25)

    # Stroke order/direction score
    expected_dirs = reference.get("directions", [])
    actual_dirs = features.get("stroke_directions", [])
    direction_matches = 0
    for i in range(min(len(expected_dirs), len(actual_dirs))):
        if expected_dirs[i] in actual_dirs[i] or actual_dirs[i] in expected_dirs[i]:
            direction_matches += 1
    
    direction_score = direction_matches / max(len(expected_dirs), 1) if expected_dirs else 0.5

    # Proportions score (aspect ratio)
    proportion_score = 0.8  # Base score for now

    # Combined accuracy
    accuracy = round(count_score * 0.4 + direction_score * 0.35 + proportion_score * 0.25, 2)

    stroke_details = []
    for i in range(actual_count):
        expected_dir = expected_dirs[i] if i < len(expected_dirs) else "unknown"
        actual_dir = actual_dirs[i] if i < len(actual_dirs) else "unknown"
        correct = expected_dir in actual_dir or actual_dir in expected_dir if expected_dir != "unknown" else True
        stroke_details.append({
            "stroke_number": i + 1,
            "direction_correct": correct,
            "expected_direction": expected_dir,
            "actual_direction": actual_dir,
        })

    return {
        "accuracy": min(accuracy, 1.0),
        "stroke_order_correct": count_score == 1.0 and direction_score >= 0.7,
        "count_score": count_score,
        "direction_score": direction_score,
        "proportion_score": proportion_score,
        "stroke_details": stroke_details,
    }


def _generate_writing_feedback(analysis: dict, cefr_level: str, writing_system: str) -> list[dict]:
    """Generate human-readable feedback for the user."""
    feedback = []
    accuracy = analysis["accuracy"]

    # Overall assessment
    if accuracy >= 0.9:
        feedback.append({
            "type": "praise",
            "message": "¡Excelente trazo! Tu escritura es muy precisa. 🌟",
        })
    elif accuracy >= 0.7:
        feedback.append({
            "type": "encouragement",
            "message": "¡Buen intento! Estás progresando bien. 💪",
        })
    elif accuracy >= 0.5:
        feedback.append({
            "type": "suggestion",
            "message": "Sigue practicando. Presta atención al orden de los trazos. ✍️",
        })
    else:
        feedback.append({
            "type": "guidance",
            "message": "Intenta seguir el orden de trazos indicado. Cada trazo tiene una dirección específica. 📝",
        })

    # Stroke count feedback
    if analysis["count_score"] < 1.0:
        feedback.append({
            "type": "stroke_count",
            "message": f"Número de trazos: esperado vs tuyo. Revisa el modelo de referencia.",
        })

    # Direction feedback
    if analysis["direction_score"] < 0.7:
        feedback.append({
            "type": "direction",
            "message": "Intenta seguir la dirección correcta de cada trazo (arriba→abajo, izquierda→derecha).",
        })

    # System-specific tips
    if writing_system == "kanji":
        feedback.append({
            "type": "tip",
            "message": "En Kanji, el orden general es: arriba antes que abajo, izquierda antes que derecha, horizontal antes que vertical.",
        })
    elif writing_system == "cyrillic":
        feedback.append({
            "type": "tip",
            "message": "En cirílico, mantén las letras dentro de las líneas guía y cuida la inclinación uniforme.",
        })

    return feedback


# ============================================================
# Character Library
# ============================================================
def get_practice_characters(writing_system: str, level: str = "beginner") -> list[dict]:
    """Get a list of practice characters for the given system and level."""
    libraries = {
        "kanji": {
            "beginner": [
                {"char": "一", "meaning": "one", "reading": "いち (ichi)", "strokes": 1},
                {"char": "二", "meaning": "two", "reading": "に (ni)", "strokes": 2},
                {"char": "三", "meaning": "three", "reading": "さん (san)", "strokes": 3},
                {"char": "人", "meaning": "person", "reading": "ひと (hito)", "strokes": 2},
                {"char": "大", "meaning": "big", "reading": "おお (ō)", "strokes": 3},
                {"char": "山", "meaning": "mountain", "reading": "やま (yama)", "strokes": 3},
                {"char": "日", "meaning": "day/sun", "reading": "にち (nichi)", "strokes": 4},
                {"char": "月", "meaning": "moon/month", "reading": "つき (tsuki)", "strokes": 4},
                {"char": "水", "meaning": "water", "reading": "みず (mizu)", "strokes": 4},
                {"char": "火", "meaning": "fire", "reading": "ひ (hi)", "strokes": 4},
            ],
            "intermediate": [
                {"char": "食", "meaning": "eat", "reading": "た (ta)", "strokes": 9},
                {"char": "飲", "meaning": "drink", "reading": "の (no)", "strokes": 12},
                {"char": "話", "meaning": "speak", "reading": "はな (hana)", "strokes": 13},
                {"char": "読", "meaning": "read", "reading": "よ (yo)", "strokes": 14},
                {"char": "書", "meaning": "write", "reading": "か (ka)", "strokes": 10},
            ],
        },
        "cyrillic": {
            "beginner": [
                {"char": "А", "meaning": "A", "reading": "ah", "strokes": 3},
                {"char": "Б", "meaning": "B", "reading": "beh", "strokes": 3},
                {"char": "В", "meaning": "V", "reading": "veh", "strokes": 3},
                {"char": "Г", "meaning": "G", "reading": "geh", "strokes": 2},
                {"char": "Д", "meaning": "D", "reading": "deh", "strokes": 3},
                {"char": "Е", "meaning": "Ye", "reading": "yeh", "strokes": 3},
                {"char": "Ж", "meaning": "Zh", "reading": "zheh", "strokes": 5},
                {"char": "З", "meaning": "Z", "reading": "zeh", "strokes": 1},
            ],
        },
        "hangul": {
            "beginner": [
                {"char": "ㄱ", "meaning": "g/k", "reading": "giyeok", "strokes": 2},
                {"char": "ㄴ", "meaning": "n", "reading": "nieun", "strokes": 2},
                {"char": "ㄷ", "meaning": "d/t", "reading": "digeut", "strokes": 3},
                {"char": "ㅁ", "meaning": "m", "reading": "mieum", "strokes": 4},
                {"char": "ㅂ", "meaning": "b/p", "reading": "bieup", "strokes": 4},
            ],
        },
    }

    system_lib = libraries.get(writing_system, {})
    return system_lib.get(level, system_lib.get("beginner", []))
