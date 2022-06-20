class Person:
    def __init__(self, name='', phone='', address=''):
        self.address = address
        self.phone = phone
        self.name = name


person = Person('hamed', '333', 'Wilson Ave')
print(person)