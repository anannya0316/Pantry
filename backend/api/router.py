from api.routes.auth import (
    router as auth_router
)

from api.routes.profile import (
    router as profile_router
)

from api.routes.inventory import (
    router as inventory_router
)

from api.routes.meal_plan import (
    router as meal_plan_router
)

from api.routes.nutrition import (
    router as nutrition_router
)

from api.routes.onboarding import (
    router as onboarding_router
)

from api.routes.shelf_life import (
    router as shelf_life_router
)

from api.routes.notifications import (
    router as notifications_router
)

from chatbot.route import (
    router as chatbot_router
)

def register_routes(app):

    app.include_router(
        auth_router,
        prefix="/auth"
    )

    app.include_router(
        profile_router,
        prefix="/profile"
    )

    app.include_router(
        inventory_router,
        prefix="/inventory"
    )
    
    app.include_router(
        meal_plan_router,
        prefix="/meal-plan"
    )

    app.include_router(
        nutrition_router,
        prefix="/nutrition"
    )

    app.include_router(
        onboarding_router,
        prefix="/onboarding"
    )

    app.include_router(
        shelf_life_router,
        prefix="/shelf-life"
    )

    app.include_router(
        notifications_router,
        prefix="/notifications"
    )

    app.include_router(
        chatbot_router,
        prefix="/recipes"
    )