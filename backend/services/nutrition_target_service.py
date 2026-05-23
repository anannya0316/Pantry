from constants.nutrition_constants import (
    GOAL_TARGETS
)


def get_daily_targets(
    goals: list[str]
):
    goals = {
        g.lower().strip()
        for g in (goals or [])
    }

    gain = "gain muscle" in goals

    lose = "lose weight" in goals

    if gain and lose:
        return GOAL_TARGETS[
            "eat_healthier"
        ]

    if gain:
        return GOAL_TARGETS[
            "gain_muscle"
        ]

    if lose:
        return GOAL_TARGETS[
            "lose_weight"
        ]

    return GOAL_TARGETS[
        "eat_healthier"
    ]