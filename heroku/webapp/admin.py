from webapp import models
from django.contrib import admin

registered = [
    models.Tag, 
    models.Bid, 
    models.Transaction, 
    models.BidInteraction
]

for model in registered:
    admin.site.register(model)
