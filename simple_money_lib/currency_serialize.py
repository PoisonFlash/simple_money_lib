import json
import tempfile
from pathlib import Path

from simple_money_lib.errors import CurrencySerializationError

_DATA_DIR = Path(__file__).parent / "data"
_PREDEFINED_FILE = _DATA_DIR / "predefined_currencies.json"
_USER_FILE = _DATA_DIR / "user_currencies.json"

def load_currencies():
    """Load predefined and user-defined currencies."""
    predefined = _load_predefined_currencies()
    user_defined = _load_user_currencies()
    return predefined, user_defined

def _load_predefined_currencies():
    """Load mandatory predefined currencies, failing if the file is missing or corrupted."""
    try:
        with open(_PREDEFINED_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        raise CurrencySerializationError(
            f"Critical error: Predefined currencies file not found: {_PREDEFINED_FILE}")
    except json.JSONDecodeError:
        raise CurrencySerializationError(
            f"Critical error: Failed to parse predefined currencies file: {_PREDEFINED_FILE}")

def _load_user_currencies():
    """Load optional user-defined currencies"""
    if not _USER_FILE.exists():
        return {}
    try:
        with open(_USER_FILE, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        raise CurrencySerializationError(
            f"Critical error: Failed to parse user-defined currencies file: {_USER_FILE}")

def save_user_currencies(user_data: dict):
    print(user_data)
    """Save user-defined currencies to JSON safely."""
    try:
        _USER_FILE.parent.mkdir(parents=True, exist_ok=True)
        # Write to a temporary file first
        with tempfile.NamedTemporaryFile('w', delete=False, dir=_USER_FILE.parent, suffix=".json") as temp_file:
            json.dump(user_data, temp_file, indent=4)
            temp_name = temp_file.name
        # Replace the old file with the new one atomically
        Path(temp_name).replace(_USER_FILE)
    except OSError as e:
        raise CurrencySerializationError(f"Unable to save user-defined currencies. Error: {e}")
    except TypeError as e:
        raise CurrencySerializationError(f"User-defined currencies contain unserializable data. Error: {e}")
