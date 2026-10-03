from dataclasses import dataclass


@dataclass(frozen=True)
class RedisCacheExpiry:
    """
    Die dauer in Sekunden, wie lange Einträge in Redis gespeichert werden
    """
    timetable: int = 60 * 60 * 24 # 24 stunden


dataclass(frozen=True)
class SolverSettings:
    DEFAULT_SOLVER_TIMEOUT: int = 60 # 60 Sekunden

@dataclass(frozen=True)
class Constants:
    """
    Hardcodierte Systemkonstanten
    """
    redis_cache_expiry = RedisCacheExpiry()
    SOLVER_SETTINGS = SolverSettings()


CONSTANTS = Constants()