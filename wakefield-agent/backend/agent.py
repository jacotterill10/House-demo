import re


from tools import (
    search_properties,
    get_property_details,
    compare_properties,
    save_shortlist,
    get_shortlist,
)

AREAS = ["city centre", "outwood", "sandal", "horbury", "stanley", "alverthorpe"]
PROPERTY_TYPES = ["house", "flat", "semi-detached", "detached"]

def extract_budget(message: str):
    match = re.search(r"(\d{2,3})\s?k", message.lower())
    if match:
        return int(match.group(1)) * 1000

    match = re.search(r"£?\s?(\d{5,6})", message.lower())
    if match:
        return int(match.group(1))

    return None

def extract_beds(message: str):
    match = re.search(r"(\d+)[ -]?bed", message.lower())
    if match:
        return int(match.group(1))
    return None

def extract_area(message: str):
    msg = message.lower()
    for area in AREAS:
        if area in msg:
            return area.title()
    return None

def extract_property_type(message: str):
    msg = message.lower()
    for ptype in PROPERTY_TYPES:
        if ptype in msg:
            return ptype.title() if ptype != "semi-detached" else "Semi-detached"
    return None

def extract_ids(message: str):
    return [int(x) for x in re.findall(r"\b\d+\b", message)]

async def run_agent(message: str) -> str:
    msg = message.lower()

    if "shortlist" in msg and ("show" in msg or "view" in msg):
        items = get_shortlist()
        if not items:
            return "Your shortlist is empty."
        return "Your shortlist contains:\n" + "\n".join(
            f"{item['id']}: {item['title']} for £{item['price']:,}"
            for item in items
        )

    if "save" in msg or "shortlist" in msg:
        ids = extract_ids(message)
        if ids:
            result = save_shortlist(ids[0])
            return f"Saved property {ids[0]} to shortlist. Current shortlist: {result['shortlist']}"
        return "Tell me which property ID to save, for example: save property 2."

    if "compare" in msg:
        ids = extract_ids(message)
        if len(ids) < 2:
            return "Please give at least 2 property IDs to compare, for example: compare 1 and 5."
        items = compare_properties(ids[:3])
        valid_items = [item for item in items if "error" not in item]
        if not valid_items:
            return "I could not find those property IDs."

        lines = []
        for item in valid_items:
            lines.append(
                f"{item['id']}: {item['title']} — £{item['price']:,}, "
                f"{item['beds']} beds, {item['type']}, "
                f"{item['commute']} mins commute, score {item['value_score']}"
            )
        return "Comparison:\n" + "\n".join(lines)

    if "details" in msg or "tell me about" in msg:
        ids = extract_ids(message)
        if ids:
            item = get_property_details(ids[0])
            if "error" in item:
                return "I could not find that property."
            return (
                f"{item['title']}\n"
                f"Price: £{item['price']:,}\n"
                f"Area: {item['area']}\n"
                f"Bedrooms: {item['beds']}\n"
                f"Bathrooms: {item['baths']}\n"
                f"Type: {item['type']}\n"
                f"Size: {item['size']} sqft\n"
                f"Commute: {item['commute']} mins\n"
                f"Value score: {item['value_score']}\n"
                f"Price per bed: £{item['price_per_bed']:,}\n"
                f"Price per sqft: £{item['price_per_sqft']:,}"
            )

    budget = extract_budget(message)
    beds = extract_beds(message)
    area = extract_area(message)
    property_type = extract_property_type(message)

    results = search_properties(
        area=area,
        max_price=budget,
        min_beds=beds,
        property_type=property_type,
    )

    if results:
        top = results[:3]
        reply = ["Here are the best matches I found:"]
        for item in top:
            reply.append(
                f"{item['id']}: {item['title']} — £{item['price']:,}, "
                f"{item['beds']} beds, {item['type']}, {item['area']}, "
                f"{item['commute']} mins commute"
            )

        best = top[0]
        reply.append(
            f"\nBest pick: {best['title']} because it has a strong balance of price, size, bedrooms, and commute."
        )
        return "\n".join(reply)

    return (
        "I could not find a matching property. Try something like:\n"
        "- Find me 2-bed homes under £200k\n"
        "- Show me flats in City Centre\n"
        "- Compare 1 and 5\n"
        "- Save property 2 to shortlist"
    )