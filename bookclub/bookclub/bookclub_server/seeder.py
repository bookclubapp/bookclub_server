from faker import Faker
from faker import Factory
import factory
import factory.django
import random
from .models import User

faker = Factory.create('tr_TR')
name = faker.name()
country = 'Turkey'
mail = faker.email()
phoneNumber = faker.phone_number()
dateOfBirth = faker.date_of_birth(minimum_age=18, maximum_age=100)
username = faker.user_name()
password = faker.password(length=6, special_chars=False, digits=False, upper_case=False, lower_case=True)
longitude = random.uniform(36, 42) 
latitude = random.uniform(26,45)

user = User(name=name, country=country, mail=mail, phoneNumber=phoneNumber, dateOfBirth=dateOfBirth, username=username, password=password,
            long=longitude, lat=latitude, onlineState=1, profilePicture='noimage.jpg')

user.save()

    # name = models.CharField(max_length=100)
    # surname = models.CharField(max_length=100)
    # country = models.CharField(max_length=100)
    # mail = models.CharField(max_length=250)
    # phoneNumber = models.CharField(max_length=100, blank=True, null=True)
    # dateOfBirth = models.DateField(blank=True, null=True)
    # username = models.CharField(max_length=50)
    # password = models.CharField(max_length=50)
    # long = models.DecimalField(max_digits=8, decimal_places=3)  # location longitude
    # lat = models.DecimalField(max_digits=8, decimal_places=3)  # location latitude
    # onlineState = models.BooleanField(default=True)
    # profilePicture = models.CharField(default="default.jpg", max_length=250)