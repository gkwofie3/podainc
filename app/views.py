from django.shortcuts import render,redirect
from django.utils import timezone
from django.http import HttpResponse,JsonResponse
from urllib import request, response
from django.contrib import messages
from .models import Admin, Calsheet,CEMSData, Gallery, Manuals,StandardInstruments,ResetTokens,SafetyMoment,Todo,Report
from . import this
import random
import string
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
import re
import os
from django.shortcuts import get_object_or_404
from django.http import FileResponse
from django.core.files.storage import FileSystemStorage
from django.utils.html import strip_tags
from datetime import datetime,timedelta,date
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
current_date = datetime.now()
current_year = current_date.year
current_month = current_date.month
def email(request):
    # this.send_text_email(
    #     subject='Plain Text Email Subject',
    #     to_email='gideonkwofie4@gmail.com',
    #     text_content='This is a plain text email content from poda'
    # )
    print(request.path)
    return render(request,'mail/rpr.html')
host='http://127.0.0.1:8000'
def generate_random_string(length=8):
    letters = string.ascii_letters + string.digits
    return ''.join(random.choice(letters) for i in range(length))

def test(request):
    return render(request,'403.html')

# Run the test

# logins and auth
def signin(request):
    context=None
    if request.method =="GET" and 'next' in request.GET:
        next =request.GET['next']
    elif request.method =="POST" and 'next' in request.GET:
        next =request.GET['next']
    else:
        next ="/"  
    if request.method =='POST':
        def validate(input):
            return request.POST[input]
        username =validate('username')
        password=validate('password')
        if Admin.objects.filter(username=username).exists() ==False:
            messages.error(request,"The username you entered does not exist")
            return redirect('/login?next='+str(next))
        else:
            user_name=(Admin.objects.get(username=username)).firstname
            user =authenticate(request,username=username,password=password)
            if password =='admin_password':
                return redirect('/reset_request')
            if user is not None:
                login(request,user)
                return redirect(str(next))
            else:
                messages.error(request,f"Dear {user_name}, you entered a wrong password!")
                return redirect('/login?next='+str(next))
    elif request.method=="GET":
        return render(request,'login.html')
    else:
        return render(request,'400.html')
def acclog(request):
    next=request.GET['next']
    return redirect('/login?next='+str(next))
def signout(request):
    logout(request)
    return redirect('/login')
def resetRequest(request):
    if request.method =="GET":
        return render(request,'forgot_password.html')
    elif request.method == "POST":
        username=request.POST["username"]
        email=request.POST["email"]
        if Admin.objects.filter(username=username).exists():
            radmin=Admin.objects.get(username=username)
            if email !=radmin.email:
                messages.error(request,"You entered a wrong email address")
                return redirect(request.path)
            else:
                key =this.codeGen(64,string.ascii_letters)
                subject='PODA - Password Reset'
                url=f'{host}/password-reset/{username}/?key={key}'
                context={
                    'receipient':email,
                    'subject':subject,
                    'url':url,
                    'name':f'{radmin.firstname} {radmin.surname}',
                }
                this.send_html_email(subject, email, 'mail/rpr.html', context)
                resettoken=ResetTokens.objects.create(key=key,token_for=radmin.username)
                resettoken.save()
                messages.info(request,"Reset link has been sent to your email. ")
                return redirect('/login')
                
        else:
            messages.error(request,"This username does not exist")
            return redirect(request.path)
def adminPasswordReset(request,username):
    if request.method =="GET":
        key=request.GET['key']
        if Admin.objects.filter(username=username).exists():
            radmin=Admin.objects.get(username=username)
            if ResetTokens.objects.filter(key=key).exists():
                querykey =ResetTokens.objects.get(key=key)
                is_used =querykey.is_used
                if querykey.is_used ==True:
                    messages.warning(request,"This token has been used. Request for another one.")
                    return redirect('/password_reset_request/')
                else:
                    
                    time =querykey.time
                    diff =(timezone.now() - time).total_seconds()
                    # return HttpResponse(f'{diff},  {15*60 -diff}')
                    if diff <(15*60):
                        if querykey.token_for !=username:
                            messages.warning(request,"The username requested for this token does not match the email received!")
                            return redirect('/password_reset_request/')
                        else:
                            admin=Admin.objects.get(username=username)
                            context={'admin':admin,
                                     'key':key,
                                     }
                            return render(request,'reset.html',context)
                    else:
                        messages.warning(request,"Sorry this token has expired!")
                        return redirect("/password_reset_request/")
            else:
                messages.warning(request,"The username requested for this token does not match the email received!")
                return redirect(request.path)
        else:
            messages.warning(request,"This username does not exist")
            return render(request,'/reset_request/',context='')
    elif request.method == "POST":
        key=request.POST['key']
        password=request.POST['password']
        confirm=request.POST['confirm']
        admin=Admin.objects.get(username=username)
        if password==confirm:
            admin.set_password(password)
            admin.save()
            this.create_activities(request,'admin','You changed  your account password.', 'danger',True)
            ResetTokens.objects.filter(key=key).update(is_used=True)
            messages.success(request,("Your password has been reset successfully!"))
            return redirect("/")
        else:
            messages.warning(request,"Sorry passwords do not match! Try again")
            return redirect(request.path)
# end auth 
@login_required
@login_required
def index(request):
    context=None
    context=this.DB(request)
    return render(request,'index.html',context)
#calibrations
@login_required
def cal(request):
    context=None
    context=this.DB(request)
    return render(request,'cal/index.html',context)
