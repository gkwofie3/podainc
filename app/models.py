from pyexpat import model
from datetime import datetime,timedelta,date
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, Group, Permission

import os
from uuid import uuid4


# Create your models here.
class AdminManager(BaseUserManager):
    def create_user(self, email, surname, firstname, phone, password, username, ppic):
        if not username:
            raise ValueError("Username is required")
        if not phone:
            raise ValueError("Phone is required")
        if not surname:
            raise ValueError("Surname is required")
        if not firstname:
            raise ValueError("First name is required")
        if not password:
            raise ValueError("Password is required")
        user = self.model(
            email=self.normalize_email(email),
            phone=phone,
            surname=surname,
            firstname=firstname,
            username=username,
            ppic=ppic,
        )
        user.set_password(password)
        user.is_verified = True
        user.save(using=self._db)
        return user

    def create_superuser(self, username, phone, surname, firstname, password=None):
        user = self.create_user(
            email=" ",
            phone=phone,
            surname=surname,
            firstname=firstname,
            password=password,
            username=username,
            ppic="admins/user.jpg",
        )
        user.set_password(password)
        user.is_admin = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

class Admin(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(verbose_name="Email address", max_length=225)
    phone = models.CharField(verbose_name="Phone number", max_length=225)
    surname = models.CharField(verbose_name="Surname", max_length=225, default="Gideon")
    firstname = models.CharField(verbose_name="First name", max_length=225, default="Kwofie")
    username = models.CharField(verbose_name="Username", max_length=225, unique=True)
    theme = models.CharField(verbose_name="Theme", max_length=225, default="light")
    ppic = models.FileField(upload_to='admins', verbose_name="Profile picture", default='admins/user.jpg')
    admin_type = models.CharField(max_length=255,default='admin')
    admin_notifications = models.IntegerField(verbose_name="Admin notifications", default=0)
    admin_messages = models.IntegerField(verbose_name="Admin messages", default=0)
    date_joined = models.DateField(auto_now_add=True)
    last_login = models.DateField(auto_now=True)
    is_admin = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    employee_id = models.IntegerField(verbose_name="Admin employee id", default=1000)

    groups = models.ManyToManyField(Group, related_name='admin_user_set', blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name='admin_user_set', blank=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['phone', 'firstname', 'surname']

    objects = AdminManager()

    def __str__(self):
        return self.username

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

class Calsheet(models.Model):
    tag = models.CharField(max_length=225, verbose_name='Tag number')
    description = models.CharField(max_length=225, verbose_name='Instrument description')
    process_type = models.CharField(max_length=225, verbose_name='Measuring variable')
    inst_type=models.CharField(max_length=225,verbose_name='Instrument type')
    design_type= models.CharField(max_length=225, verbose_name='Device type')
    serial_number= models.CharField(max_length=225, verbose_name='serial Number',default='')
    model_number= models.CharField(max_length=225, verbose_name='Model Number',default='')
    unit= models.CharField(max_length=225, verbose_name='Unit')
    manufacturer= models.CharField(max_length=225, verbose_name='Manufacturer')
    location= models.CharField(max_length=225, verbose_name='Location',default='')
    lower_limit = models.DecimalField(default=0, max_digits=10, decimal_places=2)
    upper_limit = models.DecimalField(default=0, max_digits=10, decimal_places=2)
    lower_range = models.DecimalField(default=0, max_digits=10, decimal_places=2)
    upper_range = models.DecimalField(default=0, max_digits=10, decimal_places=2)
    deviation_type=models.CharField(default=0, max_length=225,verbose_name='Deviation type')
    af_desire0=models.FloatField(default=0, )
    af_desire25=models.FloatField(default=0, )
    af_desire50=models.FloatField(default=0, )
    af_desire75=models.FloatField(default=0, )
    af_desire100=models.FloatField(default=0, )
    af_actual0=models.FloatField(default=0, )
    af_actual25=models.FloatField(default=0, )
    af_actual50=models.FloatField(default=0, )
    af_actual75=models.FloatField(default=0, )
    af_actual100=models.FloatField(default=0, )
    af_error0=models.FloatField(default=0, )
    af_error25=models.FloatField(default=0, )
    af_error50=models.FloatField(default=0, )
    af_error75=models.FloatField(default=0, )
    af_error100=models.FloatField(default=0, )
    al_actual0=models.FloatField(default=0, )
    al_actual25=models.FloatField(default=0, )
    al_actual50=models.FloatField(default=0, )
    al_actual75=models.FloatField(default=0, )
    al_actual100=models.FloatField(default=0, )
    al_error0=models.FloatField(default=0, )
    al_error25=models.FloatField(default=0, )
    al_error50=models.FloatField(default=0, )
    al_error75=models.FloatField(default=0, )
    al_error100=models.FloatField(default=0, )
    af_deviation=models.FloatField(default=0, verbose_name='As found error')
    al_deviation=models.FloatField(default=0, verbose_name='As left error')    
    date=models.DateField(auto_now_add=True)
    next_cal_due_date=models.DateField()
    remarks=models.TextField(default ='')
    standard_instrument=models.CharField(max_length=225)
    by=models.CharField(max_length=225, verbose_name='By')
    cal_number=models.IntegerField(default=1)
    remarks=models.TextField()

class StandardInstruments(models.Model):
    name=models.CharField(max_length=255)
    manufacturer=models.CharField(max_length=255)
    process_type=models.CharField(max_length=255)
    unit=models.CharField(max_length=255)
    upper_limit=models.FloatField()
    lower_limit=models.FloatField()
    serial_number=models.CharField(max_length=255)
    model_number=models.CharField(max_length=255)
    last_cal_date=models.DateField()
    due_cal_date=models.DateField()
    calibrated_by=models.CharField(max_length=255)
    picture=models.FileField(upload_to='standar_instruments', null=True, blank=True)
class CEMSData(models.Model):
    # Unit 31 fields
    unit31_room_temperature = models.FloatField()
    unit31_instrument_air_pressure = models.FloatField()
    unit31_sample_flow = models.FloatField()
    unit31_vacuum_pressure = models.FloatField()
    unit31_chiller_temperature = models.FloatField()
    unit31_heated_sample_temperature = models.FloatField()
    unit31_nox_analyzer = models.FloatField()
    unit31_o2_analyzer = models.FloatField()
    unit31_co_analyzer = models.FloatField()
    unit31_so2_analyzer = models.FloatField()
    unit31_main_pm_analyzer = models.FloatField()
    unit31_bypass_pm_analyzer = models.FloatField()
    unit31_main_deltaflow = models.FloatField()
    unit31_bypass_deltaflow = models.FloatField()
    unit31_power = models.FloatField()
    unit31_nitrogen_cylinder_pressure = models.FloatField()
    unit31_so2_o2_cylinder_pressure = models.FloatField()
    unit31_co_nox_cylinder_pressure = models.FloatField()
    unit31_plc_status = models.BooleanField()
    unit31_network_switch_status = models.BooleanField()
    unit31_hmi_status = models.BooleanField()
    unit31_air_condition_status = models.BooleanField()
    # Unit 32 fields
    unit32_room_temperature = models.FloatField()
    unit32_instrument_air_pressure = models.FloatField()
    unit32_sample_flow = models.FloatField()
    unit32_vacuum_pressure = models.FloatField()
    unit32_chiller_temperature = models.FloatField()
    unit32_heated_sample_temperature = models.FloatField()
    unit32_nox_analyzer = models.FloatField()
    unit32_o2_analyzer = models.FloatField()
    unit32_co_analyzer = models.FloatField()
    unit32_so2_analyzer = models.FloatField()
    unit32_main_pm_analyzer = models.FloatField()
    unit32_bypass_pm_analyzer = models.FloatField()
    unit32_main_deltaflow = models.FloatField()
    unit32_bypass_deltaflow = models.FloatField()
    unit32_nitrogen_cylinder_pressure = models.FloatField()
    unit32_so2_o2_cylinder_pressure = models.FloatField()
    unit32_co_nox_cylinder_pressure = models.FloatField()
    unit32_power = models.FloatField()
    unit32_plc_status = models.BooleanField()
    unit32_network_switch_status = models.BooleanField()
    unit32_hmi_status = models.BooleanField()
    unit32_air_condition_status = models.BooleanField()
    remarks=models.TextField()
    date=models.DateField(auto_now_add=True)
    time=models.TimeField(auto_now_add=True)
    dt=models.DateTimeField(auto_now_add=True)
    by=models.CharField(max_length=255)
    modify=models.BooleanField(default=True)
    

class Gallery(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    location = models.CharField(max_length=255)
    date = models.DateTimeField(auto_now_add=True)
    by = models.CharField(max_length=255)
    media = models.FileField(upload_to='gallery', null=False, blank=False)
class Manuals(models.Model):
    title = models.CharField(max_length=255)
    ext = models.CharField(max_length=255,default='pdf')
    description = models.TextField()
    date=models.DateTimeField(auto_now=True)
    type = models.CharField(max_length=255)
    by = models.CharField(max_length=255)
    media = models.FileField(upload_to='manuals', null=False, blank=True)

class ResetTokens(models.Model):
    key =models.CharField(max_length=225,verbose_name="Token key")
    is_used=models.BooleanField(default=False,verbose_name="Is used")
    token_for=models.CharField(max_length=224,verbose_name="Created for ")
    time=models.DateTimeField(auto_now=True)
class Activities(models.Model):
    by =models.CharField(max_length=225,verbose_name="By")
    action =models.CharField(max_length=225,verbose_name="From")
    type =models.CharField(max_length=225,verbose_name="Type",default='')
    date=models.DateTimeField(auto_now_add=True,verbose_name="Date")
    read=models.BooleanField(default=False,verbose_name="Is read")
    personal=models.BooleanField(default=False,verbose_name="Is personal")
    color=models.CharField(max_length=225,verbose_name="From",default='primary')
    tag=models.CharField(max_length=225,verbose_name="From",default='primary')
class Notifications(models.Model):
    by =models.CharField(max_length=225,verbose_name="From")
    fr =models.CharField(max_length=225,verbose_name="for")
    date=models.DateTimeField(auto_now_add=True,verbose_name="Date")
    read=models.BooleanField(default=False,verbose_name="Is read")
    message =models.CharField(max_length=225,verbose_name="Message",default="")
    tag=models.CharField(max_length=225,verbose_name="From",default='primary')
class Message(models.Model):
    frm =models.CharField(max_length=225,verbose_name="From")
    to =models.CharField(max_length=225,verbose_name="To")
    date=models.DateField(auto_now_add=True,verbose_name="Date")
    time=models.TimeField(auto_now_add=True,verbose_name="Date")
    read=models.BooleanField(default=False,verbose_name="Is read")
    message =models.CharField(max_length=225,verbose_name="Message",default="")
    tag=models.CharField(max_length=225,verbose_name="From",default='primary')
class SafetyMoment(models.Model):
    month = models.CharField(max_length=20)
    year = models.IntegerField()
    main_topic = models.TextField()
    # Fields for each day (1 to 31)
    day_1_topic = models.TextField(blank=True, null=True)
    day_1_user = models.CharField(max_length=100, blank=True, null=True)

    day_2_topic = models.TextField(blank=True, null=True)
    day_2_user = models.CharField(max_length=100, blank=True, null=True)

    day_3_topic = models.TextField(blank=True, null=True)
    day_3_user = models.CharField(max_length=100, blank=True, null=True)

    day_4_topic = models.TextField(blank=True, null=True)
    day_4_user = models.CharField(max_length=100, blank=True, null=True)

    day_5_topic = models.TextField(blank=True, null=True)
    day_5_user = models.CharField(max_length=100, blank=True, null=True)

    day_6_topic = models.TextField(blank=True, null=True)
    day_6_user = models.CharField(max_length=100, blank=True, null=True)

    day_7_topic = models.TextField(blank=True, null=True)
    day_7_user = models.CharField(max_length=100, blank=True, null=True)

    day_8_topic = models.TextField(blank=True, null=True)
    day_8_user = models.CharField(max_length=100, blank=True, null=True)

    day_9_topic = models.TextField(blank=True, null=True)
    day_9_user = models.CharField(max_length=100, blank=True, null=True)

    day_10_topic = models.TextField(blank=True, null=True)
    day_10_user = models.CharField(max_length=100, blank=True, null=True)

    day_11_topic = models.TextField(blank=True, null=True)
    day_11_user = models.CharField(max_length=100, blank=True, null=True)

    day_12_topic = models.TextField(blank=True, null=True)
    day_12_user = models.CharField(max_length=100, blank=True, null=True)

    day_13_topic = models.TextField(blank=True, null=True)
    day_13_user = models.CharField(max_length=100, blank=True, null=True)

    day_14_topic = models.TextField(blank=True, null=True)
    day_14_user = models.CharField(max_length=100, blank=True, null=True)

    day_15_topic = models.TextField(blank=True, null=True)
    day_15_user = models.CharField(max_length=100, blank=True, null=True)

    day_16_topic = models.TextField(blank=True, null=True)
    day_16_user = models.CharField(max_length=100, blank=True, null=True)

    day_17_topic = models.TextField(blank=True, null=True)
    day_17_user = models.CharField(max_length=100, blank=True, null=True)

    day_18_topic = models.TextField(blank=True, null=True)
    day_18_user = models.CharField(max_length=100, blank=True, null=True)

    day_19_topic = models.TextField(blank=True, null=True)
    day_19_user = models.CharField(max_length=100, blank=True, null=True)

    day_20_topic = models.TextField(blank=True, null=True)
    day_20_user = models.CharField(max_length=100, blank=True, null=True)

    day_21_topic = models.TextField(blank=True, null=True)
    day_21_user = models.CharField(max_length=100, blank=True, null=True)

    day_22_topic = models.TextField(blank=True, null=True)
    day_22_user = models.CharField(max_length=100, blank=True, null=True)

    day_23_topic = models.TextField(blank=True, null=True)
    day_23_user = models.CharField(max_length=100, blank=True, null=True)

    day_24_topic = models.TextField(blank=True, null=True)
    day_24_user = models.CharField(max_length=100, blank=True, null=True)

    day_25_topic = models.TextField(blank=True, null=True)
    day_25_user = models.CharField(max_length=100, blank=True, null=True)

    day_26_topic = models.TextField(blank=True, null=True)
    day_26_user = models.CharField(max_length=100, blank=True, null=True)

    day_27_topic = models.TextField(blank=True, null=True)
    day_27_user = models.CharField(max_length=100, blank=True, null=True)

    day_28_topic = models.TextField(blank=True, null=True)
    day_28_user = models.CharField(max_length=100, blank=True, null=True)

    day_29_topic = models.TextField(blank=True, null=True)
    day_29_user = models.CharField(max_length=100, blank=True, null=True)

    day_30_topic = models.TextField(blank=True, null=True)
    day_30_user = models.CharField(max_length=100, blank=True, null=True)

    day_31_topic = models.TextField(blank=True, null=True)
    day_31_user = models.CharField(max_length=100, blank=True, null=True)
    
    
class Todo(models.Model):
    title = models.CharField(max_length=200)  
    description = models.TextField(blank=True, null=True)  
    completed = models.BooleanField(default=False) 
    created_at = models.DateTimeField(auto_now_add=True) 
    updated_at = models.DateTimeField(auto_now=True) 
    by = models.CharField(max_length=225) 
    priority = models.CharField(max_length=225,default='Low') 
class Report(models.Model):
    title = models.CharField(max_length=200)
    contents = models.TextField()
    conclusion = models.TextField(default='Device is now working perfectly')
    featured_picture_1 = models.ImageField(upload_to='reports/', null=True, blank=True)
    featured_picture_2 = models.ImageField(upload_to='reports/', null=True, blank=True)
    featured_picture_3 = models.ImageField(upload_to='reports/', null=True, blank=True)
    featured_picture_4 = models.ImageField(upload_to='reports/', null=True, blank=True)
    featured_picture_5 = models.ImageField(upload_to='reports/', null=True, blank=True)
    featured_picture_6 = models.ImageField(upload_to='reports/', null=True, blank=True)
    asset = models.CharField(max_length=100)
    work_order_number = models.CharField(max_length=100)
    permit_number = models.CharField(max_length=100)
    date_created = models.DateField(auto_now=True)
    date_started = models.DateField()
    date_ended = models.DateField()
    location = models.CharField(max_length=255)  # New location field
    observations = models.TextField()
    actions_implemented = models.TextField()
    item_replaced = models.BooleanField(default=False)
    item_replaced_code = models.TextField()
   