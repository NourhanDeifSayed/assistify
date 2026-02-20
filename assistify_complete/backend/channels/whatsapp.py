from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json
from chatbot.models import Conversation, Message, Customer

class WhatsAppManager:
    def __init__(self):
        self.client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        self.phone_number = settings.TWILIO_PHONE_NUMBER
    
    def send_message(self, to_number, message_body):
        try:
            message = self.client.messages.create(
                from_=f'whatsapp:{self.phone_number}',
                body=message_body,
                to=f'whatsapp:{to_number}'
            )
            return {'success': True, 'message_id': message.sid}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def send_template_message(self, to_number, template_name, parameters=None):
        try:
            message = self.client.messages.create(
                from_=f'whatsapp:{self.phone_number}',
                template={
                    'name': template_name,
                    'language': {'code': 'en_US'},
                    'parameters': {'body': {'text': parameters or []}}
                },
                to=f'whatsapp:{to_number}'
            )
            return {'success': True, 'message_id': message.sid}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def send_media_message(self, to_number, media_url, message_body=None):
        try:
            message = self.client.messages.create(
                from_=f'whatsapp:{self.phone_number}',
                body=message_body,
                media_url=[media_url],
                to=f'whatsapp:{to_number}'
            )
            return {'success': True, 'message_id': message.sid}
        except Exception as e:
            return {'success': False, 'error': str(e)}

@csrf_exempt
@require_http_methods(['POST'])
def whatsapp_webhook(request):
    try:
        data = json.loads(request.body)
        
        incoming_message = data.get('Body')
        from_number = data.get('From', '').replace('whatsapp:', '')
        
        customer, created = Customer.objects.get_or_create(
            whatsapp_id=from_number,
            defaults={'name': from_number}
        )
        
        conversation, created = Conversation.objects.get_or_create(
            customer=customer,
            channel='whatsapp',
            status='active'
        )
        
        message = Message.objects.create(
            conversation=conversation,
            sender='customer',
            content=incoming_message,
            metadata={'whatsapp_from': from_number}
        )
        
        response = MessagingResponse()
        response.message("Message received. Processing...")
        
        return HttpResponse(str(response), content_type='application/xml')
    
    except Exception as e:
        return HttpResponse(f"Error: {str(e)}", status=400)

def handle_whatsapp_message(message_id, conversation_id, response_text):
    whatsapp_manager = WhatsAppManager()
    
    conversation = Conversation.objects.get(id=conversation_id)
    customer = conversation.customer
    
    if customer.whatsapp_id:
        result = whatsapp_manager.send_message(customer.whatsapp_id, response_text)
        return result
    
    return {'success': False, 'error': 'No WhatsApp ID found'}
