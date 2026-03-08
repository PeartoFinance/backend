"""
Sync all tools from tools_data_enabled.json into the database.
Inserts missing tools and updates is_implemented / enabled flags for existing ones.
Run from the backend directory:
    python3 migrations/sync_tools_from_json.py
"""
import os
import sys
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from models.base import db
from models.settings import ToolSettings

JSON_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    'frontend', 'tools_data_enabled.json'
)


def sync_tools():
    with open(JSON_PATH, 'r') as f:
        tools_json = json.load(f)

    app = create_app()
    with app.app_context():
        added = updated = skipped = 0

        for entry in tools_json:
            slug = entry.get('tool_slug', '').strip()
            name = entry.get('tool_name', '').strip()
            category = entry.get('category', 'General').strip()
            enabled = bool(entry.get('enabled', True))
            is_implemented = bool(entry.get('is_implemented', False))
            order_index = int(entry.get('order_index', 100))
            country_code = entry.get('country_code', 'GLOBAL') or 'GLOBAL'

            if not slug:
                continue

            existing = ToolSettings.query.filter_by(tool_slug=slug).first()
            if existing:
                changed = False
                if existing.is_implemented != is_implemented:
                    existing.is_implemented = is_implemented
                    changed = True
                if existing.enabled != enabled:
                    existing.enabled = enabled
                    changed = True
                if changed:
                    updated += 1
                    print(f'  ~ Updated: {slug}')
                else:
                    skipped += 1
            else:
                new_tool = ToolSettings(
                    tool_slug=slug,
                    tool_name=name,
                    category=category,
                    enabled=enabled,
                    is_implemented=is_implemented,
                    order_index=order_index,
                    country_code=country_code,
                )
                db.session.add(new_tool)
                added += 1
                print(f'  + Added: {slug}')

        db.session.commit()
        print(f'\nDone — Added: {added}, Updated: {updated}, Skipped (unchanged): {skipped}')


if __name__ == '__main__':
    sync_tools()