@login_required 
def newcal(request):
    context=None
    context=this.DB(request)
    if request.method=='GET':
        return render(request,'cal/add.html',context)
    elif request.method=='POST':
        tag =request.POST['tag']
        description=request.POST['description']
        process_type=request.POST['process_type']
        inst_type=request.POST['inst_type']
        design_type=request.POST['design_type']
        serial_number=request.POST['serial_number']
        model_number=request.POST['model_number']
        unit=request.POST['unit']
        manufacturer=request.POST['manufacturer']
        deviation_type=request.POST['deviation_type']
        location=request.POST['location']
        lower_limit=float(request.POST['lower_limit'])
        upper_limit=float(request.POST['upper_limit'])
        lower_range=float(request.POST['lower_range'])
        upper_range=float(request.POST['upper_range'])
        af_desire0=float(request.POST['af_desire0'])
        af_desire25=float(request.POST['af_desire25'])
        af_desire50=float(request.POST['af_desire50'])
        af_desire75=float(request.POST['af_desire75'])
        af_desire100=float(request.POST['af_desire100'])
        af_actual0=float(request.POST['af_actual0'])
        af_actual25=float(request.POST['af_actual25'])
        af_actual50=float(request.POST['af_actual50'])
        af_actual75=float(request.POST['af_actual75'])
        af_actual100=float(request.POST['af_actual100'])
        af_error0=float(request.POST['af_error0'])
        af_error25=float(request.POST['af_error25'])
        af_error50=float(request.POST['af_error50'])
        af_error75=float(request.POST['af_error75'])
        af_error100=float(request.POST['af_error100'])
        al_actual0=float(request.POST['al_actual0'])
        al_actual25=float(request.POST['al_actual25'])
        al_actual50=float(request.POST['al_actual50'])
        al_actual75=float(request.POST['al_actual75'])
        al_actual100=float(request.POST['al_actual100'])
        al_error0=float(request.POST['al_error0'])
        al_error25=float(request.POST['al_error25'])
        al_error50=float(request.POST['al_error50'])
        al_error75=float(request.POST['al_error75'])
        al_error100=float(request.POST['al_error100'])
        af_deviation=float(request.POST['af_deviation'])
        al_deviation =float(request.POST['al_deviation'])
        next_cal_due_date=this.getDatatime(183)
        standard_instrument=request.POST['standard_instrument']
        by=(request.user.firstname)+(request.user.surname)
        remarks=request.POST['remarks']
        cal_number=1
        if Calsheet.objects.filter(tag=tag).exists():
            cn=0
            css =Calsheet.objects.filter(tag=tag)
            for item in css:
                cal_number+=1
        new_cal_sheet=Calsheet.objects.create(
            tag =tag,
            description=description,
            process_type=process_type,
            inst_type=inst_type,
            design_type=design_type,
            serial_number=serial_number,
            model_number=model_number,
            unit=unit,
            manufacturer=manufacturer,
            location=location,
            lower_limit=lower_limit,
            upper_limit=upper_limit,
            lower_range=lower_range,
            upper_range=upper_range,
            deviation_type=deviation_type,
            af_desire0=af_desire0,
            af_desire25=af_desire25,
            af_desire50=af_desire50,
            af_desire75=af_desire75,
            af_desire100=af_desire100,
            af_error0=af_error0,
            af_error25=af_error25,
            af_error50=af_error50,
            af_error75=af_error75,
            af_error100=af_error100,
            af_actual0=af_actual0,
            af_actual25=af_actual25,
            af_actual50=af_actual50,
            af_actual75=af_actual75,
            af_actual100=af_actual100,
            al_actual0=al_actual0,
            al_actual25=al_actual25,
            al_actual50=al_actual50,
            al_actual75=al_actual75,
            al_actual100=al_actual100,
            al_error0=al_error0,
            al_error25=al_error25,
            al_error50=al_error50,
            al_error75=al_error75,
            al_error100=al_error100,
            af_deviation=af_deviation,
            al_deviation =al_deviation,
            next_cal_due_date=next_cal_due_date,
            standard_instrument=standard_instrument,
            by=by,
            remarks=remarks,
        )
        new_cal_sheet.save()   
        this.create_activities(request,'cal','You added new cal sheet succcessfully.', 'success',False)
        messages.success(request,'You added new cal sheet succcessfully.')
        return redirect(request.path)
@login_required
def calview(request,tk):
    context=None
    context=this.DB(request)
    sheet=Calsheet.objects.get(id=tk)
    context['sheet'] = sheet
    standard_instrument_id = int(sheet.standard_instrument) if sheet.standard_instrument else None
    if standard_instrument_id:
        try:
            context['sheet_stdin'] = StandardInstruments.objects.get(id=standard_instrument_id)
        except StandardInstruments.DoesNotExist:
            context['sheet_stdin'] = None
    else:
        context['sheet_stdin'] = None

    return render(request,'cal/details.html',context)
@login_required
def caledit(request,tk):
    context=None
    context=this.DB(request)
    sheet=Calsheet.objects.get(id=tk)
    context['sheet']=sheet
    if request.method=='GET':
        return render(request,'cal/edit.html',context)
    elif request.method=='POST':
        tag =request.POST['tag']
        description=request.POST['description']
        process_type=request.POST['process_type']
        inst_type=request.POST['inst_type']
        design_type=request.POST['design_type']
        serial_number=request.POST['serial_number']
        model_number=request.POST['model_number']
        unit=request.POST['unit']
        manufacturer=request.POST['manufacturer']
        deviation_type=request.POST['deviation_type']
        location=request.POST['location']
        lower_limit=float(request.POST['lower_limit'])
        upper_limit=float(request.POST['upper_limit'])
        lower_range=float(request.POST['lower_range'])
        upper_range=float(request.POST['upper_range'])
        af_desire0=float(request.POST['af_desire0'])
        af_desire25=float(request.POST['af_desire25'])
        af_desire50=float(request.POST['af_desire50'])
        af_desire75=float(request.POST['af_desire75'])
        af_desire100=float(request.POST['af_desire100'])
        af_actual0=float(request.POST['af_actual0'])
        af_actual25=float(request.POST['af_actual25'])
        af_actual50=float(request.POST['af_actual50'])
        af_actual75=float(request.POST['af_actual75'])
        af_actual100=float(request.POST['af_actual100'])
        af_error0=float(request.POST['af_error0'])
        af_error25=float(request.POST['af_error25'])
        af_error50=float(request.POST['af_error50'])
        af_error75=float(request.POST['af_error75'])
        af_error100=float(request.POST['af_error100'])
        al_actual0=float(request.POST['al_actual0'])
        al_actual25=float(request.POST['al_actual25'])
        al_actual50=float(request.POST['al_actual50'])
        al_actual75=float(request.POST['al_actual75'])
        al_actual100=float(request.POST['al_actual100'])
        al_error0=float(request.POST['al_error0'])
        al_error25=float(request.POST['al_error25'])
        al_error50=float(request.POST['al_error50'])
        al_error75=float(request.POST['al_error75'])
        al_error100=float(request.POST['al_error100'])
        af_deviation=float(request.POST['af_deviation'])
        al_deviation =float(request.POST['al_deviation'])
        next_cal_due_date=this.getDatatime(183)
        standard_instrument=request.POST['standard_instrument']
        by=(request.user.firstname)+(request.user.surname)
        remarks=request.POST['remarks']
        Calsheet.objects.filter(id=tk).update(
            tag =tag,
            description=description,
            process_type=process_type,
            inst_type=inst_type,
            design_type=design_type,
            serial_number=serial_number,
            model_number=model_number,
            unit=unit,
            manufacturer=manufacturer,
            location=location,
            lower_limit=lower_limit,
            upper_limit=upper_limit,
            lower_range=lower_range,
            upper_range=upper_range,
            deviation_type=deviation_type,
            af_desire0=af_desire0,
            af_desire25=af_desire25,
            af_desire50=af_desire50,
            af_desire75=af_desire75,
            af_desire100=af_desire100,
            af_error0=af_error0,
            af_error25=af_error25,
            af_error50=af_error50,
            af_error75=af_error75,
            af_error100=af_error100,
            af_actual0=af_actual0,
            af_actual25=af_actual25,
            af_actual50=af_actual50,
            af_actual75=af_actual75,
            af_actual100=af_actual100,
            al_actual0=al_actual0,
            al_actual25=al_actual25,
            al_actual50=al_actual50,
            al_actual75=al_actual75,
            al_actual100=al_actual100,
            al_error0=al_error0,
            al_error25=al_error25,
            al_error50=al_error50,
            al_error75=al_error75,
            al_error100=al_error100,
            af_deviation=af_deviation,
            al_deviation =al_deviation,
            next_cal_due_date=next_cal_due_date,
            standard_instrument=standard_instrument,
            by=by,
            remarks=remarks,
        )
        this.create_activities(request,'cal',f'{request.user.username} updated the cal details of cal sheet {id}','info',False)
        messages.success(request,'Cal details updated successfully')
        return redirect(request.path)
