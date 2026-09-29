"""Twenty source-linked production rules and the questionnaire schema.

Rules express possible causes, not laboratory-confirmed diagnoses.
All horticultural references were checked on 28 September 2026.
"""

SOURCES = {
    "S1": {"title": "Watering Indoor Plants", "publisher": "University of Maryland Extension", "url": "https://www.extension.umd.edu/resource/watering-indoor-plants", "accessed": "2026-09-28"},
    "S2": {"title": "Diagnose Indoor Plant Problems", "publisher": "University of Maryland Extension", "url": "https://www.extension.umd.edu/resource/diagnose-indoor-plant-problems", "accessed": "2026-09-28"},
    "S3": {"title": "Houseplant Diseases & Disorders", "publisher": "Clemson Cooperative Extension", "url": "https://hgic.clemson.edu/factsheet/houseplant-diseases-disorders/", "accessed": "2026-09-28"},
    "S4": {"title": "Common Houseplant Insects & Related Pests", "publisher": "Clemson Cooperative Extension", "url": "https://hgic.clemson.edu/factsheet/common-houseplant-insects-related-pests/", "accessed": "2026-09-28"},
    "S5": {"title": "Managing insects on indoor plants", "publisher": "University of Minnesota Extension", "url": "https://extension.umn.edu/garden-and-home/yard-and-garden/yard-and-garden-insects/insects-on-indoor-plants", "accessed": "2026-09-28"},
}

GROUPS = [
    {"id": "water", "title": "Water and soil", "description": "Check the potting mix below the surface. Choose Not sure if you have not checked."},
    {"id": "environment", "title": "Light and temperature", "description": "Think about recent changes in the plant's position or growing conditions."},
    {"id": "leaves", "title": "Leaves and roots", "description": "Report only what you can see. Roots can stay Not sure if you have not inspected them."},
    {"id": "pests", "title": "Visible pests", "description": "Look closely at new growth, leaf joints, leaf undersides and the soil surface."},
]

def question(key, label, group, help_text="", choices=None):
    return {"key": key, "label": label, "group": group, "help": help_text,
            "choices": choices or [["unknown", "Not sure"], ["yes", "Yes"], ["no", "No"]]}

QUESTIONS = [
    question("soil", "How does the potting mix feel?", "water", "Wet means it remains wet between waterings, not just immediately after watering.", [["unknown", "Not sure"], ["dry", "Dry below the surface"], ["wet", "Persistently wet"], ["balanced", "Neither dry nor persistently wet"]]),
    question("wilting", "Is the plant wilting or drooping?", "water"),
    question("yellowing", "Are leaves turning yellow?", "water"),
    question("standing_water", "Does the pot remain standing in collected water?", "water"),
    question("salt_crust", "Are there crusty mineral deposits on the mix or pot?", "water", "A hard crust, rather than fuzzy mould."),
    question("brown_tips", "Are the leaf tips brown?", "water"),
    question("softened_water", "Do you use chemically softened water?", "water", "Water treated by a household salt-based softener; ordinary filtered water is different."),
    question("stretched", "Is new growth unusually thin and stretched?", "environment"),
    question("low_light", "Is the plant in a dim position?", "environment", "Less light than the species normally needs."),
    question("bleached", "Do leaves have pale or bleached patches?", "environment"),
    question("stronger_sun", "Was the plant recently moved into stronger sunlight?", "environment"),
    question("blackening", "Are leaves or shoots turning black?", "environment"),
    question("cold_exposure", "Was the plant recently exposed to unusually cold conditions?", "environment"),
    question("gray_fuzz", "Is fuzzy grey growth present on old leaves or flowers?", "leaves"),
    question("dark_soft_roots", "If inspected, are roots both dark and soft?", "leaves", "Do not answer Yes from root colour alone."),
    question("white_powder", "Is white powdery growth spreading across leaf surfaces?", "leaves", "Different from individual cottony insects or dried water deposits."),
    question("brown_spots", "Are there brown spots on the leaves?", "leaves"),
    question("target_rings", "Do those spots contain target-like rings?", "leaves"),
    question("black_dots", "Are tiny black dots visible inside dead leaf spots?", "leaves"),
    question("water_soaked", "Do leaf spots look water-soaked?", "leaves"),
    question("spot_ooze", "Does sticky liquid ooze from those spots?", "leaves", "Liquid at the lesion, not a general sticky coating from insects."),
    question("pear_insects", "Are small pear-shaped insects clustered on new growth?", "pests"),
    question("cotton_insects", "Are cottony white insects in leaf joints or underneath leaves?", "pests"),
    question("pale_speckles", "Are there many tiny pale speckles on leaves?", "pests"),
    question("fine_webbing", "Is delicate webbing present on the plant?", "pests"),
    question("shell_bumps", "Are attached shell-like bumps present on stems or leaves?", "pests"),
    question("white_flies", "Do tiny white insects fly up when the plant is disturbed?", "pests"),
    question("dark_flies", "Are tiny dark flies moving near the soil surface?", "pests"),
]

def rule(number, title, conditions, advice, refs, section, any_conditions=None, pest=False, kind="Possible problem"):
    identifier = f"R{number:02d}"
    return {"id": identifier, "title": title, "all": conditions, "any": any_conditions or [],
            "advice": advice, "sources": refs, "source_section": section, "kind": kind,
            "derive": {identifier + "_matched": True, **({"pest_suspected": True} if pest else {})}}

