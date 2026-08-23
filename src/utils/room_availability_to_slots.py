from api.schemas.room import RoomAvailability


def room_availability_to_slots(*, occurence_rules: list[RoomAvailability], start_slot: int, end_slot: int) -> set[int]:
    slots: set[int] = set()

    for occ_rule in occurence_rules:
        



    return slots