@login_required
def stdins(request):
    context=None
    context=this.DB(request)
    stdins=StandardInstruments.objects.all()
    context['stdins']=stdins
    return render(request,'cal/stdins.html',context)
@login_required
def stdinsadd(request):
    context=None
    context=this.DB(request)
    if request.method =='GET':
        return render(request,'cal/stdinsadd.html',context)
    elif request.method =='POST':
        name=request.POST['name']
        manufacturer=request.POST['manufacturer']
        process_type=request.POST['process_type']
        unit=request.POST['unit']
        upper_limit=request.POST['upper_limit']
        lower_limit=request.POST['lower_limit']
        serial_number=request.POST['serial_number']
        model_number=request.POST['model_number']
        last_cal_date=this.inputToDateTime(request.POST['last_cal_date'])
        due_cal_date =this.inputToDateTime(request.POST['due_cal_date'])
        calibrated_by=(request.user.firstname)+(request.user.surname)
        picture=request.FILES['picture']
        new_stdins=StandardInstruments.objects.create(
            name=name,
            manufacturer=manufacturer,
            process_type=process_type,
            unit=unit,
            upper_limit=upper_limit,
            lower_limit=lower_limit,
            serial_number=serial_number,
            model_number=model_number,
            last_cal_date=last_cal_date,
            due_cal_date=due_cal_date,
            calibrated_by=calibrated_by,
            picture=picture,
        )
        new_stdins.save()
        this.create_activities(request,'stdins',f'{request.user.username} added new Standard Instrument {StandardInstruments.objects.last().id}','success',False)
        messages.success(request,'Standard instrument added successfully')
        return redirect(request.path)
@login_required
def stdinsview(request,id):
    context=None
    context=this.DB(request)
    this_stdin=StandardInstruments.objects.get(id=id)
    if request.method =='GET':
        context['this_stdin']=this_stdin
        return render(request,'cal/stdinsdetails.html',context)
    elif request.method =='POST':
        name=request.POST['name']
        manufacturer=request.POST['manufacturer']
        process_type=request.POST['process_type']
        unit=request.POST['unit']
        upper_limit=request.POST['upper_limit']
        lower_limit=request.POST['lower_limit']
        serial_number=request.POST['serial_number']
        model_number=request.POST['model_number']
        if request.POST['last_cal_date']=='':
            last_cal_date=this_stdin.last_cal_date
        else:
            last_cal_date=this.inputToDateTime(request.POST['last_cal_date'])
        if request.POST['due_cal_date'] =='':
            due_cal_date=this_stdin.due_cal_date
        else:
            due_cal_date=this.inputToDateTime(request.POST['due_cal_date'])
        calibrated_by=request.POST['calibrated_by']
        StandardInstruments.objects.filter(id=id).update(
            name=name,
            manufacturer=manufacturer,
            process_type=process_type,
            unit=unit,
            upper_limit=upper_limit,
            lower_limit=lower_limit,
            serial_number=serial_number,
            model_number=model_number,
            last_cal_date=last_cal_date,
            due_cal_date=due_cal_date,
            calibrated_by=calibrated_by,
        )
        this.create_activities(request,'stdins',f'{request.user.username} updated the deatails of the Standard Instrument, {StandardInstruments.objects.last().id}','info',False)
        messages.success(request,'Details updated successfully')
        return redirect(request.path)
@login_required
def cems(request):
    context=None
    context=this.DB(request)
    return render(request,'cems/index.html',context)
    # return render(request,'cems/index.html',context)
