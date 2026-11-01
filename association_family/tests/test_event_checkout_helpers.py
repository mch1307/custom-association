import importlib.util
import sys
import types
from pathlib import Path


odoo_module = types.ModuleType('odoo')
odoo_module.http = types.SimpleNamespace(route=lambda *args, **kwargs: (lambda f: f))
sys.modules.setdefault('odoo', odoo_module)

odoo_http_module = types.ModuleType('odoo.http')
odoo_http_module.request = object()
sys.modules.setdefault('odoo.http', odoo_http_module)

website_sale_main_module = types.ModuleType('odoo.addons.website_sale.controllers.main')
website_sale_main_module.WebsiteSale = type('WebsiteSale', (), {})
sys.modules.setdefault('odoo.addons.website_sale.controllers.main', website_sale_main_module)


def _load_controller_module():
    module_path = Path(__file__).resolve().parents[1] / 'controllers' / 'cart_event.py'
    spec = importlib.util.spec_from_file_location('association_family.cart_event', module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_normalize_int_ids_skips_invalid_values():
    module = _load_controller_module()
    controller = module.AssociationFamilyWebsiteSale
    assert controller.normalize_int_ids(['1', 'x', 2, None, '3']) == [1, 2, 3]


def test_filter_allowed_ids_keeps_household_members_only():
    module = _load_controller_module()
    controller = module.AssociationFamilyWebsiteSale
    assert controller.filter_allowed_ids([1, 2, 3, 4], [2, 4, 9]) == [2, 4]


def test_filter_allowed_ids_deduplicates_preserving_order():
    module = _load_controller_module()
    controller = module.AssociationFamilyWebsiteSale
    assert controller.filter_allowed_ids([4, 2, 4, 9, 2], [2, 4, 9]) == [4, 2, 9]


def test_is_event_line_true_for_event_or_ticket():
    module = _load_controller_module()
    controller = module.AssociationFamilyWebsiteSale

    event_line = types.SimpleNamespace(_fields={'event_id': True}, event_id=types.SimpleNamespace(id=1), event_ticket_id=False)
    ticket_line = types.SimpleNamespace(_fields={'event_ticket_id': True}, event_id=False, event_ticket_id=types.SimpleNamespace(id=2))
    simple_line = types.SimpleNamespace(_fields={}, event_id=False, event_ticket_id=False)

    assert controller.is_event_line(event_line)
    assert controller.is_event_line(ticket_line)
    assert not controller.is_event_line(simple_line)


def test_confirmation_template_contains_participant_summary_block():
    template_path = Path(__file__).resolve().parents[1] / 'views' / 'website_event_confirmation_templates.xml'
    xml = template_path.read_text(encoding='utf-8')
    assert 'Participants enregistres' in xml
    assert 'line.event_participant_ids' in xml
    assert 'Aucun participant specifie' in xml
