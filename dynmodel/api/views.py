from django.contrib import admin

from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.reverse import reverse

from .models import TYPE_DEFINITIONS
from .serializers import generic_serializer
from .dynamicmodel import DynamicModel


@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'update table': reverse('update-table', request=request, args=[1]),
        'create table': reverse('create-table', request=request, format=format),
        'create row': reverse('create-row', request=request, format=format, args=[1]),
        'list rows': reverse('list-rows', request=request, format=format, args=[1]),
    })


def convert_type(in_type: str) -> str:
    for typ_id, name in TYPE_DEFINITIONS:
        if name == in_type:
            return typ_id


def convert_input_types(in_type: dict[str, str]) -> dict[str, str]:
    fields = {}
    for name, fld_type in in_type.items():
        fields[name] = convert_type(fld_type)

    return fields


@api_view(['POST'])
@parser_classes([JSONParser])
def create_table(request):
    """
    Creates table from json file with 'name': 'type' pairs.
    Allowed types: 'boolean', 'character', 'integer'
    Example:

    {
        "make": "character",
        "model": "character",
        "year": "integer",
        "valid_license": "boolean"
    }

    """
    fields = convert_input_types(request.data)

    mdl = DynamicModel()
    id = mdl.create_model(fields)

    admin.site.register(mdl.as_model())

    return Response({'id': id}, status=201)


@api_view(['PUT'])
@parser_classes([JSONParser])
def update_table(request, id):
    """
    Updates dynamic model table from json file with 'name': 'type' pairs.
    Allowed types: 'boolean', 'character', 'integer'
    Example:

    {
        "make": "character",
        "model": "character",
        "year": "character",
        "make_year": "integer",
        "licence_valid_year": "integer"
    }

    """
    fields = convert_input_types(request.data)
    mdl = DynamicModel(id)
    mdl.update_model(fields)

    admin.site.register(mdl.as_model())

    return Response({'id': id})


@api_view(['POST'])
@parser_classes([JSONParser])
def create_row(request, id):
    """"
    Example:
    {
        "make": "toyota",
        "model": "corolla",
        "year": 2012,
        "valid_license": true
    }
    """
    model_cls = DynamicModel(id).as_model()

    serializer_cls = generic_serializer(model_cls)
    serializer = serializer_cls(data=request.data)

    if serializer.is_valid():
        obj = serializer.save()
        return Response({'id': obj.id}, status=201)

    return Response({'error': serializer.errors}, status=400)


@api_view(['GET'])
def list_rows(request, id):
    model_cls = DynamicModel(id).as_model()

    serializer_cls = generic_serializer(model_cls)
    rows = model_cls.objects.all()
    serializer = serializer_cls(rows, many=True)

    return Response(serializer.data)
