from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import ChatMessage

@login_required
def chat_room_view(request, room_name='general'):
    # Get messages for the current room
    messages = ChatMessage.objects.filter(room=room_name).order_by('timestamp')[:50]
    
    # Get distinct available rooms for sidebar list
    available_rooms = ChatMessage.objects.values_list('room', flat=True).distinct()
    # Ensure 'general' is always in the list
    rooms_list = list(set(['general', 'development', 'design'] + list(available_rooms)))

    if request.method == 'POST':
        msg_text = request.POST.get('message')
        new_room = request.POST.get('new_room')
        
        # If user typed a new room name in the creator input
        if new_room:
            room_name = new_room.strip().lower().replace(' ', '-')
            return redirect('chat_room', room_name=room_name)
            
        # If user sent a message
        if msg_text:
            ChatMessage.objects.create(
                sender=request.user,
                room=room_name,
                message=msg_text
            )
            return redirect('chat_room', room_name=room_name)

    return render(request, 'team_chat/room.html', {
        'messages': messages,
        'room_name': room_name,
        'rooms_list': rooms_list,
        'active_tab': 'chat'
    })