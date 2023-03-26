from rest_framework import serializers


def generic_serializer(model_instance):
    class GenericSerializer(serializers.ModelSerializer):
        class Meta:
            model = model_instance
            fields = '__all__'

    return GenericSerializer