from .models import Dht11
from .serializers import DHT11serialize
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

@api_view(["GET", "POST"])
def dhtser(request):
    if request.method == "GET":
        all = Dht11.objects.all()
        dataSer = DHT11serialize(all, many=True)
        return Response(dataSer.data)
    elif request.method == "POST":
        serial = DHT11serialize(data=request.data)
        if serial.is_valid():
            serial.save()
            return Response(serial.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serial.id, status=status.HTTP_400_CREATED)