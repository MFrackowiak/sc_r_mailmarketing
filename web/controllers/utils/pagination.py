from typing import Dict, Optional


def create_pagination_context(current_page: int, total_pages: int) -> Optional[Dict]:
    if total_pages < 2:
        return None

    next_pages = list(range(current_page + 1, min(current_page + 3, total_pages + 1)))
    prev_pages = list(range(max(current_page - 2, 1), current_page))

    return {
        "prev": prev_pages,
        "first": current_page != 1 and 1 not in prev_pages,
        "next": next_pages,
        "current": current_page,
        "last": current_page != total_pages and total_pages not in next_pages,
        "total": total_pages,
    }
