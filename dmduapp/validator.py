from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


# def val_weight(value):
#     if value <0 or value >1:
#         raise ValidationError(
#             _("Weight must be between 0 and 1"),
#             code="invalid",
#             params={"value": value}
#         )
    
# def val_duration(value):
#     if value <0:
#         raise ValidationError(
#             _("Duration must be greater than or equal to 0"),
#             code="invalid",
#             params={"value": value}
#         )

# def val_time(value):
#     if value <0:
#         raise ValidationError(
#             _("Time must be greater than or equal to 0"),
#             code="invalid",
#             params={"value": value}
#         )

def pos_int(value):
    if value < 0:
        raise ValidationError("Cannot be negative")

def max_100(value):
    if value > 100:
        raise ValidationError("Cannot be greater than 100")