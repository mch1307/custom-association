import importlib.util
import sys
import types
from pathlib import Path


odoo_module = types.ModuleType('odoo')
odoo_module.http = types.SimpleNamespace(
    Controller=type('Controller', (), {}),
    route=lambda *args, **kwargs: (lambda f: f),
)
sys.modules.setdefault('odoo', odoo_module)

odoo_http_module = types.ModuleType('odoo.http')
odoo_http_module.request = object()
sys.modules.setdefault('odoo.http', odoo_http_module)


def _load_controller_module():
    module_path = Path(__file__).resolve().parents[1] / 'controllers' / 'portal_household.py'
    spec = importlib.util.spec_from_file_location('association_family.portal_household', module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_partner_supports_firstname_field_detection():
    module = _load_controller_module()
    controller = module.AssociationFamilyPortal

    no_firstname_model = types.SimpleNamespace(_fields={'name': object()})
    with_firstname_model = types.SimpleNamespace(_fields={'name': object(), 'firstname': object()})

    assert not controller._partner_supports_firstname(no_firstname_model)
    assert controller._partner_supports_firstname(with_firstname_model)


def test_build_member_vals_skips_firstname_when_field_not_supported():
    module = _load_controller_module()
    controller = module.AssociationFamilyPortal

    vals = controller._build_member_vals(
        {
            'name': 'Doe',
            'firstname': 'Jane',
            'email': 'jane@example.com',
            'phone': '123',
            'birthdate_date': '2000-01-01',
            'x_household_role': 'child',
            'x_costume_size': 'S',
        },
        include_firstname=False,
        parent_id=42,
    )

    assert vals['name'] == 'Doe'
    assert vals['parent_id'] == 42
    assert 'firstname' not in vals


def test_build_member_vals_includes_firstname_when_supported():
    module = _load_controller_module()
    controller = module.AssociationFamilyPortal

    vals = controller._build_member_vals(
        {
            'name': 'Doe',
            'firstname': 'Jane',
        },
        include_firstname=True,
    )

    assert vals['name'] == 'Doe'
    assert vals['firstname'] == 'Jane'
