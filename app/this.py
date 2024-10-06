from importlib.metadata import requires
from django.utils import timezone
import math
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
# from .models import Files
from multiprocessing import context
from urllib import request, response
from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import qrcode
from django.urls import include
from .models import Admin, Calsheet,CEMSData, Gallery, Manuals,StandardInstruments,Activities,Message,Notifications,SafetyMoment,Todo,Report
import string
import random
from datetime import datetime,timedelta,date
import datetime as dt
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
import fileinput
from openai import OpenAI
from django.http import JsonResponse
from django.conf import settings
import os
now =timezone.now()
current_date = datetime.now()
current_year = current_date.year
current_month = current_date.month
current_month_name = datetime.now().strftime("%B")

from datetime import datetime, timedelta
from django.utils.timezone import now
from collections import defaultdict

def get_weekly_power_data():
    # Get today's date
    today = now().date()

    # Calculate the start of the week (Monday)
    start_of_week = today - timedelta(days=today.weekday())

    # Initialize dictionary for both units
    unit31_power_data = defaultdict(float)
    unit32_power_data = defaultdict(float)

    for day_offset in range(7):
        current_day = start_of_week + timedelta(days=day_offset)
        # Set default power to 0 for days in the future
        day_key = current_day.strftime('%a')  
        
        if current_day > today:
            unit31_power_data[day_key] = 0.0
            unit32_power_data[day_key] = 0.0
        else:
            # Fetch data for the current day for unit31 and unit32
            day_data = CEMSData.objects.filter(date=current_day).first()
            if day_data:
                # Use 0.0 if the database value is None
                unit31_power_data[day_key] = day_data.unit31_power if day_data.unit31_power is not None else 0.0
                unit32_power_data[day_key] = day_data.unit32_power if day_data.unit32_power is not None else 0.0
            else:
                # If no data, set power to 0
                unit31_power_data[day_key] = 0.0
                unit32_power_data[day_key] = 0.0

    return {
        'unit31': dict(unit31_power_data),
        'unit32': dict(unit32_power_data)
    }



def DB(request):
    takeAction()
    admin=Admin.objects.all()
    calsheet=Calsheet.objects.all()
    cems=CEMSData.objects.all()
    manuals=Manuals.objects.all()
    todo=Todo.objects.all()
    report=Report.objects.all()
    gallery=Gallery.objects.all()
    messages=Message.objects.all()
    activities=Activities.objects.all()
    notifications=Notifications.objects.all()
    stdins=StandardInstruments.objects.all()
    if SafetyMoment.objects.exists():
        if SafetyMoment.objects.filter(month=current_month,year=current_year).exists():
            safety_moment = SafetyMoment.objects.get(month=current_month)
            today = date.today()
            tomorrow = today + timedelta(days=1)
            today_day = today.day
            tomorrow_day = tomorrow.day
            today_topic = getattr(safety_moment, f'day_{today_day}_topic', 'No topic assigned')
            today_facilitator = getattr(safety_moment, f'day_{today_day}_user', 'No facilitator assigned')

            tomorrow_topic = getattr(safety_moment, f'day_{tomorrow_day}_topic', 'No topic assigned')
            tomorrow_facilitator = getattr(safety_moment, f'day_{tomorrow_day}_user', 'No facilitator assigned')

            saftymoment = {
                'today_topic': today_topic,
                'today_facilitator': today_facilitator,
                'tomorrow_topic': tomorrow_topic,
                'tomorrow_facilitator': tomorrow_facilitator,
            }
        else:
            safety_moment=None
    else:
        safety_moment=None
    context={
    'calsheets':calsheet,
    'cems':cems,
    'gallery':gallery,
    'chatmessage':messages,
    'activities':activities,
    'notifications':notifications,
    'manuals':manuals,
    'user':request.user,
    'admins':admin,
    'reports':report,
    'stdins':stdins,
    'todo':todo,
    'unit31_power':(get_weekly_power_data())['unit31'],
    'unit32_power':(get_weekly_power_data())['unit32'],
    'safety_moment':safety_moment,
    'current_month_name':current_month_name,
    'current_path':request.path,
    'current_year':current_year,
    'saftymoment':saftymoment,
    }
    return context
def getDatatime(to):
    return datetime.now()+timedelta(days=int(to))
def inputToDateTime(input):
    date_time_string =input+" "+"00:00:00"
    date_time_obj = datetime.strptime(date_time_string,'%Y-%m-%d %H:%M:%S')
    return(date_time_obj)
def codeGen(size,type):
    chars=type + string.digits
    return ''.join(random.choice(chars) for _ in range(size))

def takeAction():
    pass
    cems_items = CEMSData.objects.all()
    now = timezone.now()
    for item in cems_items:
        item_dt = item.dt
        if (now - item_dt) > timedelta(hours=6):
            item.modify = False
            item.save()
def create_activities(request,type,action,tag,personal):
    by=request.user.username
    colors = ['primary', 'secondary', 'success', 'danger', 'warning', 'info', 'dark','light']
    color=0
    if type =='cals' or type =='cal':
        color=0
    elif type=='cems' or type=='cemss':
        color=1
    elif type=='gallery':
        color=2
    elif type=='manual':
        color=3
    elif type=='stdins':
        color=4

    else:
        color= random.randint(0,7)
    random_color =colors[color]
    act=Activities.objects.create(
        by=by,
        type=type,
        tag=tag,
        personal=personal,
        action=action,
        color=random_color
    )
    act.save()
def create_notification(by,message,tag,fr='all'):
    
    if fr=='all':
        for  admin in Admin.objects.all():
            id=admin.id
            notifs =1+int(admin.admin_notifications)
            new_notif=Notifications.objects.create(
            fr=admin.username,
            message=message,
            tag=tag,
            by=by,
            )
            new_notif.save()
            Admin.objects.filter(id=int(id)).update(admin_notifications=notifs)
    else:
        admin =Admin.objects.get(username=fr)
        notifs =1+int(admin.admin_notifications)
        
        new_notif=Notifications.objects.create(
            fr=admin.username,
            message=message,
            tag=tag,
            by=by,
            )
        new_notif.save()
        Admin.objects.filter(username=fr).update(admin_notifications=notifs)
# Set your API key
client = OpenAI(api_key='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')  # Ensure your API key is set in environment variables

def generate_subtopics(main_topic):
    try:
        # Create a chat completion request
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": f"Generate 30 safety subtopics based on the main topic: {main_topic}",
                }
            ],
            model="gpt-3.5-turbo",  # or "gpt-4" if you have access
        )

        # Extract the generated text from the response
        generated_text = chat_completion.choices[0].message['content']
        subtopics = generated_text.strip().split("\n")  # Split by new lines

        return JsonResponse({
            'status': 'success',
            'subtopics': subtopics
        })

    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        })

def test_gpt():
    try:
        from openai import OpenAI

        client = OpenAI(
            # This is the default and can be omitted
            api_key='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',
        )

        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": "Say this is a test",
                }
            ],
            model="gpt-3.5-turbo",
        )

    except Exception as e:
        print("Error occurred:", e)
        return response
def send_text_email(subject, to_email, text_content):
    from_email = 'PODA'
    # Create the email
    email = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
    # Send the email
    email.send()
def send_html_email(subject, to_email, template_name, context):
    from_email = settings.DEFAULT_FROM_EMAIL
    # HTML content
    html_content = render_to_string(template_name, context)
    # Plain text content
    text_content = strip_tags(html_content)
    # Create the email
    email = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
    email.attach_alternative(html_content, "text/html")
    # Send the email
    email.send()
