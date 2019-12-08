from rest_framework import serializers
from .models import Citizen, Import


class CitizenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Citizen
        fields = [
            'citizen_id',
            'town',
            'street',
            'building',
            'apartment',
            'name',
            'birth_date',
            'gender'
        ]
        #depthПараметр должен быть установлен на целое значение, которое
        #указует на глубину отношений, которые должны быть пройдены, прежде
        #чем возвращаться к плоскому представлению.
        depth = 1
