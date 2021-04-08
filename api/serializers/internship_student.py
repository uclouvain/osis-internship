from rest_framework import serializers

from base.models.student import Student


class InternshipStudentSerializer(serializers.ModelSerializer):

    first_name = serializers.CharField(read_only=True, source='person.first_name')
    last_name = serializers.CharField(read_only=True, source='person.last_name')

    class Meta:
        model = Student
        fields = ['uuid', 'first_name', 'last_name']
