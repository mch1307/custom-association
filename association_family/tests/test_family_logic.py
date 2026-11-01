import importlib.util
import sys
import types
from datetime import date
from pathlib import Path


odoo_module = types.ModuleType('odoo')
odoo_module.api = types.SimpleNamespace(
    depends=lambda *args, **kwargs: (lambda f: f),
    model=lambda f: f,
    model_create_multi=lambda f: f,
    constrains=lambda *args, **kwargs: (lambda f: f),
)
odoo_module.fields = types.SimpleNamespace(
    Selection=lambda *args, **kwargs: None,
    Date=lambda *args, **kwargs: None,
    Many2one=lambda *args, **kwargs: None,
    Many2many=lambda *args, **kwargs: None,
    Integer=lambda *args, **kwargs: None,
    Char=lambda *args, **kwargs: None,
    Text=lambda *args, **kwargs: None,
    Boolean=lambda *args, **kwargs: None,
)
odoo_module.models = types.SimpleNamespace(Model=type('Model', (), {}))
sys.modules.setdefault('odoo', odoo_module)

exceptions_module = types.ModuleType('odoo.exceptions')
exceptions_module.UserError = Exception
exceptions_module.ValidationError = Exception
sys.modules.setdefault('odoo.exceptions', exceptions_module)


def _load_module(file_name, dotted_name):
    module_path = Path(__file__).resolve().parents[1] / 'models' / file_name
    spec = importlib.util.spec_from_file_location(dotted_name, module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


res_partner_module = _load_module('res_partner.py', 'association_family.res_partner')
sale_order_line_module = _load_module('sale_order_line.py', 'association_family.sale_order_line')
account_move_module = _load_module('account_move.py', 'association_family.account_move')
event_registration_module = _load_module('event_registration.py', 'association_family.event_registration')


def test_compute_household_size_flags_counts_active_members_only():
    size = res_partner_module.ResPartner.compute_household_size_flags([True, False, True])
    assert size == 3


def test_sale_order_line_member_validation_allows_manager_or_child():
    assert sale_order_line_module.SaleOrderLine.is_member_allowed(10, 10, 15)
    assert sale_order_line_module.SaleOrderLine.is_member_allowed(10, 99, 10)
    assert not sale_order_line_module.SaleOrderLine.is_member_allowed(10, 99, 15)


def test_pick_event_participant_id_uses_selected_participants_then_fallback():
    picker = sale_order_line_module.SaleOrderLine.pick_event_participant_id
    assert picker([11, 12], 10, 0) == 11
    assert picker([11, 12], 10, 1) == 12
    assert picker([11, 12], 10, 5) == 12
    assert picker([], 10, 0) == 10


def test_membership_end_date_adds_months():
    end_date = account_move_module.AccountMove.compute_membership_end_date(date(2026, 1, 1), 12)
    assert end_date >= date(2026, 12, 25)


def test_event_registration_assignment_uses_selected_members():
    assignment = event_registration_module.EventRegistration._assign_line_registrations_to_participants

    class FakeReg:
        def __init__(self, reg_id, partner_id):
            self.id = reg_id
            self.partner_id = types.SimpleNamespace(id=partner_id)
            self.create_date = None

        def sudo(self):
            return self

        def write(self, vals):
            self.partner_id = types.SimpleNamespace(id=vals['partner_id'])

    class FakeRegistrations(list):
        @property
        def ids(self):
            return [r.id for r in self]

        def sorted(self, _key):
            return FakeRegistrations(sorted(self, key=lambda r: r.id))

    line = types.SimpleNamespace(
        event_participant_ids=types.SimpleNamespace(ids=[21, 22]),
        member_id=types.SimpleNamespace(id=20),
        event_registration_ids=FakeRegistrations([FakeReg(1, 20), FakeReg(2, 20)]),
        pick_event_participant_id=sale_order_line_module.SaleOrderLine.pick_event_participant_id,
    )
    new_regs = FakeRegistrations([line.event_registration_ids[0], line.event_registration_ids[1]])

    assignment(None, line, new_regs)

    assert line.event_registration_ids[0].partner_id.id == 21
    assert line.event_registration_ids[1].partner_id.id == 22
