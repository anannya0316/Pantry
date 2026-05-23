"""Tests for services/notifications_service.py."""
import pytest
from unittest.mock import patch, MagicMock
from datetime import date, timedelta

_SVC = "services.notifications_service"


def _item(name, quantity=1, purchase_date=None, shelf_life_days=30):
    return {
        "display_name": name,
        "quantity": quantity,
        "purchase_date": purchase_date or date.today().isoformat(),
        "shelf_life_days": shelf_life_days,
    }


class TestGetNotifications:
    def _setup(self, inv=None, meals=None, recent_log=None, log_count=0, profile=None, enriched=None):
        """Return a context manager tuple for all 5 patches."""
        return (
            patch(f"{_SVC}.inventory_collection"),
            patch(f"{_SVC}.meal_plans_collection"),
            patch(f"{_SVC}.nutrition_logs_collection"),
            patch(f"{_SVC}.profiles_collection"),
            patch(f"{_SVC}.enrich_with_shelf_life"),
        )

    def test_no_data_returns_no_plan_and_no_logs_notifications(self):
        from services.notifications_service import get_notifications
        with (
            patch(f"{_SVC}.inventory_collection") as mock_inv,
            patch(f"{_SVC}.meal_plans_collection") as mock_meals,
            patch(f"{_SVC}.nutrition_logs_collection") as mock_logs,
            patch(f"{_SVC}.profiles_collection") as mock_profiles,
            patch(f"{_SVC}.enrich_with_shelf_life", return_value=[]),
        ):
            mock_inv.find_one.return_value = None
            mock_meals.find_one.return_value = None
            mock_logs.find_one.return_value = None
            mock_logs.count_documents.return_value = 0
            mock_profiles.find_one.return_value = None
            result = get_notifications("u1")
        ids = [n["id"] for n in result]
        assert "meal_no_plan" in ids
        assert "nutrition_no_logs" in ids

    def test_expired_item_generates_danger_notification(self):
        from services.notifications_service import get_notifications
        old_date = (date.today() - timedelta(days=10)).isoformat()
        item = _item("Milk", quantity=1, purchase_date=old_date, shelf_life_days=5)
        with (
            patch(f"{_SVC}.inventory_collection") as mock_inv,
            patch(f"{_SVC}.meal_plans_collection") as mock_meals,
            patch(f"{_SVC}.nutrition_logs_collection") as mock_logs,
            patch(f"{_SVC}.profiles_collection") as mock_profiles,
            patch(f"{_SVC}.enrich_with_shelf_life", return_value=[item]),
        ):
            mock_inv.find_one.return_value = {"items": [item]}
            mock_meals.find_one.return_value = {}
            mock_logs.find_one.return_value = MagicMock()
            mock_profiles.find_one.return_value = {
                "goals": ["x"], "diet": "veg", "allergies": ["none"]
            }
            result = get_notifications("u1")
        danger = [n for n in result if n["severity"] == "danger"]
        assert len(danger) == 1
        assert danger[0]["id"] == "inv_expired"

    def test_multiple_expired_items_uses_count_in_title(self):
        from services.notifications_service import get_notifications
        old_date = (date.today() - timedelta(days=15)).isoformat()
        items = [
            _item("Milk", quantity=1, purchase_date=old_date, shelf_life_days=5),
            _item("Yogurt", quantity=1, purchase_date=old_date, shelf_life_days=7),
        ]
        with (
            patch(f"{_SVC}.inventory_collection") as mock_inv,
            patch(f"{_SVC}.meal_plans_collection") as mock_meals,
            patch(f"{_SVC}.nutrition_logs_collection") as mock_logs,
            patch(f"{_SVC}.profiles_collection") as mock_profiles,
            patch(f"{_SVC}.enrich_with_shelf_life", return_value=items),
        ):
            mock_inv.find_one.return_value = {"items": items}
            mock_meals.find_one.return_value = {}
            mock_logs.find_one.return_value = MagicMock()
            mock_profiles.find_one.return_value = {
                "goals": ["x"], "diet": "veg", "allergies": ["none"]
            }
            result = get_notifications("u1")
        danger = next(n for n in result if n["id"] == "inv_expired")
        assert "2" in danger["title"]

    def test_out_of_stock_item_generates_shopping_notification(self):
        from services.notifications_service import get_notifications
        item = _item("Rice", quantity=0, shelf_life_days=365)
        with (
            patch(f"{_SVC}.inventory_collection") as mock_inv,
            patch(f"{_SVC}.meal_plans_collection") as mock_meals,
            patch(f"{_SVC}.nutrition_logs_collection") as mock_logs,
            patch(f"{_SVC}.profiles_collection") as mock_profiles,
            patch(f"{_SVC}.enrich_with_shelf_life", return_value=[item]),
        ):
            mock_inv.find_one.return_value = {"items": [item]}
            mock_meals.find_one.return_value = {}
            mock_logs.find_one.return_value = MagicMock()
            mock_profiles.find_one.return_value = {
                "goals": ["x"], "diet": "veg", "allergies": ["none"]
            }
            result = get_notifications("u1")
        shopping = [n for n in result if n["type"] == "shopping"]
        assert len(shopping) == 1
        assert shopping[0]["id"] == "inv_out_of_stock"

    def test_expiring_soon_generates_warning_notification(self):
        from services.notifications_service import get_notifications
        yesterday = (date.today() - timedelta(days=1)).isoformat()
        item = _item("Yogurt", quantity=2, purchase_date=yesterday, shelf_life_days=2)
        with (
            patch(f"{_SVC}.inventory_collection") as mock_inv,
            patch(f"{_SVC}.meal_plans_collection") as mock_meals,
            patch(f"{_SVC}.nutrition_logs_collection") as mock_logs,
            patch(f"{_SVC}.profiles_collection") as mock_profiles,
            patch(f"{_SVC}.enrich_with_shelf_life", return_value=[item]),
        ):
            mock_inv.find_one.return_value = {"items": [item]}
            mock_meals.find_one.return_value = {}
            mock_logs.find_one.return_value = MagicMock()
            mock_profiles.find_one.return_value = {
                "goals": ["x"], "diet": "veg", "allergies": ["none"]
            }
            result = get_notifications("u1")
        warnings = [n for n in result if n["severity"] == "warning" and n["type"] == "inventory"]
        assert len(warnings) == 1
        assert "Yogurt" in warnings[0]["title"]

    def test_incomplete_profile_generates_warning(self):
        from services.notifications_service import get_notifications
        with (
            patch(f"{_SVC}.inventory_collection") as mock_inv,
            patch(f"{_SVC}.meal_plans_collection") as mock_meals,
            patch(f"{_SVC}.nutrition_logs_collection") as mock_logs,
            patch(f"{_SVC}.profiles_collection") as mock_profiles,
            patch(f"{_SVC}.enrich_with_shelf_life", return_value=[]),
        ):
            mock_inv.find_one.return_value = None
            mock_meals.find_one.return_value = {}
            mock_logs.find_one.return_value = MagicMock()
            mock_profiles.find_one.return_value = {"goals": [], "diet": "", "allergies": []}
            result = get_notifications("u1")
        profile_notifs = [n for n in result if n["id"] == "profile_incomplete"]
        assert len(profile_notifs) == 1
        assert profile_notifs[0]["severity"] == "warning"

    def test_no_recent_logs_but_has_past_logs_generates_not_logged(self):
        from services.notifications_service import get_notifications
        with (
            patch(f"{_SVC}.inventory_collection") as mock_inv,
            patch(f"{_SVC}.meal_plans_collection") as mock_meals,
            patch(f"{_SVC}.nutrition_logs_collection") as mock_logs,
            patch(f"{_SVC}.profiles_collection") as mock_profiles,
            patch(f"{_SVC}.enrich_with_shelf_life", return_value=[]),
        ):
            mock_inv.find_one.return_value = None
            mock_meals.find_one.return_value = {}
            mock_logs.find_one.return_value = None
            mock_logs.count_documents.return_value = 5
            mock_profiles.find_one.return_value = {
                "goals": ["x"], "diet": "veg", "allergies": ["none"]
            }
            result = get_notifications("u1")
        ids = [n["id"] for n in result]
        assert "nutrition_not_logged" in ids
        assert "nutrition_no_logs" not in ids

    def test_returns_list(self):
        from services.notifications_service import get_notifications
        with (
            patch(f"{_SVC}.inventory_collection") as mock_inv,
            patch(f"{_SVC}.meal_plans_collection") as mock_meals,
            patch(f"{_SVC}.nutrition_logs_collection") as mock_logs,
            patch(f"{_SVC}.profiles_collection") as mock_profiles,
            patch(f"{_SVC}.enrich_with_shelf_life", return_value=[]),
        ):
            mock_inv.find_one.return_value = None
            mock_meals.find_one.return_value = {}
            mock_logs.find_one.return_value = MagicMock()
            mock_profiles.find_one.return_value = {
                "goals": ["x"], "diet": "veg", "allergies": ["none"]
            }
            result = get_notifications("u1")
        assert isinstance(result, list)
