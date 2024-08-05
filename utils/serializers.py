from rest_framework import serializers

class ForexConvertSerializer(serializers.Serializer):
    from_currency = serializers.CharField(max_length=3)
    to_currency = serializers.CharField(max_length=3)
    date = serializers.DateField()
    amount = serializers.DecimalField(max_digits=20, decimal_places=2)
    
    