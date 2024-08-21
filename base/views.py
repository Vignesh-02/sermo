from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.db.models import Q
from .models import Room, Topic, Message, User
from .forms import RoomForm, UserForm, MyUserCreationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout

# rooms = [
#     {'id': 1, 'name': 'Hello'},
#     {'id': 2, 'name': 'Fello'},
# ]

def loginPage(request):

    page = 'login'
    # not requiring a user to login again
    if request.user.is_authenticated:
        return redirect('home')


    if request.method == 'POST':
        email = request.POST.get('email').lower()
        password = request.POST.get('password')
        
        try:
            user = User.objects.get(email=email)
        except:
            messages.error(request, 'User does not exist')
        
        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Email or password does not exist')
    
    context = {'page': page}
    return render(request, 'base/login_register.html', context)

def logoutUser(request):
    # The logout function deletes the session id from the cookies
    logout(request)
    return redirect('home')

def registerPage(request):
        # page = 'register'
        form = MyUserCreationForm()

        if request.method == 'POST':
            form = MyUserCreationForm(request.POST)
            if form.is_valid():
                # saving the form and freezing it
                # we use commit = False to access the user object
                user = form.save(commit=False)
                user.username = user.username.lower()
                user.save()
                login(request, user)
                return redirect('home')
            else:
                messages.error(request, 'An error occurred during registration')

        context = {'form': form}
        return render(request, 'base/login_register.html', context)

# Create your views here.
def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    # i in icontains makes it case sensitive
    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q) |
        Q(host__username__icontains=q)
    )
    topics = Topic.objects.all()[0:5]
    # this is faster than the python len method
    room_count = rooms.count()
    room_messages = Message.objects.filter(Q(room__topic__name__icontains=q))


    context = {'rooms': rooms, 'topics': topics, 'room_count': room_count, 
               'room_messages': room_messages}
    return render(request, 'base/home.html', context)

def room(request, pk):
    room = Room.objects.get(id=pk)
    # querying child objects of a specific room

    # give the set of messages related to this specific room

    # order it in descending order
    room_messages = room.message_set.all()
    participants = room.participants.all()
    # for k in rooms:

    #     if k['id'] == int(pk):
            # setting dictionary key value pair to the matching room

    if request.method == "POST":
        message = Message.objects.create(
            user = request.user,
            room = room,
            body = request.POST.get('body')
        )
        # adding the participants to the room
        room.participants.add(request.user)

        return redirect('room', pk=room.id)
    
    context = {'room': room, 'room_messages': room_messages, 'participants': participants}
    return render(request, 'base/room.html', context)

def userProfile(request, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    topics = Topic.objects.all() 
    context = {'user': user, 'rooms': rooms, 'room_messages': room_messages, 'topics': topics}
    return render(request, 'base/profile.html',  context)



@login_required(login_url='/login')
def createRoom(request):
    form = RoomForm()
    topics = Topic.objects.all()
    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        
        Room.objects.create(
            host=request.user,
            topic=topic,
            name=request.POST.get('name'),
            description=request.POST.get('description')
        )
        # form = RoomForm(request.POST)
        # reques.POST has the data that we will send from frontend to backend
        # if form.is_valid():
        #     room = form.save(commit=False)
        #     room.host = request.user
        #     room.save()
            # using the name from the view
        return redirect('home')

    context = {'form': form, 'topics': topics}
    return render(request, 'base/room_form.html', context)

@login_required(login_url='/login')
def updateRoom(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)
    topics = Topic.objects.all()

    print('room deets', room.topic)
    # Only the correct  user can edit it
    if request.user != room.host:
        return HttpResponse('You are not allowed here!')


    if request.method == "POST":
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        room.name =  request.POST.get('name')
        room.topic = topic
        room.description = request.POST.get('description')
        room.save()
        return redirect('home')

    context = {'form': form, 'topics': topics, 'room': room}
    return render(request, 'base/room_form.html', context)

@login_required(login_url='/login')
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)

        # Only the correct  user can delete it
    if request.user != room.host:
        return HttpResponse('You are not allowed here!')
    
    if request.method == 'POST':
        room.delete()
        return redirect('home')
    context = {'obj':room}
    return render(request, 'base/delete.html', context)

@login_required(login_url='/login')
def updateMessage(request, pk):
    message = Message.objects.get(id=pk)
    
    # Only the correct user can edit it
    if request.user != message.user:
        return HttpResponse('You are not allowed here!')

    if request.method == "POST":
        message.body = request.POST.get('body')
        message.save()
        return redirect('room', pk=message.room.id)
    
    context = {'message': message}
    return render(request, 'base/edit.html', context)

    

@login_required(login_url='/login')
def deleteMessage(request, pk):
    message = Message.objects.get(id=pk)

    print('message', message)
        # Only the correct  user can delete it
    if request.user != message.user:
        return HttpResponse('You are not allowed here!')
    

    if request.method == 'POST':
        message.delete()
        return redirect('home')
    context = {'obj':message}
    return render(request, 'base/delete.html', context)

@login_required(login_url='login')
def updateUser(request):
    
    user = request.user
    form = UserForm(instance=user)

    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user-profile', pk=user.id)

    return render(request, 'base/update-user.html', {'form': form})


def topicsPage(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    topics = Topic.objects.filter(name__icontains=q)
    return render(request, 'base/topics.html', {'topics': topics})
 
def activityPage(request):
    room_messages = Message.objects.all()
    return render(request, 'base/activity.html',{'room_messages': room_messages})