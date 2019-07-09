from re import findall
from typing import Dict

from voluptuous import Invalid

AVAILABLE_DATA = frozenset(
    {"user_id", "name", "id", "first_name", "last_name", "email"}
)


def validate_template(template: str):
    """Simple validator of templates and usage of variables."""
    all_params = findall(r"{([ \w_]*)}", template)

    used_params = set(param for param in all_params)

    if not used_params.issubset(AVAILABLE_DATA):
        raise Invalid(
            f"Used unsupported params: {', '.join(sorted(used_params - AVAILABLE_DATA))}"
        )


def validate_template_schema(data: Dict):
    validate_template(data["template"])
