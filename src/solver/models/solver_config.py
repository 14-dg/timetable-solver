from dataclasses import dataclass
from enum import Enum


class ConstraintState(Enum):
    IGNORED = 0  
    SOFT = 1     
    HARD = 2

@dataclass
class SolverConfig:
    # Feature Toggles (Hard/Soft/Ignored)
    check_room_equipment: ConstraintState = ConstraintState.HARD
    check_room_capacity: ConstraintState = ConstraintState.HARD
    check_teacher_max_hours: ConstraintState = ConstraintState.HARD
    check_travel_times: ConstraintState = ConstraintState.HARD
    
    avoid_hohlstunden: ConstraintState = ConstraintState.SOFT
    avoid_randzeiten: ConstraintState = ConstraintState.SOFT
    constant_room: ConstraintState = ConstraintState.SOFT
    avoid_mandatory_overlap_diff_semesters: ConstraintState = ConstraintState.SOFT
    avoid_elective_overlap: ConstraintState = ConstraintState.SOFT
    maximize_teacher_preferences: ConstraintState = ConstraintState.SOFT

    # User-Defined Weights (Greifen nur bei State = SOFT)
    weight_hohlstunden: int = 10
    weight_randzeiten: int = 5
    weight_constant_room: int = 8
    weight_elective_overlap: int = 15
    weight_teacher_preferences: int = 5