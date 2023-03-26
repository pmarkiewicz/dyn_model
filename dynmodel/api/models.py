from django.db import models
from typing import Any


class DynamicTable(models.Model):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

        # self._registry = ModelRegistry(self.app_label)
        # model = self._registry.get_model(self.model_name)


TYPE_DEFINITIONS = [('c', 'character',), ('b', 'boolean',), ('i', 'integer')]

class DynamicField(models.Model):

    name = models.CharField(max_length=63)
    fld_type = models.CharField(max_length=1, choices=TYPE_DEFINITIONS)
    table_def = models.ForeignKey(DynamicTable, on_delete=models.CASCADE, related_name="fields")

    class Meta:
        unique_together = (("name", "table_def"),)
