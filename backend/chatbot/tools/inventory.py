from datetime import date
from typing import Optional

from pydantic import BaseModel, Field

from dao.inventory_dao import (
    get_user_inventory,
    update_inventory,
    push_inventory_items,
    get_profile,
    get_user,
)
from services.classification_service import classify_item
from constants.meal_constants import VALID_UNITS
from utils.matching_utils import fuzzy_match


# ── Pydantic schemas (used as args_schema in agent.py tool closures) ─────────

class InventoryItemModel(BaseModel):
    display_name: str = Field(..., description="The name of the item in the inventory.")
    quantity: int = Field(..., description="The quantity of the item in the inventory.")
    unit: str = Field(..., description="The unit of measurement for the item quantity.")
    category: str = Field(..., description="The category of the item in the inventory.")
    purchase_date: str = Field(..., description="The date when the item was purchased.")
    status: str = Field(..., description="The status of the item in the inventory.")


class AddInventoryItemInput(BaseModel):
    display_name: str = Field(description="Name of the item, e.g., 'mango'")
    quantity: Optional[int] = Field(default=None, description="How many units to add; if not given, ask user.")
    unit: Optional[str] = Field(default=None, description="Unit of measure, e.g., 'kg', 'pieces'; if not given, ask user.")
    category: Optional[str] = Field(default=None, description="Infer from the item name — e.g., 'Spice' for cumin/pepper, 'Fruit' for oranges/mango, 'Vegetable' for lauki/broccoli, 'Dairy' for milk/cheese.")
    purchase_date: Optional[str] = Field(default=None, description="Use today's date if not stated by the user.")
    status: Optional[str] = Field(default=None, description="Default to 'fresh' for newly added items.")


class UpdateInventoryItemInput(BaseModel):
    display_name: str = Field(description="Name of the item to update.")
    quantity: Optional[int] = Field(default=None, description="New quantity, if user gave it.")
    unit: Optional[str] = Field(default=None, description="New unit, if user gave it.")
    category: Optional[str] = Field(default=None, description="New category, if user gave it.")
    purchase_date: Optional[str] = Field(default=None, description="New purchase date, if user gave it.")
    status: Optional[str] = Field(default=None, description="New status, if user gave it.")


# ── Helpers ───────────────────────────────────────────────────────────────────

def _find_item(items, input_name):
    """Return (index, item) for the best match, or (None, None)."""
    for idx, item in enumerate(items):
        existing_name = item.get("display_name", "").strip().lower()
        aliases = [a.lower() for a in item.get("aliases", [])]
        if input_name == existing_name or input_name in aliases:
            return idx, item

    for idx, item in enumerate(items):
        existing_name = item.get("display_name", "").strip().lower()
        aliases = [a.lower() for a in item.get("aliases", [])]
        if any(fuzzy_match(input_name, c) for c in [existing_name] + aliases):
            return idx, item

    return None, None


# ── Tool implementations ──────────────────────────────────────────────────────

