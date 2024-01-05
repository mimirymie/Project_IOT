import json

import asyncio
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from telegram import Bot

from .models import Dht11  # Assurez-vous d'importer le modèle Dht11
from django.utils import timezone
import csv
from django.http import HttpResponse
from django.utils import timezone
from django.http import JsonResponse
from datetime import timedelta
import datetime
import telepot

import csv
from django.shortcuts import render
from django.http import HttpResponse
import datetime
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
import json
from django.conf import settings
from django.core.mail import send_mail


def table(request):
    derniere_ligne = Dht11.objects.last()
    derniere_date = Dht11.objects.last().dt
    delta_temps = timezone.now() - derniere_date
    days = delta_temps.days
    seconds = delta_temps.seconds + days * 86400
    if seconds >= 60:
        minutes = seconds // 60
        seconds = seconds % 60
        if minutes >= 60:
            heures = minutes // 60
            minutes %= 60
            if heures >= 24:
                jours = heures // 24
                heures %= 24
                if jours == 1:
                    temps_ecoule = str(jours) + ' day ' + str(heures) + ' h ' + str(minutes) + ' min ' + str(
                        seconds) + ' sc' + ' ago'
                else:
                    temps_ecoule = str(jours) + ' days ' + str(heures) + ' h ' + str(minutes) + ' min ' + str(
                        seconds) + ' sc' + ' ago'
            else:
                temps_ecoule = str(heures) + ' h ' + str(minutes) + ' min ' + str(seconds) + ' sc ' + 'ago'
        else:
            temps_ecoule = str(minutes) + ' min ' + str(seconds) + ' sc' + ' ago'

    else:
        temps_ecoule = str(seconds) + ' sc' + ' ago'

    valeurs = {'date': temps_ecoule, 'id': derniere_ligne.id, 'temp': derniere_ligne.temp,
               'hum': derniere_ligne.hum}
    return render(request, 'value.html', {'valeurs': valeurs})



def download_csv(request):
    model_values = Dht11.objects.all()
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="dht.csv"'
    writer = csv.writer(response)
    writer.writerow(['id', 'temp', 'hum', 'dt'])
    liste = model_values.values_list('id', 'temp', 'hum', 'dt')
    for row in liste:
        writer.writerow(row)
    return response
#pour afficher navbar de template
def index_view(request):
    return render(request, 'index.html')

#pour afficher les graphes
def graphique(request):
    return render(request, 'Chart.html')

# récupérer toutes les valeur de température et humidity sous forme un #fichier json
def chart_data(request):
    dht = Dht11.objects.all()

    data = {
        'temps': [Dt.dt for Dt in dht],
        'temperature': [Temp.temp for Temp in dht],
        'humidity': [Hum.hum for Hum in dht]
    }
    return JsonResponse(data)

#pour récupérer les valeurs de température et humidité de dernier 24h
# et envoie sous forme JSON
def chart_data_heure(request):
    now = timezone.now()
    dht = Dht11.objects.filter(dt__hour=now.time().hour, dt__day=now.date().day, dt__month=now.date().month,
                               dt__year=now.date().year)
    return JsonResponse(limitingPoints(dht))


def chart_data_jour(request):
    now = timezone.now().date()  # Assuming you want to filter by the current date
    dht = Dht11.objects.filter(dt__day=now.day, dt__month=now.month, dt__year=now.year)
    return JsonResponse(limitingPoints(dht))


def chart_data_mois(request):
    now = timezone.now().date()  # Assuming you want to filter by the current date
    dht = Dht11.objects.filter(dt__month=now.month, dt__year=now.year)
    return JsonResponse(limitingPoints(dht))


def limitingPoints(dht):
    temps = [Dt.dt for Dt in dht]
    temperatures = [Temp.temp for Temp in dht]
    humidities = [Hum.hum for Hum in dht]
    length = len(temps)
    print(length)
    if length >= 30:
        samplesRate = length // 30
        print(samplesRate)
        temps = temps[::samplesRate]
        print(len(temps))
        humidities = humidities[::samplesRate]
        print(len(humidities))
        temperatures = temperatures[::samplesRate]
        print(len(temperatures))
    return {
        'temps': temps,
        'temperature': temperatures,
        'humidity': humidities,
    }
def sendtele(request, message):
    async def send_telegram_message(token, chat_id, message_text):
        bot = Bot(token=token)
        await bot.send_message(chat_id=chat_id, text=message_text)

    bot_token = '6810467864:AAEqt3A0Wbn9VuUI7wBV0AkIaR9qZ6ssIso'
    chat_id = '5368258598'
    message_text = message

    asyncio.run(send_telegram_message(bot_token, chat_id, message_text))
def sendmail(message):
    subject = 'Alerte DHT'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = ['maryamben200217@gmail.com']
    send_mail(subject, message, email_from, recipient_list)
@csrf_exempt
def receive_data(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            temperature = data['temp']
            humidity = data['hum']
            Dht11.objects.create(temp=temperature, hum=humidity)
            if temperature>17:
                sendtele(request, "la température dépasse la normale")
                sendmail("la température dépasse la normale")
            if humidity>60:
                sendtele(request, "l'humidité dépasse la normale")
                sendmail("l'humidité dépasse la normale")
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    else:
        return JsonResponse({'status': 'error', 'message': 'Only POST requests are allowed'})