@login_required
def cemsadd(request):
    if request.method=='GET':

        context=None
        context=this.DB(request)
        return render(request,'cems/add.html',context)
    elif request.method =='POST':
        unit31_room_temperature = float(request.POST['unit31_room_temperature'])
        unit31_instrument_air_pressure = float(request.POST['unit31_instrument_air_pressure'])
        unit31_sample_flow = float(request.POST['unit31_sample_flow'])
        unit31_vacuum_pressure = float(request.POST['unit31_vacuum_pressure'])
        unit31_chiller_temperature = float(request.POST['unit31_chiller_temperature'])
        unit31_heated_sample_temperature = float(request.POST['unit31_heated_sample_temperature'])
        unit31_nox_analyzer = float(request.POST['unit31_nox_analyzer'])
        unit31_o2_analyzer = float(request.POST['unit31_o2_analyzer'])
        unit31_co_analyzer = float(request.POST['unit31_co_analyzer'])
        unit31_so2_analyzer = float(request.POST['unit31_so2_analyzer'])
        unit31_main_pm_analyzer = float(request.POST['unit31_main_pm_analyzer'])
        unit31_bypass_pm_analyzer = float(request.POST['unit31_bypass_pm_analyzer'])
        unit31_main_deltaflow = float(request.POST['unit31_main_deltaflow'])
        unit31_bypass_deltaflow = float(request.POST['unit31_bypass_deltaflow'])
        unit31_nitrogen_cylinder_pressure = float(request.POST['unit31_nitrogen_cylinder_pressure'])
        unit31_so2_o2_cylinder_pressure = float(request.POST['unit31_so2_o2_cylinder_pressure'])
        unit31_co_nox_cylinder_pressure = float(request.POST['unit31_co_nox_cylinder_pressure'])
        unit32_room_temperature = float(request.POST['unit32_room_temperature'])
        unit32_instrument_air_pressure = float(request.POST['unit32_instrument_air_pressure'])
        unit32_sample_flow = float(request.POST['unit32_sample_flow'])
        unit32_vacuum_pressure = float(request.POST['unit32_vacuum_pressure'])
        unit32_chiller_temperature = float(request.POST['unit32_chiller_temperature'])
        unit32_heated_sample_temperature = float(request.POST['unit32_heated_sample_temperature'])
        unit32_nox_analyzer = float(request.POST['unit32_nox_analyzer'])
        unit32_o2_analyzer = float(request.POST['unit32_o2_analyzer'])
        unit32_co_analyzer = float(request.POST['unit32_co_analyzer'])
        unit32_so2_analyzer = float(request.POST['unit32_so2_analyzer'])
        unit32_main_pm_analyzer = float(request.POST['unit32_main_pm_analyzer'])
        unit32_bypass_pm_analyzer = float(request.POST['unit32_bypass_pm_analyzer'])
        unit32_main_deltaflow = float(request.POST['unit32_main_deltaflow'])
        unit32_bypass_deltaflow = float(request.POST['unit32_bypass_deltaflow'])
        unit32_nitrogen_cylinder_pressure = float(request.POST['unit32_nitrogen_cylinder_pressure'])
        unit32_so2_o2_cylinder_pressure = float(request.POST['unit32_so2_o2_cylinder_pressure'])
        unit32_co_nox_cylinder_pressure = float(request.POST['unit32_co_nox_cylinder_pressure'])
        unit31_power = float(request.POST['unit31_power'])
        unit32_power = float(request.POST['unit32_power'])
        unit32_plc_status = True if request.POST.get('unit32_plc_status') == 'on' else False
        unit32_network_switch_status = True if request.POST.get('unit32_network_switch_status') == 'on' else False
        unit32_hmi_status = True if request.POST.get('unit32_hmi_status') == 'on' else False
        unit32_air_condition_status = True if request.POST.get('unit32_air_condition_status') == 'on' else False
        unit31_plc_status = True if request.POST.get('unit31_plc_status') == 'on' else False
        unit31_network_switch_status = True if request.POST.get('unit31_network_switch_status') == 'on' else False
        unit31_hmi_status = True if request.POST.get('unit31_hmi_status') == 'on' else False
        unit31_air_condition_status = True if request.POST.get('unit31_air_condition_status') == 'on' else False
        remarks = request.POST['remarks']
        by = (request.user.firstname)+(request.user.surname)
        if not all([unit31_room_temperature, unit31_instrument_air_pressure, unit31_sample_flow,
                    unit31_vacuum_pressure, unit31_chiller_temperature, unit31_heated_sample_temperature,
                    unit31_nox_analyzer, unit31_o2_analyzer, unit31_co_analyzer, unit31_so2_analyzer,
                    unit31_main_pm_analyzer, unit31_bypass_pm_analyzer, unit31_main_deltaflow,
                    unit31_bypass_deltaflow, unit31_nitrogen_cylinder_pressure,
                    unit31_so2_o2_cylinder_pressure, unit31_co_nox_cylinder_pressure,
                    unit32_room_temperature, unit32_instrument_air_pressure, unit32_sample_flow,
                    unit32_vacuum_pressure, unit32_chiller_temperature, unit32_heated_sample_temperature,
                    unit32_nox_analyzer, unit32_o2_analyzer, unit32_co_analyzer, unit32_so2_analyzer,
                    unit32_main_pm_analyzer, unit32_bypass_pm_analyzer, unit32_main_deltaflow,
                    unit32_bypass_deltaflow, unit32_nitrogen_cylinder_pressure,
                    unit32_so2_o2_cylinder_pressure, unit32_co_nox_cylinder_pressure,
                    
                    remarks, by]):
            messages.error(request,'you need to fill all fields')
            return redirect(request.path)

            # Save the data
        cems_data = CEMSData(
            unit31_room_temperature=unit31_room_temperature,
            unit31_instrument_air_pressure=unit31_instrument_air_pressure,
            unit31_sample_flow=unit31_sample_flow,
            unit31_vacuum_pressure=unit31_vacuum_pressure,
            unit31_chiller_temperature=unit31_chiller_temperature,
            unit31_heated_sample_temperature=unit31_heated_sample_temperature,
            unit31_nox_analyzer=unit31_nox_analyzer,
            unit31_o2_analyzer=unit31_o2_analyzer,
            unit31_co_analyzer=unit31_co_analyzer,
            unit31_so2_analyzer=unit31_so2_analyzer,
            unit31_main_pm_analyzer=unit31_main_pm_analyzer,
            unit31_bypass_pm_analyzer=unit31_bypass_pm_analyzer,
            unit31_main_deltaflow=unit31_main_deltaflow,
            unit31_bypass_deltaflow=unit31_bypass_deltaflow,
            unit31_nitrogen_cylinder_pressure=unit31_nitrogen_cylinder_pressure,
            unit31_so2_o2_cylinder_pressure=unit31_so2_o2_cylinder_pressure,
            unit31_co_nox_cylinder_pressure=unit31_co_nox_cylinder_pressure,
            unit31_plc_status=unit31_plc_status,
            unit31_network_switch_status=unit31_network_switch_status,
            unit31_hmi_status=unit31_hmi_status,
            unit31_air_condition_status=unit31_air_condition_status,
            unit32_room_temperature=unit32_room_temperature,
            unit32_instrument_air_pressure=unit32_instrument_air_pressure,
            unit32_sample_flow=unit32_sample_flow,
            unit32_vacuum_pressure=unit32_vacuum_pressure,
            unit32_chiller_temperature=unit32_chiller_temperature,
            unit32_heated_sample_temperature=unit32_heated_sample_temperature,
            unit32_nox_analyzer=unit32_nox_analyzer,
            unit32_o2_analyzer=unit32_o2_analyzer,
            unit32_co_analyzer=unit32_co_analyzer,
            unit32_so2_analyzer=unit32_so2_analyzer,
            unit32_main_pm_analyzer=unit32_main_pm_analyzer,
            unit32_bypass_pm_analyzer=unit32_bypass_pm_analyzer,
            unit32_main_deltaflow=unit32_main_deltaflow,
            unit32_bypass_deltaflow=unit32_bypass_deltaflow,
            unit32_nitrogen_cylinder_pressure=unit32_nitrogen_cylinder_pressure,
            unit32_so2_o2_cylinder_pressure=unit32_so2_o2_cylinder_pressure,
            unit32_co_nox_cylinder_pressure=unit32_co_nox_cylinder_pressure,
            unit32_plc_status=unit32_plc_status,
            unit32_network_switch_status=unit32_network_switch_status,
            unit32_hmi_status=unit32_hmi_status,
            unit32_air_condition_status=unit32_air_condition_status,
            remarks=remarks,
            unit31_power=unit31_power,
            unit32_power=unit32_power,
            by=by
        )
        cems_data.save()
        message=f'{request.user.username} added a new CEMS readings {CEMSData.objects.last().id}'
        this.create_activities(request,'cems',message,'success',False)
        this.create_notification(request.user.username,message,'info')
        messages.success(request,'You have successfully added a new CEMS readings')
        return redirect('/cems/')
    else:
        return render(request,'400.html')
@login_required
def cemsdetails(request,id):
    cems_item=CEMSData.objects.get(id=id)
    context=None
    context=this.DB(request)
    context['cems_item']=cems_item
    return render(request,'cems/details.html',context)
