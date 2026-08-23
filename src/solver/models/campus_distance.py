from dataclasses import dataclass


@dataclass(kw_only=True)
class CampusDistance:
    """ Definiert die Fahrzeit in Zeitslots zwischen zwei Campussen """
    from_campus: str
    to_campus: str
    distance: int # in zeitslots. da zeitslots unterschiedlich groß sein können wird die distanz basierend auf der zeitslotlänge berechnet