from multiprocessing import Event
from django.contrib import admin
from .models import Admin, Calsheet,CEMSData, Gallery, Manuals,ResetTokens,Activities,Notifications,Message,StandardInstruments,SafetyMoment,Todo,Report
admin.site.register(Admin)
admin.site.register(CEMSData)
admin.site.register(Gallery)
admin.site.register(Manuals)
admin.site.register(Calsheet)
admin.site.register(ResetTokens)
admin.site.register(Activities)
admin.site.register(Notifications)
admin.site.register(Message)
admin.site.register(StandardInstruments)
admin.site.register(SafetyMoment)
admin.site.register(Todo)
admin.site.register(Report)