@login_required
def cemsedit(request,id):
    cems_item=CEMSData.objects.get(id=id)
    context=None
    context=this.DB(request)
    context['cems_item']=cems_item
    if request.method=='GET':
        return render(request,'cems/edit.html',context)
    elif request.method=='POST':
        action=request.POST['action']
        if action=='edit':
            if cems_item.modify ==True:
                unit31_room_temperature = float(request.POST['unit31_room_temperature'])
                unit31_instrument_air_pressure = float(request.POST['unit31_instrument_air_pressure'])
                unit31_sample_flow = float(request.POST['unit31_sample_flow'])
                unit31_vacuum_pressure = float(request.POST['unit31_vacuum_pressure'])
                unit31_chiller_temperature = float(request.POST['unit31_chiller_temperature'])
                unit31_heated_sample_temperature = float(request.POST['unit31_heated_sample_temperature'])
                unit31_nox_analyzer = float(request.POST['unit31_nox_analyzer'])
                unit31_o2_analyzer = float(request.POST['unit31_o2_analyzer'])
                unit31_co_analyzer = float(request.POST['unit31_co_analyzer'])
                unit31_so2_analyzer = float(request.POST['unit31_so2_analyzer'])
                unit31_main_pm_analyzer = float(request.POST['unit31_main_pm_analyzer'])
                unit31_bypass_pm_analyzer = float(request.POST['unit31_bypass_pm_analyzer'])
                unit31_main_deltaflow = float(request.POST['unit31_main_deltaflow'])
                unit31_bypass_deltaflow = float(request.POST['unit31_bypass_deltaflow'])
                unit31_nitrogen_cylinder_pressure = float(request.POST['unit31_nitrogen_cylinder_pressure'])
                unit31_so2_o2_cylinder_pressure = float(request.POST['unit31_so2_o2_cylinder_pressure'])
                unit31_co_nox_cylinder_pressure = float(request.POST['unit31_co_nox_cylinder_pressure'])
                unit32_room_temperature = float(request.POST['unit32_room_temperature'])
                unit32_instrument_air_pressure = float(request.POST['unit32_instrument_air_pressure'])
                unit32_sample_flow = float(request.POST['unit32_sample_flow'])
                unit32_vacuum_pressure = float(request.POST['unit32_vacuum_pressure'])
                unit32_chiller_temperature = float(request.POST['unit32_chiller_temperature'])
                unit32_heated_sample_temperature = float(request.POST['unit32_heated_sample_temperature'])
                unit32_nox_analyzer = float(request.POST['unit32_nox_analyzer'])
                unit32_o2_analyzer = float(request.POST['unit32_o2_analyzer'])
                unit32_co_analyzer = float(request.POST['unit32_co_analyzer'])
                unit32_so2_analyzer = float(request.POST['unit32_so2_analyzer'])
                unit32_main_pm_analyzer = float(request.POST['unit32_main_pm_analyzer'])
                unit32_bypass_pm_analyzer = float(request.POST['unit32_bypass_pm_analyzer'])
                unit32_main_deltaflow = float(request.POST['unit32_main_deltaflow'])
                unit32_bypass_deltaflow = float(request.POST['unit32_bypass_deltaflow'])
                unit32_nitrogen_cylinder_pressure = float(request.POST['unit32_nitrogen_cylinder_pressure'])
                unit32_so2_o2_cylinder_pressure = float(request.POST['unit32_so2_o2_cylinder_pressure'])
                unit32_co_nox_cylinder_pressure = float(request.POST['unit32_co_nox_cylinder_pressure'])
                unit31_power = float(request.POST['unit31_power'])
                unit32_power = float(request.POST['unit32_power'])
                unit32_plc_status = True if request.POST.get('unit32_plc_status') == 'on' else False
                unit32_network_switch_status = True if request.POST.get('unit32_network_switch_status') == 'on' else False
                unit32_hmi_status = True if request.POST.get('unit32_hmi_status') == 'on' else False
                unit32_air_condition_status = True if request.POST.get('unit32_air_condition_status') == 'on' else False
                unit31_plc_status = True if request.POST.get('unit31_plc_status') == 'on' else False
                unit31_network_switch_status = True if request.POST.get('unit31_network_switch_status') == 'on' else False
                unit31_hmi_status = True if request.POST.get('unit31_hmi_status') == 'on' else False
                unit31_air_condition_status = True if request.POST.get('unit31_air_condition_status') == 'on' else False
                remarks = request.POST['remarks']

                CEMSData.objects.filter(id=id).update(
                unit31_room_temperature=unit31_room_temperature,
                unit31_instrument_air_pressure=unit31_instrument_air_pressure,
                unit31_sample_flow=unit31_sample_flow,
                unit31_vacuum_pressure=unit31_vacuum_pressure,
                unit31_chiller_temperature=unit31_chiller_temperature,
                unit31_heated_sample_temperature=unit31_heated_sample_temperature,
                unit31_nox_analyzer=unit31_nox_analyzer,
                unit31_o2_analyzer=unit31_o2_analyzer,
                unit31_co_analyzer=unit31_co_analyzer,
                unit31_so2_analyzer=unit31_so2_analyzer,
                unit31_main_pm_analyzer=unit31_main_pm_analyzer,
                unit31_bypass_pm_analyzer=unit31_bypass_pm_analyzer,
                unit31_main_deltaflow=unit31_main_deltaflow,
                unit31_bypass_deltaflow=unit31_bypass_deltaflow,
                unit31_nitrogen_cylinder_pressure=unit31_nitrogen_cylinder_pressure,
                unit31_so2_o2_cylinder_pressure=unit31_so2_o2_cylinder_pressure,
                unit31_co_nox_cylinder_pressure=unit31_co_nox_cylinder_pressure,
                unit31_plc_status=unit31_plc_status,
                unit31_network_switch_status=unit31_network_switch_status,
                unit31_hmi_status=unit31_hmi_status,
                unit31_air_condition_status=unit31_air_condition_status,
                unit32_room_temperature=unit32_room_temperature,
                unit32_instrument_air_pressure=unit32_instrument_air_pressure,
                unit32_sample_flow=unit32_sample_flow,
                unit32_vacuum_pressure=unit32_vacuum_pressure,
                unit32_chiller_temperature=unit32_chiller_temperature,
                unit32_heated_sample_temperature=unit32_heated_sample_temperature,
                unit32_nox_analyzer=unit32_nox_analyzer,
                unit32_o2_analyzer=unit32_o2_analyzer,
                unit32_co_analyzer=unit32_co_analyzer,
                unit32_so2_analyzer=unit32_so2_analyzer,
                unit32_main_pm_analyzer=unit32_main_pm_analyzer,
                unit32_bypass_pm_analyzer=unit32_bypass_pm_analyzer,
                unit32_main_deltaflow=unit32_main_deltaflow,
                unit32_bypass_deltaflow=unit32_bypass_deltaflow,
                unit32_nitrogen_cylinder_pressure=unit32_nitrogen_cylinder_pressure,
                unit32_so2_o2_cylinder_pressure=unit32_so2_o2_cylinder_pressure,
                unit32_co_nox_cylinder_pressure=unit32_co_nox_cylinder_pressure,
                unit32_plc_status=unit32_plc_status,
                unit32_network_switch_status=unit32_network_switch_status,
                unit32_hmi_status=unit32_hmi_status,
                unit32_air_condition_status=unit32_air_condition_status,
                unit31_power=unit31_power,
                unit32_power=unit32_power,
                remarks=remarks)
                this.create_activities(request,'cems',f'{request.user.username} updated the CEMS details of CEMS sheet {id}','info',False)
                messages.success(request,'Details successfully updated')
                return redirect(request.path)
            else: 
                messages.error(request,'This data cannot be modified. CEMS data can only be modified within 6 hours of creation')
                return redirect(request.path)
        elif action =='delete':
            if cems_item.modify ==True:
                CEMSData.objects.filter(id=id).delete()
                this.create_activities(request,'cems',f'{request.user.username} deleted the CEMS data of CEMS sheet {id}','danger',False)
                messages.warning(request,'CEMS data has been deleted successfully')
                return redirect('/cems/')
            else: 
                messages.error(request,'This data cannot be deleted. CEMS data can only be deleted within 6 hours of creation')
                return redirect(request.path)

