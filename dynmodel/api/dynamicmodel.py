from django.conf import settings
from django.db import connection, models, transaction

from .models import DynamicField, DynamicTable


class DynamicModel:
    # there are diffent options how to resolve table naming, simplest one is to use std prefix and id
    # another option is to use uuid as table name and store one in DynamicTable for mapping
    def __init__(self, model_id: int = None):
        self.tableprefix = settings.DYNAMIC_MODELS['DYNAMIC_TABLE_PREFIX']

        self.model_name = f'{self.tableprefix}{model_id}'
        self.model_id = model_id
        self.model_class = None

    def create_model(self, fields: dict[str, str]) -> int:
        new_table = DynamicTable.objects.create()
        self.model_id = new_table.id
        self.model_name = f'{self.tableprefix}{self.model_id}'

        for name, fld_type in fields.items():
            DynamicField.objects.create(name=name, fld_type=fld_type, table_def=new_table)
        
        model_fields = self._convert_to_types(fields)
        self._build_model_cls(model_fields)
        self._create_table()

        return self.model_id

    @transaction.atomic
    def update_model(self, new_fields: dict[str, str]) -> None:
        if not self.model_class:
            fields = DynamicField.objects.filter(table_def_id=self.model_id)
            model_def = self._convert_qs_types(fields)
            self._build_model_cls(model_def)            

        change_type = []
        remove_column = []

        for field in fields:
            if field.name not in new_fields.keys():
                remove_column.append(field.name)
            elif new_fields[field.name] == field.fld_type:
                del new_fields[field.name]
            elif new_fields[field.name] != field.fld_type:
                change_type.append( (field.name, field.fld_type, new_fields[field.name],) )
                del new_fields[field.name]

        # changing table definition is rare operation, so there is no need to make it batch operation
        for column in change_type:
            self._change_column_type(*column)

        for name, fld_type in new_fields.items():
            self._add_column(name, fld_type)

        for col in remove_column:
            self._remove_column(col, model_def[col])

        # force model recreation
        self.model_class = None

    def as_model(self) -> models.Model:
        if not self.model_class:
            fields = DynamicField.objects.filter(table_def_id=self.model_id)
            model_def = self._convert_qs_types(fields)

            self._build_model_cls(model_def)

        return self.model_class

    def _change_column_type(self, column_name: str, old_type: str, new_type: str) -> None:
        old_column = self._convert_to_field(old_type, column_name)
        old_column.set_attributes_from_name(column_name)
        new_column = self._convert_to_field(new_type, column_name)
        new_column.set_attributes_from_name(column_name)

        with connection.schema_editor() as schema_editor:
            schema_editor.alter_field(self.model_class, old_column, new_column)

        o = DynamicField.objects.filter(table_def_id=self.model_id, name=column_name).get()
        o.fld_type = new_type
        o.save()

    def _remove_column(self, column_name: str, column: models.Field) -> None:
        with connection.schema_editor() as schema_editor:
            schema_editor.remove_field(self.model_class, column)

        DynamicField.objects.filter(table_def_id=self.model_id, name=column_name).delete()

    def _add_column(self, column_name: str, column_type: str) -> None:
        column = self._convert_to_field(column_type, column_name)
        column.set_attributes_from_name(column_name)

        with connection.schema_editor() as schema_editor:
            schema_editor.add_field(self.model_class, column)

        DynamicField.objects.create(name=column_name, fld_type=column_type, table_def_id=self.model_id)

    def _convert_to_types(self, fields: dict[str, str]) -> dict[str, models.Field]:
        result = {}

        for name, fld_type_id in fields.items():
            result[name] = self._convert_to_field(fld_type_id)

        return result
    
    def _convert_qs_types(self, fields: models.QuerySet) -> dict[str, models.Field]:
        result = {}

        for field in fields:
            result[field.name] = self._convert_to_field(field.fld_type)

        return result
        
    def _convert_to_field(self, in_type: str, name: str = None) -> models.Field:
        if in_type == 'c':
            max_length = settings.DYNAMIC_MODELS['DEFAULT_CHAR_LENGHT']
            return models.CharField(null=True, blank=True, max_length=max_length, name=name)
        
        if in_type == 'i':
            return models.IntegerField(null=True, blank=True, name=name)
        
        if in_type == 'b':
            return models.BooleanField(null=True, blank=True, name=name)
        
        raise ValueError(f'Unknown type "{in_type}"')

    def _build_model_cls(self, fields_dict: dict[str, models.Field]) -> None:
        class Meta:
            app_label = 'api'
            db_table = self.model_name

        attrs = {'__module__': 'api.models', 'Meta': Meta}
        attrs.update(fields_dict)

        self.model_class = type(self.model_name, (models.Model,), attrs)

    def _create_table(self):
        with connection.schema_editor() as schema_editor:
            schema_editor.create_model(self.model_class)

    def _delete_table(self):
        with connection.schema_editor() as schema_editor:
            schema_editor.delete_model(self.model_class)