def add_inventory_item(
    user_id: str,
    display_name: str,
    quantity: Optional[int] = None,
    unit: Optional[str] = None,
    category: Optional[str] = None,
    purchase_date: Optional[str] = None,
    status: Optional[str] = None,
):
    """Add an item to inventory. If any required fields are missing,
    the agent should ask the user for them before calling this tool."""
    try:
        if not display_name or not display_name.strip():
            return {"success": False, "error": "Item name cannot be empty."}

        if quantity is None or unit is None:
            missing = (["quantity"] if quantity is None else []) + (["unit"] if unit is None else [])
            return {
                "success": False,
                "error": f"Missing required fields: {', '.join(missing)}.",
                "missing_fields": missing,
            }

        if quantity <= 0:
            return {"success": False, "error": "Quantity must be positive."}

        normalized_unit = unit.lower()
        if normalized_unit not in VALID_UNITS:
            return {"success": False, "error": f"Invalid unit '{unit}'. Valid units are: {sorted(VALID_UNITS)}"}

        input_name = display_name.strip().lower()
        inventory_doc = get_user_inventory(user_id) or {"items": []}
        items = inventory_doc.get("items", [])
        matched_index, matched_item = _find_item(items, input_name)

        profile = get_profile(user_id)
        household_size = profile.get("household_size", 1) if profile else 1

        if matched_index is not None:
            matched_item["quantity"] = quantity
            matched_item["unit"] = normalized_unit
            matched_item["category"] = category or matched_item.get("category", "Other")
            matched_item["purchase_date"] = purchase_date or date.today().isoformat()
            matched_item["status"] = status or "fresh"
            items[matched_index] = matched_item
            update_inventory(user_id, items)
            return {
                "success": True,
                "item": {
                    "display_name": matched_item["display_name"],
                    "quantity": quantity,
                    "unit": normalized_unit,
                    "category": matched_item["category"],
                    "purchase_date": matched_item["purchase_date"],
                    "status": matched_item["status"],
                },
            }

        classified = classify_item(display_name, household_size) or {}
        resolved_name = classified.get("display_name", display_name.title())
        aliases = [input_name] if input_name != resolved_name.lower() else []

        new_item = {
            "display_name": resolved_name,
            "aliases": aliases,
            "quantity": quantity,
            "unit": normalized_unit,
            "category": category or classified.get("category", "Other"),
            "purchase_date": purchase_date or date.today().isoformat(),
            "status": status or "fresh",
        }
        push_inventory_items(user_id, [new_item])

        return {"success": True, "item": new_item}

    except Exception as e:
        return {"success": False, "error": f"Unexpected error: {str(e)}"}


def update_inventory_item(
    user_id: str,
    display_name: str,
    quantity: Optional[int] = None,
    unit: Optional[str] = None,
    category: Optional[str] = None,
    purchase_date: Optional[str] = None,
    status: Optional[str] = None,
):
    """Update an existing inventory item. Only update the fields that are provided."""
    try:
        if not display_name or not display_name.strip():
            return {"success": False, "error": "Item name cannot be empty."}

        inventory_doc = get_user_inventory(user_id)
        if not inventory_doc:
            return {"success": False, "error": "Inventory not found."}

        items = inventory_doc.get("items", [])
        matched_index, matched_item = _find_item(items, display_name.strip().lower())

        if matched_index is None:
            return {"success": False, "error": f"{display_name} was not found in your inventory."}

        updated_fields = {}

        if quantity is not None:
            if quantity < 0:
                return {"success": False, "error": "Quantity cannot be negative."}
            matched_item["quantity"] = quantity
            updated_fields["quantity"] = quantity

        if unit is not None:
            normalized_unit = unit.lower()
            if normalized_unit not in VALID_UNITS:
                return {"success": False, "error": f"Invalid unit '{unit}'. Valid units are: {sorted(VALID_UNITS)}"}
            matched_item["unit"] = normalized_unit
            updated_fields["unit"] = normalized_unit

        if category is not None:
            matched_item["category"] = category
            updated_fields["category"] = category

        if purchase_date is not None:
            matched_item["purchase_date"] = purchase_date
            updated_fields["purchase_date"] = purchase_date

        if status is not None:
            matched_item["status"] = status
            updated_fields["status"] = status

        if not updated_fields:
            return {"success": False, "error": "No fields provided to update."}

        items[matched_index] = matched_item
        update_inventory(user_id, items)

        return {"success": True, "updated_fields": updated_fields}

    except Exception as e:
        return {"success": False, "error": f"Unexpected error: {str(e)}"}


def get_all_inventory_items(user_id: str):
    """Fetch all inventory items."""
    try:
        inventory_doc = get_user_inventory(user_id)
        if not inventory_doc:
            return {"success": True, "items": [], "message": "No inventory items found."}

        return {"success": True, "items": inventory_doc.get("items", [])}

    except Exception as e:
        return {"success": False, "error": f"Unexpected error: {str(e)}"}


# ── Backward-compat alias (used by tool_schemas.py) ─────────────────────────
list_inventory = get_all_inventory_items
