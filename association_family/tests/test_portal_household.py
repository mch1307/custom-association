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


def test_partner_supports_birthdate_field_detection():
    module = _load_controller_module()
    controller = module.AssociationFamilyPortal

    no_birthdate_model = types.SimpleNamespace(_fields={'name': object()})
    with_birthdate_model = types.SimpleNamespace(_fields={'name': object(), 'birthdate_date': object()})

    assert not controller._partner_supports_birthdate(no_birthdate_model)
    assert controller._partner_supports_birthdate(with_birthdate_model)


def test_partner_supports_custom_optional_fields_detection():
    module = _load_controller_module()
    controller = module.AssociationFamilyPortal

    no_custom_fields_model = types.SimpleNamespace(_fields={'name': object()})
    with_custom_fields_model = types.SimpleNamespace(
        _fields={
            'name': object(),
            'x_household_role': object(),
            'x_costume_size': object(),
            'x_membership_status': object(),
        }
    )

    assert not controller._partner_supports_household_role(no_custom_fields_model)
    assert controller._partner_supports_household_role(with_custom_fields_model)
    assert not controller._partner_supports_costume_size(no_custom_fields_model)
    assert controller._partner_supports_costume_size(with_custom_fields_model)
    assert not controller._partner_supports_membership_status(no_custom_fields_model)
    assert controller._partner_supports_membership_status(with_custom_fields_model)


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
    assert 'birthdate_date' not in vals
    assert 'x_household_role' not in vals
    assert 'x_costume_size' not in vals


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


def test_build_member_vals_includes_birthdate_when_supported():
    module = _load_controller_module()
    controller = module.AssociationFamilyPortal

    vals = controller._build_member_vals(
        {
            'name': 'Doe',
            'birthdate_date': '2000-01-01',
        },
        include_birthdate=True,
    )

    assert vals['name'] == 'Doe'
    assert vals['birthdate_date'] == '2000-01-01'


def test_build_member_vals_includes_custom_fields_when_supported():
    module = _load_controller_module()
    controller = module.AssociationFamilyPortal

    vals = controller._build_member_vals(
        {
            'name': 'Doe',
            'x_household_role': 'child',
            'x_costume_size': 'M',
        },
        include_household_role=True,
        include_costume_size=True,
    )

    assert vals['name'] == 'Doe'
    assert vals['x_household_role'] == 'child'
    assert vals['x_costume_size'] == 'M'
