import requests
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json

ACCESS_TOKEN = 'APP_USR-3223439958553130-070718-7ebda0fea9a4b3c486556755cd48f463-529569186'

@csrf_exempt
def crear_preferencia(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    try:
        data = json.loads(request.body)
        plan = data.get('plan')
        price = data.get('price')
        title = data.get('title')
        user_email = data.get('user_email')

        items = [{
            "title": title,
            "quantity": 1,
            "currency_id": "ARS",
            "unit_price": float(price)
        }]

        preference_data = {
            "items": items,
            "payer": {
                "email": user_email
            },
            "back_urls": {
                "success": "https://scoutgine-frontend.onrender.com/subscripcion.html?status=approved",
                "failure": "https://scoutgine-frontend.onrender.com/subscripcion.html?status=rejected",
                "pending": "https://scoutgine-frontend.onrender.com/subscripcion.html?status=pending"
            },
            "auto_return": "approved",
            "notification_url": "https://scoutgine-frontend.onrender.com/webhook/mercadopago"
        }

        response = requests.post(
            "https://api.mercadopago.com/checkout/preferences",
            json=preference_data,
            headers={"Authorization": f"Bearer {ACCESS_TOKEN}"}
        )

        if response.status_code == 201:
            preference_id = response.json().get('id')
            return JsonResponse({"preference_id": preference_id})
        else:
            return JsonResponse({"error": response.json()}, status=400)
            
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)