RULES = [
    rule(1, "Insufficient watering", [("wilting", "yes"), ("soil", "dry")], "Water according to this plant's needs and allow excess water to drain. Check moisture before watering again.", ["S1", "S2"], "Watering guidance; Plant wilting"),
    rule(2, "Overwatering stress", [("soil", "wet")], "Review watering frequency. Check drainage and, if practical, inspect the roots before adding more water.", ["S2", "S3"], "Plant wilting; Cultural/Environmental Problems", [("yellowing", "yes"), ("wilting", "yes")]),
    rule(3, "Standing water", [("standing_water", "yes")], "Empty the saucer or outer pot after drainage. Do not leave the plant standing in water.", ["S1"], "Bottom watering", kind="Care action"),
    rule(4, "Mineral salt buildup", [("salt_crust", "yes"), ("brown_tips", "yes")], "Check drainage first. Flush accumulated salts only if water can drain freely; otherwise repot in suitable fresh mix.", ["S1"], "Watering to minimize soluble salt buildup"),
    rule(5, "Softened water risk", [("softened_water", "yes")], "Use a suitable water source that has not been chemically softened to reduce mineral accumulation.", ["S1"], "Watering to minimize soluble salt buildup", kind="Care action"),
    rule(6, "Insufficient light", [("stretched", "yes"), ("low_light", "yes")], "Move gradually toward light levels suitable for the species; avoid a sudden change to strong sun.", ["S2"], "Spindly growth; Bleached or whitened leaves"),
    rule(7, "Sunburn", [("bleached", "yes"), ("stronger_sun", "yes")], "Reduce excessive exposure and acclimatise the plant gradually to stronger light.", ["S2"], "Bleached or whitened leaves"),
    rule(8, "Cold injury", [("blackening", "yes"), ("cold_exposure", "yes")], "Move the plant away from cold exposure and maintain temperatures suitable for its species.", ["S2"], "Leaf or shoot blackening"),
    rule(9, "Grey mould", [("gray_fuzz", "yes")], "Remove affected ageing leaves or flowers and improve air circulation.", ["S2"], "Fuzzy gray growth on leaves or flowers"),
    rule(10, "Root rot", [("wilting", "yes"), ("dark_soft_roots", "yes")], "Assess root damage. If healthy portions remain, remove rotten roots and repot in fresh suitable mix; seek help for extensive damage.", ["S3"], "Root Rot & Stem Rot"),
    rule(11, "Powdery mildew", [("white_powder", "yes")], "Improve ventilation and remove severely affected leaves.", ["S3"], "Powdery Mildew"),
    rule(12, "Fungal leaf spot", [("brown_spots", "yes")], "Remove affected material, improve airflow and avoid splashing water on foliage.", ["S3"], "Fungal Leaf Spots", [("target_rings", "yes"), ("black_dots", "yes")]),
    rule(13, "Bacterial leaf spot", [("water_soaked", "yes"), ("spot_ooze", "yes")], "Remove affected material, avoid crowding and do not splash water onto foliage.", ["S3"], "Bacterial Leaf Spots"),
    rule(14, "Aphids", [("pear_insects", "yes")], "Inspect closely. Physically remove small infestations or rinse a plant sturdy enough to tolerate it.", ["S4"], "Aphids; Non-Chemical Control", pest=True),
    rule(15, "Mealybugs", [("cotton_insects", "yes")], "Inspect leaf joints and undersides; physically remove individual insects and recheck the plant.", ["S4"], "Mealybugs; Non-Chemical Control", pest=True),
    rule(16, "Spider mites", [("pale_speckles", "yes"), ("fine_webbing", "yes")], "Inspect leaf undersides. Rinse suitable sturdy plants to dislodge mites and monitor for recurrence.", ["S4"], "Spider Mites", pest=True),
    rule(17, "Scale insects", [("shell_bumps", "yes")], "Inspect the bumps closely. Physically remove small infestations without damaging plant tissue.", ["S5"], "Scale insects: Appearance, Detection and Management", pest=True),
    rule(18, "Whiteflies", [("white_flies", "yes")], "Inspect leaf undersides and confirm the pest before choosing a control method.", ["S2", "S5"], "Leaf yellowing; Whiteflies; Managing common pests", pest=True),
    rule(19, "Fungus gnats", [("dark_flies", "yes"), ("soil", "wet")], "Review watering and drainage. Allow drying appropriate to the species between waterings.", ["S2", "S5"], "Flying insects; Water plants properly", pest=True),
    rule(20, "Separate the affected plant", [("pest_suspected", True)], "Keep this plant separate from other houseplants while the suspected infestation is investigated and controlled.", ["S4"], "Non-Chemical Control", kind="Care action"),
]

QUESTION_MAP = {q["key"]: q for q in QUESTIONS}

def condition_text(condition):
    key, value = condition
    if key == "pest_suspected":
        return "A pest rule (R14 to R19) has matched"
    q = QUESTION_MAP[key]
    display = dict(q["choices"])[value]
    return f'{q["label"]} = {display}'

def rule_text(r):
    parts = [condition_text(c) for c in r["all"]]
    if r["any"]:
        parts.append("(" + " OR ".join(condition_text(c) for c in r["any"]) + ")")
    return " AND ".join(parts)