@login_required
def gallery(request):
    context=None
    context=this.DB(request)
    if request.method=='GET':
        return render(request,'gallery/index.html',context)
    elif request.method == 'POST':
        task = request.POST['task']
        if task == 'addnew':
            title = request.POST['title']
            description = request.POST['description']
            location = request.POST['location']
            files = request.FILES.getlist('images')
            by=(request.user.firstname)+(request.user.surname)  # replace this with the actual user name retrieval logic
            n=0
            for index, f in enumerate(files):
                n+=1
                random_string = generate_random_string(4)
                file_extension = f.name.split('.')[-1]
                if len(files) > 1:
                    new_filename = f"{index + 1}_{random_string}.{file_extension}"
                else:
                    new_filename = f"{random_string}.{file_extension}"
                f.name = new_filename

                instance = Gallery.objects.create(
                    title=title+'('+str(n)+')',
                    location=location,
                    by=by,
                    description=description,
                    media=f
                )
                instance.save()
            message=f'{request.user.username} added a new media files'
            this.create_activities(request,'gallery',message,'success',False)
            this.create_notification(request.user.username,message,'info')
            messages.success(request, 'Images saved successfully')
            return redirect(request.path)

@login_required
def gallerydelete(request,id):
    if request.method=='POST':
        item=Gallery.objects.get(id=id)
        item.delete()
        this.create_activities(request,'gallery',f'{request.user.username} deleted the gallery item,{item.title}','danger',False)

        messages.success(request,'Item deleted succesfully')
        return redirect('/gallery/')
    else:
        return render(request,'400.html')

@login_required
def manual(request):
    context=None
    context=this.DB(request)
    if request.method=='GET':
        return render(request,'manual/index.html',context)
    elif request.method == 'POST':
        task = request.POST['task']
        if task == 'addnew':
            title = request.POST['title']
            description = request.POST['description']
            type = request.POST['type']
            files = request.FILES.getlist('docs')
            by = (request.user.firstname)+(request.user.surname  )
            n=0
            for index, f in enumerate(files):
                n+=1
                random_string = generate_random_string()
                file_extension = f.name.split('.')[-1]
                if len(files) > 1:
                    new_filename = f"{index + 1}_{random_string}.{file_extension}"
                else:
                    new_filename = f"{random_string}.{file_extension}"
                f.name = new_filename
                ext='pdf'
                if type =='txt':
                    ext='txt'
                elif type == 'WordDoc':
                    ext='docx'
                elif type == 'PowerPoint':
                    ext='pptx'
                elif type == 'Excel':
                    ext='xlsx'
                elif type == 'PDF':
                    ext='pdf'

                instance = Manuals.objects.create(
                    title=title+'('+str(n)+')',
                    type=type,
                    ext=ext,
                    by=by,
                    description=description,
                    media=f
                )
                instance.save()
            message=f'{request.user.username} added a new document file(s)'
            this.create_activities(request,'manual',message,'success',False)
            this.create_notification(request.user.username,message,'warning')
            messages.success(request, 'Document saved successfully')
            return redirect(request.path)


def manual_view(request, id):
    manual = get_object_or_404(Manuals, id=id)
    file_path = manual.media.path  # Get the path to the file
    
    # Open the file for reading in binary mode
    response = FileResponse(open(file_path, 'rb'), content_type='application/octet-stream')
    
    # Set the content disposition header to inline so the file opens in the browser
    response['Content-Disposition'] = f'inline; filename="{os.path.basename(file_path)}"'
    
    return response

@login_required
def manualdelete(request,id):
    if request.method=='POST':
        item=Manuals.objects.get(id=id)
        item.delete()
        this.create_activities(request,'manual',f'{request.user.username} deleted the manual item, {item.title}','danger',False)
        messages.success(request,'Item deleted succesfully')
        return redirect('/manual/')
    else:
        return render(request,'400.html')
@login_required
def interpol(request):
    context=None
    context=this.DB(request)
    return render(request,'interpol.html',context)
@login_required
def users(request):
    context=None
    context=this.DB(request)
    if request.user.admin_type !='superadmin':
        return render(request,'403.html')
    return render(request,'user/index.html',context)
@login_required
def newusers(request):
    if request.user.admin_type !='superadmin':
        return render(request,'403.html')
    if request.method=='GET':
        context=None
        context=this.DB(request)
        return render(request,'user/add.html',context)
    elif request.method=='POST':
        firstname=request.POST['firstname']
        surname=request.POST['surname']
        admin_type=request.POST['admin_type']
        phone=request.POST['phone']
        email=request.POST['email']
        username = firstname[0].lower() + surname.lower()
        password='admin_password'
        admin= Admin.objects.create(
            firstname=firstname,
            surname=surname,
            username=username,
            phone=phone,
            email=email,
            admin_type=admin_type,
        )
        admin.set_password(password)
        admin.save()
        message=f'{request.user.username} added a new user; {Admin.objects.last().id}','primary'
        this.create_activities(request,'admin',message,'success',False)
        this.create_notification(request.user.username,message,'info')
        messages.success(request,"Admin with username: "+username +" has been added successfully")
        return redirect('/users/')
    
@login_required
def userdetails(request,username):
    if request.user.admin_type !='superadmin':
        return render(request,'403.html')
    admin=Admin.objects.get(username=username)
    context=None
    context=this.DB(request)
    context['this_admin']=admin
    if request.method=='GET':
        return render(request,'user/details.html',context)
    if request.method=='POST':
        task=request.POST['task']
        if task=='edit':
            firstname=request.POST['firstname']
            surname=request.POST['surname']
            phone=request.POST['phone']
            email=request.POST['email']
            admin_type=request.POST['admin_type']
            employee_id=request.POST['employee_id']
            
            Admin.objects.filter(username=username).update(
                firstname=firstname,
                surname=surname,
                phone=phone,
                email=email,
                admin_type=admin_type,
                employee_id=employee_id,
            )
            this.create_activities(request,'admin',f'{request.user.username} updated the details of admin, {username}','warning',False)
            messages.success(request,"Admin with username: "+username +" has been updated successfully")
            return redirect(request.path)
        elif task=='accountsettings':
            nusername=request.POST['username']
            password=request.POST['password']
            confirm=request.POST['confirm']
            if nusername !='' and nusername !=admin.username:
                Admin.objects.filter(username=username).update(username=nusername)
                messages.success(request,"username has been reset successfully")
                return redirect('/users/')
            if password !='':
                if password== confirm:
                    admin.set_password(password)
                    admin.save()
                    this.create_activities(request,'admin',f'{request.user.username} reset the password of admin, {username}','danger',False)
                    messages.success(request,"Admin with username: "+username +" password has been reset successfully")
                    return redirect(request.path)
                else:
                    messages.error(request,"Passwords do not match")
                    return redirect(request.path)
            return render(request,'user/details.html',context)
        elif task =='eteled':
            confirmed=request.POST['confirmed']
            if request.user.username !=admin.username:
                Admin.objects.filter(username=username).delete()
                this.create_activities(request,'admin',f'{request.user.username} deleted the account of admin, {username}','danger',False)
                messages.success(request,f"user with username {username} has been deleted permanently")
                return redirect('/users/')
            else:
                messages.error(request,"Please you cannot delete your own account")
                return redirect(request.path)
