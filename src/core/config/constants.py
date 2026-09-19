from dataclasses import dataclass


@dataclass(frozen=True)
class RedisCacheExpiry:
    """
    Die dauer in Sekunden, wie lange Einträge in Redis gespeichert werden
    """
    timetable: int = 60 * 60 * 24 # 24 stunden

@dataclass(frozen=True)
class Constants:
    """
    Hardcodierte Systemkonstanten
    """
    redis_cache_expiry: RedisCacheExpiry = RedisCacheExpiry()


CONSTANTS = Constants()