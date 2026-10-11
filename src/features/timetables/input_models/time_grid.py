from pydantic import BaseModel, Field


class TimeGrid(BaseModel):
    days: int = Field(
        default=5,
        ge=5,
        le=7,
    )
    slots_per_day: int = Field(
        default=16,
        ge=1,
        le=50,
    )

    @property
    def n_slots(self) -> int:
        """
        gibt gesamte anzahl der slots aus
        """
        return self.days * self.slots_per_day

    def day(self, slot: int) -> int:
        """
        gibt an im wievieltem tag der übergebene slot liegt
        """
        return slot // self.slots_per_day

    def period(self, slot: int) -> int:
        """
        gibt an, der wievielte slot eines tages der übergebene slot ist
        """
        return slot % self.slots_per_day