@login_required
def userself(request):
    admin=request.user
    username=admin.username
    context=None
    context=this.DB(request)
    context['this_admin']=admin
    if request.method=='GET':
        return render(request,'user/self.html',context)
    if request.method=='POST':
        task=request.POST['task']
        if task=='edit':
            firstname=request.POST['firstname']
            surname=request.POST['surname']
            phone=request.POST['phone']
            email=request.POST['email']
            employee_id=request.POST['employee_id']
            
            Admin.objects.filter(username=username).update(
                firstname=firstname,
                surname=surname,
                phone=phone,
                email=email,
                employee_id=employee_id,
            )
            messages.success(request,"Admin with username: "+username +" has been updated successfully")
            return redirect(request.path)
        elif task == 'ppic_change':
            username = request.user.username  # Assuming the user is logged in
            # ppic change
            if 'nppic' in request.FILES:
                npic = request.FILES['nppic']
                
                # Generate a random string for the new file name
                ext = os.path.splitext(npic.name)[1].lower()  # Get the file extension
                random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
                clean_name = random_string + ext

                # Open the uploaded image with Pillow
                img = Image.open(npic)

                # Convert image to RGB if it's RGBA (JPEG doesn't support transparency)
                if img.mode == 'RGBA':
                    img = img.convert('RGB')

                # Crop the image from the bottom side to make it a square
                width, height = img.size
                if width != height:
                    min_dim = min(width, height)  # Find the smallest dimension (either width or height)
                    top = 0  # We want to keep the top part intact
                    bottom = min_dim  # Crop the bottom to the same as the width, so it becomes a square
                    img = img.crop((0, top, width, bottom))  # Crop only the bottom part

                # Save the cropped image to a BytesIO buffer
                buffer = BytesIO()
                img.save(buffer, format='JPEG')  # Adjust format if necessary (JPEG, PNG, etc.)
                cropped_image_file = ContentFile(buffer.getvalue(), clean_name)

                # Save the new profile picture with the cropped image
                admin_instance = Admin.objects.get(username=username)
                admin_instance.ppic.save(clean_name, cropped_image_file)

                messages.success(request, "Your profile picture has been updated successfully.")
                return redirect('/users/')
            else:
                messages.error(request, "Please upload a valid image file.")
                return redirect('/users/')
            # end ppic
        elif task=='accountsettings':
            nusername=request.POST['username']
            
            if nusername !='' and nusername !=admin.username:
                Admin.objects.filter(username=username).update(username=nusername)
                messages.success(request,"username has been reset successfully")
                return redirect('/users/')
            
            return render(request,'user/details.html',context)
        elif task=='accpassword':
            opassword=request.POST['opassword']
            password=request.POST['password']
            confirm=request.POST['confirm']
            if password !='':
                if password== confirm:
                    if request.user.check_password(opassword):
                        thisadmin=Admin.objects.get(username=username)
                        thisadmin.set_password(password)
                        thisadmin.save()
                        messages.success(request,"Admin with username: "+username +" password has been reset successfully")
                        return redirect('/logout')
                    else:
                        messages.error(request,"Your old password you entered is wrong!")
                        return redirect(request.path)
                    
                else:
                    messages.error(request,"Passwords do not match")
                    return redirect(request.path)
            return render(request,'user/self.html',context)
        elif task =='eteled':
            confirmed=request.POST['confirmed']
            if request.user.username !=admin.username:
                Admin.objects.filter(username=username).delete()
                messages.success(request,f"user with username {username} has been deleted permanently")
                return redirect('/users/')
            else:
                messages.error(request,"Please you cannot delete your own account")
                return redirect(request.path)
@login_required
def safety_moment(request):
    if request.method=='GET':
        context=None
        context=this.DB(request)
        return render(request,'safety/index.html',context)
@login_required
def safety_moment_add(request):
    if request.method == 'POST':
        current_date = datetime.now()
        current_year = current_date.year
        current_month = current_date.month

        # Check if a safety moment for this month already exists
        if SafetyMoment.objects.filter(month=current_month, year=current_year).exists():
            messages.error(request, "A safety moment for this month already exists.")
            return redirect('/safety_moment/')

        topics_string= request.POST['topics']
        main_topic= request.POST['main_topic']
        topic_list = re.split(r'[,.]|(?<=\d)\s*', topics_string.strip())

        # Remove any empty strings from the list
        topic_list = [topic.strip() for topic in topic_list if topic.strip()]

        # Determine the number of days in the current month
        if current_month in [1, 3, 5, 7, 8, 10, 12]:  # 31 days
            num_days = 31
        elif current_month in [4, 6, 9, 11]:  # 30 days
            num_days = 30
        else:  # February (check for leap year)
            num_days = 29 if (current_year % 4 == 0 and (current_year % 100 != 0 or current_year % 400 == 0)) else 28

        # Create SafetyMoment instance
        sm = SafetyMoment.objects.create(
            main_topic=main_topic,
            month=current_month,
            year=current_year
        )

        # User distributions
        users = list(Admin.objects.all())
        num_users = len(users)

        if num_users == 0:
            return HttpResponse("No users available for assignment.")

        # Randomly select a starting user from the list
        starting_user = random.choice(users)
        user_index = users.index(starting_user)  # Get the index of the selected user

        # Track user assignments and used topics
        user_assignments = {user: 0 for user in users}
        max_assignments = 3
        min_assignments = 2
        topic_index = 0

        # Assign topics and users to available days (excluding weekends)
        for day in range(1, num_days + 1):
            day_date = datetime(current_year, current_month, day)
            if day_date.weekday() < 5:  # 0-4 are Monday to Friday
                if topic_index < len(topic_list):  # Check if there are available topics
                    setattr(sm, f'day_{day}_topic', topic_list[topic_index])
                    assigned = False
                    attempts = 0  # Track attempts to avoid infinite loop

                    while not assigned and attempts < 10:  # Limit attempts to prevent infinite loops
                        user = users[user_index]

                        # Assign the user if they haven't hit the max assignments yet
                        if user_assignments[user] < max_assignments:
                            setattr(sm, f'day_{day}_user', f'{user.firstname.capitalize()} {user.surname.capitalize()}')
                            user_assignments[user] += 1
                            assigned = True
                        # Move to the next user, wrapping around if necessary
                        user_index = (user_index + 1) % num_users
                        attempts += 1

                    topic_index += 1  # Move to the next topic

        # Ensure each user has at least min_assignments
        for user in users:
            while user_assignments[user] < min_assignments:
                for day in range(1, num_days + 1):
                    day_field = f'day_{day}_user'
                    if getattr(sm, day_field) is None:
                        setattr(sm, day_field, f'{user.firstname.capitalize()} {user.surname.capitalize()}')
                        user_assignments[user] += 1
                        break

        # Save the SafetyMoment instance with assigned users
        sm.save()

        # Redirect or return a success message
        messages.success(request, "Safety Moment successfully created with user assignments.")
        return redirect('/safety_moment/')

    else:
        return render(request,'400.html')

