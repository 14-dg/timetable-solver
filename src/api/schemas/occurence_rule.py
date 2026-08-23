from pydantic import BaseModel


class ApiOccurenceRule(BaseModel):
    duration_slots: int # die dauer des termins in zeitslots
    week_step: int # alle wie viele wochen soll der termin stattfinden. 1 für jede woche, 2 für jede zweite woche
    week_offset: int # wenn die vorlesung alle 3 wochen stattfindet kann man hiermit sagen, ob die vorlesung in woche 1, 2 oder 3 stattfindet