from django.db import models


def ResourceObject(instance: models.Model):  # noqa
    return {
        "type": instance._meta.model.__name__.capitalize(),
        "id": instance.id,
    }


def ObjectFromDict(type_name: str, data: dict = None):  # noqa
    data = data or {}
    record_id = 0
    if "id" in data:
        record_id = data.pop("id")
    return {
        "data": {
            "type": type_name,
            "id": record_id,
            "attributes": {
                k: v if not isinstance(v, models.Model) else ResourceObject(v)
                for k, v in data.items()
            },
        },
    }
