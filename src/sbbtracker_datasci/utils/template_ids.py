import copy

def replace_template_ids(state):
    copied = copy.deepcopy(state)
    for playerid in copied:
        for character in copied[playerid]:
            templateid = character.content_id
            is_golden = character.is_golden if hasattr(character, "is_golden") else False
            actually_is_golden = is_golden if isinstance(is_golden, bool) else is_golden == "True"
            character.content_id = get_card_art_name(templateid, actually_is_golden)
            if hasattr(character, "health") and character.health <= 0:
                character.content_id = ""
    return copied