def todo(request):
    if request.method=='GET':
        context=None
        context=this.DB(request)
        return render(request,'todo/index.html',context)
def todo_add(request):
    if request.method == 'GET':
        context = this.DB(request)
        return render(request, 'todo/add.html', context)

    if request.method == 'POST':
        
        task = request.POST['task']
        if task =='add':
            title = request.POST['title']
            priority = request.POST['priority']
            description = request.POST['description']
            if not title:
                messages.error(request, "Title is required.")
                return redirect('/todo/')

            try:
                task = Todo.objects.create(
                    title=(title),
                    description=(description),
                    priority=(priority),
                    completed=False,
                    by=request.user.username
                )
                task.save()
                messages.success(request, "Task added successfully!")
                return redirect('/todo')
            except Exception as e:
                messages.error(request, f"An error occurred: {str(e)}")
                return redirect('/todo/')
        elif task =='edit':
            title = request.POST['title']
            priority = request.POST['priority']
            todo_id = int(request.POST['todo_id'])
            status = request.POST['status']
            if status=='completed':
                completed=True
            elif status=='pending':
                completed=False
            description = request.POST['description']
            if not title:
                messages.error(request, "Title is required.")
                return redirect('/todo/')

            try:
                task = Todo.objects.filter(id=todo_id).update(
                    title=(title),
                    description=(description),
                    completed=completed,
                    priority=priority,
                )
                messages.success(request, "Task updated successfully!")
                return redirect('/todo')
            except Exception as e:
                messages.error(request, f"An error occurred: {str(e)}")
                return redirect('/todo/')
        elif task =='delete':
            todo_id = int(request.POST['todo_id'])
            Todo.objects.filter(id=todo_id).delete()
            messages.success(request, f"Todo item {todo_id} has been deleted successfully")
            return redirect('/todo/')
def reports(request):
    if request.method=='GET':
        context=None
        context=this.DB(request)
        return render(request,'reports/index.html',context)
def report_add(request):
    if request.method=='GET':
        context=None
        context=this.DB(request)
        return render(request,'reports/add.html',context)
    elif request.method == 'POST':
        title = request.POST.get('title')
        contents = request.POST.get('contents')
        asset = request.POST.get('asset')
        work_order_number = request.POST.get('work_order_number')
        permit_number = request.POST.get('permit_number')

        # Convert the date strings to Django DateField format
        try:
            date_started = datetime.strptime(request.POST.get('date_started'), '%Y-%m-%d').date()
            date_ended = datetime.strptime(request.POST.get('date_ended'), '%Y-%m-%d').date()
        except ValueError:
            messages.error(request, 'Invalid date format. Please use YYYY-MM-DD.')
            return redirect(request.path)  # Redirect back to the form

        location = request.POST.get('location')
        observations = request.POST.get('observations')
        conclusion = request.POST.get('conclusion')
        actions_implemented = request.POST.get('actions_implemented')
        item_replaced = request.POST.get('item_replaced') == 'Yes'
        item_replaced_code = request.POST.get('item_replaced_code', '')

        # Handle file uploads
        featured_pictures = []
        for i in range(1, 7):  # Accepting 6 images
            picture = request.FILES.get(f'featured_pictures')
            if picture:
                fs = FileSystemStorage()
                filename = fs.save(picture.name, picture)
                featured_pictures.append(filename)

        # Create a new report instance
        report = Report.objects.create(
            title=title,
            contents=contents,
            conclusion=conclusion,
            asset=asset,
            work_order_number=work_order_number,
            permit_number=permit_number,
            date_started=date_started,
            date_ended=date_ended,
            location=location,
            observations=observations,
            actions_implemented=actions_implemented,
            item_replaced=item_replaced,
            item_replaced_code=item_replaced_code,
        )

        featured_pictures = request.FILES.getlist('featured_pictures')  
        for i, picture in enumerate(featured_pictures[:6]):  # Limit to 6 images
            if picture:
                fs = FileSystemStorage()
                random_string = generate_random_string(3)
                filename = fs.save(picture.name, picture)
                setattr(report, f'featured_picture_{i + 1}', filename) 
        # Save the report instance
        report.save()

        # Show success message
        # When creating the report
        this.create_activities(request, 'report', 'You have created a new report.', 'primary', False)
        messages.success(request, 'Report created successfully!')
        return redirect('/reports/')  # Change to your success URL

    else:
        return render(request,'400.html')
def report_view(request,id):
    if request.method=='GET':
        context=None
        context=this.DB(request)
        context['report']=Report.objects.get(id=id)
        return render(request,'reports/view.html',context)
def report_edit(request,id):
    if request.method=='GET':
        context=None
        context=this.DB(request)
        context['report']=Report.objects.get(id=id)
        return render(request,'reports/edit.html',context)
    elif request.method == 'POST':
        title = request.POST.get('title')
        contents = request.POST.get('contents')
        asset = request.POST.get('asset')
        work_order_number = request.POST.get('work_order_number')
        permit_number = request.POST.get('permit_number')

        try:
            date_started = datetime.strptime(request.POST.get('date_started'), '%Y-%m-%d').date()
            date_ended = datetime.strptime(request.POST.get('date_ended'), '%Y-%m-%d').date()

            # Check if start date comes before end date
            if date_started > date_ended:
                messages.error(request, 'Start date cannot be later than the end date.')
                return redirect(request.path)

        except ValueError:
            messages.error(request, 'Invalid date format. Please use YYYY-MM-DD.')
            return redirect(request.path)

        location = request.POST.get('location')
        observations = request.POST.get('observations')
        conclusion = request.POST.get('conclusion')
        actions_implemented = request.POST.get('actions_implemented')
        item_replaced = request.POST.get('item_replaced') == 'Yes'
        item_replaced_code = request.POST.get('item_replaced_code', '')

        # Update the report instance
        report = Report.objects.filter(id=id).first()
        if report:
            report.title = title
            report.contents = contents
            report.asset = asset
            report.work_order_number = work_order_number
            report.permit_number = permit_number
            report.date_started = date_started
            report.date_ended = date_ended
            report.location = location
            report.conclusion = conclusion
            report.observations = observations
            report.actions_implemented = actions_implemented
            report.item_replaced = item_replaced
            report.item_replaced_code = item_replaced_code

            # Handle file uploads, only replace images if new ones are uploaded
            featured_pictures = request.FILES.getlist('featured_pictures')
            if featured_pictures:  # Check if any new images are uploaded
                for i, picture in enumerate(featured_pictures[:6]):  # Limit to 6 images
                    if picture:
                        fs = FileSystemStorage()
                        filename = fs.save(picture.name, picture)
                        setattr(report, f'featured_picture_{i + 1}', filename)  # Dynamically set the field

            # Save the updated report
            report.save()

            # Log the activity
            this.create_activities(request, 'report', 'You have edited an existing report.', 'primary', False)

            # Show success message and redirect
            messages.success(request, 'This report has been edited successfully!')
            return redirect('/reports/')  # Change to your success URL
        else:
            messages.error(request, 'Report not found.')
            return redirect('/reports/')  # Change to your error URL
