from django.db import models


class DynamicTable(models.Model):
    # class with just id column
    pass


TYPE_DEFINITIONS = [('c', 'character',), ('b', 'boolean',), ('i', 'integer')]


class DynamicField(models.Model):

    name = models.CharField(max_length=63)
    fld_type = models.CharField(max_length=1, choices=TYPE_DEFINITIONS)
    table_def = models.ForeignKey(DynamicTable, on_delete=models.CASCADE, related_name="fields")

    class Meta:
        unique_together = (("name", "table_def"),)
