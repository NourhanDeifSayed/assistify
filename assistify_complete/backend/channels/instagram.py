import requests
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json
from chatbot.models import Conversation, Message, Customer

class InstagramManager:
    def __init__(self):
        self.access_token = settings.META_ACCESS_TOKEN
        self.business_account_id = settings.META_BUSINESS_ACCOUNT_ID
        self.api_version = 'v18.0'
        self.base_url = f'https://graph.instagram.com/{self.api_version}'
    
    def send_message(self, recipient_id, message_text):
        url = f'{self.base_url}/{self.business_account_id}/messages'
        
        payload = {
            'recipient': {'id': recipient_id},
            'message': {'text': message_text},
            'access_token': self.access_token
        }
        
        try:
            response = requests.post(url, json=payload)
            return {'success': response.status_code == 200, 'response': response.json()}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def send_media_message(self, recipient_id, media_type, media_url):
        url = f'{self.base_url}/{self.business_account_id}/messages'
        
        payload = {
            'recipient': {'id': recipient_id},
            'message': {
                'attachment': {
                    'type': media_type,
                    'payload': {'url': media_url}
                }
            },
            'access_token': self.access_token
        }
        
        try:
            response = requests.post(url, json=payload)
            return {'success': response.status_code == 200, 'response': response.json()}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_user_profile(self, user_id):
        url = f'{self.base_url}/{user_id}'
        params = {'fields': 'name,username,profile_picture_url', 'access_token': self.access_token}
        
        try:
            response = requests.get(url, params=params)
            return {'success': response.status_code == 200, 'data': response.json()}
        except Exception as e:
            return {'success': False, 'error': str(e)}

@csrf_exempt
@require_http_methods(['POST', 'GET'])
def instagram_webhook(request):
    if request.method == 'GET':
        verify_token = request.GET.get('hub.verify_token')
        challenge = request.GET.get('hub.challenge')
        
        if verify_token == settings.META_VERIFY_TOKEN:
            return HttpResponse(challenge)
        else:
            return HttpResponse('Invalid verify token', status=403)
    
    try:
        data = json.loads(request.body)
        
        for entry in data.get('entry', []):
            for messaging_event in entry.get('messaging', []):
                sender_id = messaging_event.get('sender', {}).get('id')
                recipient_id = messaging_event.get('recipient', {}).get('id')
                
                if messaging_event.get('message'):
                    message_text = messaging_event['message'].get('text', '')
                    
                    customer, created = Customer.objects.get_or_create(
                        instagram_id=sender_id,
                        defaults={'name': sender_id}
                    )
                    
                    conversation, created = Conversation.objects.get_or_create(
                        customer=customer,
                        channel='instagram',
                        status='active'
                    )
                    
                    message = Message.objects.create(
                        conversation=conversation,
                        sender='customer',
                        content=message_text,
                        metadata={'instagram_from': sender_id}
                    )
        
        return HttpResponse('ok', status=200)
    
    except Exception as e:
        return HttpResponse(f"Error: {str(e)}", status=400)

def handle_instagram_message(message_id, conversation_id, response_text):
    instagram_manager = InstagramManager()
    
    conversation = Conversation.objects.get(id=conversation_id)
    customer = conversation.customer
    
    if customer.instagram_id:
        result = instagram_manager.send_message(customer.instagram_id, response_text)
        return result
    
    return {'success': False, 'error': 'No Instagram ID found'}
