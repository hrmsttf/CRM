import threading
from .models import *

from faker import Faker
import random

# Faker in library to create dummy records.
fake = Faker()


class CreateProductThread(threading.Thread):
    
    def __init__(self, total):
        self.total = total
        threading.Thread.__init__(self)

    def run(self):
        try:
            print('Thread executed..')
            for i in range(self.total):
                print(i)
                Product.objects.create(
                    name = fake.name(),
                    price = random.randint(100, 1000),
                    category = fake.name(),
                    description = fake.name(),
                    
                )

        except Exception as e:
            print(e)


