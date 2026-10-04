from dataclasses import dataclass


@dataclass
class RedisCacheExpiryLength:
    """
    Die dauer in Sekunden, wie lange Einträge in Redis gespeichert werden
    """
    pending: int
    completed: int
    failed: int

@dataclass(frozen=True)
class RedisCacheExpiry:
    timetable = RedisCacheExpiryLength(
        pending=60 * 30, # 30 minuten
        completed=60 * 60 * 24 * 2, # 48 stunden / 2 tage
        failed=60 * 15, # 15 minuten
    )


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