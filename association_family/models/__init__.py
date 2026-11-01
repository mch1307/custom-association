try:
    from . import account_move
    from . import event_registration
    from . import product_template
    from . import res_partner
    from . import sale_order_line
except (ImportError, ModuleNotFoundError):
    pass
