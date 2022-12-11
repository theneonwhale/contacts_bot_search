from collections import UserDict
from datetime import datetime
import pickle


class AddressBook(UserDict):
    def __init__(self):
        super().__init__()
        self.load_from_file()

    def add_record(self, record):
        self.data[record.name.value] = record

    def iterator(self, per_page=5):
        contacts_list = []
        for contact in self.data.values():
            contacts_list.append(contact)
            if len(contacts_list) == per_page:
                yield contacts_list
                contacts_list = []
        if contacts_list:
            yield contacts_list

    def search_contacts(self, query):
        contacts_list = []
        for key, value in self.data.items():
            contact_data = key + '\n' + '\n'.join([phone.value for phone in value.phones])
            if query in contact_data:
                phones = ', '.join([phone.value for phone in self.data[key].phones])
                birthday = self.data[key].birthday.value if self.data[key].birthday else 'no data'
                message = f'{key.title()}:\n phones: {phones}\n birthday: {birthday}'
                contacts_list.append(message)

        if len(contacts_list):
            message = ('\n').join(contacts_list)
            return message
        else:
            return f'Nothing found'

    def save_to_file(self):
        with open('contacts.bin', 'wb') as data:
            pickle.dump(self.data, data)

    def load_from_file(self):
        try:
            with open('contacts.bin', 'rb') as data:
                self.data = pickle.load(data)
        except FileNotFoundError:
            pass

class Field:
    def __init__(self, value):
        self._value = None
        self.value = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value

class Name(Field):
    pass

class Phone(Field):
    @Field.value.setter
    def value(self, phone):
        if not phone.isnumeric():
            raise ValueError('Phone should be a number.')
        if len(phone) != 10:
            raise ValueError('Phone must contains 10 symbols.')
        self._value = phone

class Birthday(Field):
    @Field.value.setter
    def value(self, birthday):
        current_date = datetime.now().date()
        birthday_date = datetime.strptime(birthday, '%Y/%m/%d').date()
        if birthday_date > current_date:
            raise ValueError('Date should not be earlier than current date.')
        self._value = birthday

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def info(self):
        phones = []
        for phone in self.phones:
            phones.append(phone.value)
        phones = ', '.join(phones)
        birthday = ''
        if self.birthday:
            birthday = f'{self.birthday.value}'
        message = f'{self.name.value.title()}:\n phones: {phones}\n birthday: {birthday}'
        return message

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def delete_phone(self, phone):
        for item in self.phones:
            if item.value == phone:
                self.phones.remove(item)

    def change_phone(self, old_phone, new_phone):
        self.delete_phone(old_phone)
        self.add_phone(new_phone)

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def days_to_birthday(self):
        if not self.birthday:
            raise ValueError('There is no birthday date in this contact.')
        current_date = datetime.now().date()
        birthday_date = datetime.strptime(self.birthday.value, '%Y/%m/%d').date()
        next_birthday = birthday_date.replace(year=current_date.year)
        if next_birthday < current_date:
            next_birthday = next_birthday.replace(year=current_date.year + 1)
        return (next_birthday - current_date).days


contacts = AddressBook()


def parser(command_input):
    parsed_input = command_input.lower().strip().split()
    return parsed_input


def input_error(func):
    def inner(data):
        try:
            return func(data)
        except ValueError as exception:
            return exception.args[0]
        except KeyError as exception:
            return exception.args[0]
        except IndexError:
            return 'With this command you should enter some data.'
    return inner


def hello():
    return 'How can I help you?'

@input_error
def add(data):
    if data[0].isnumeric():
        raise ValueError('Name should be a string.')
    if data[0] in contacts:
        record = contacts.data[data[0]]
        record.add_phone(data[1])
        message = f'Phone {data[1]} was successfully added to contact {data[0].title()}.'
        return message
    else:
        record = Record(data[0])
        if len(data) > 1:
            record.add_phone(data[1])
        contacts.add_record(record)
        message = f'Contact {data[0].title()} was successfully added.'
        return message

@input_error
def delete(data):
    if data[0].isnumeric():
        raise ValueError('Name should be a string.')
    if not data[1].isnumeric():
        raise ValueError('Phone should be a number.')
    if data[0] in contacts:
        record = contacts.data[data[0]]
        record.delete_phone(data[1])
        message = f'Phone {data[1]} was successfully deleted from contact {data[0].title()}.'
        return message
    else:
        raise KeyError('There is no such contact.')

@input_error
def change(data):
    if data[0].isnumeric():
        raise ValueError('Name should be a string.')
    if data[0] not in contacts:
        raise KeyError('There is no such contact.')
    if not data[1].isnumeric() or not data[2].isnumeric():
        raise ValueError('Phone should be a number.')
    record = contacts.data[data[0]]
    record.change_phone(data[1], data[2])
    message = f'Contact {data[0].title()} phone {data[1]} was successfully updated with phone {data[2]}.'
    return message

@input_error
def phone(data):
    if data[0].isnumeric():
        raise ValueError('Name should be a string.')
    if data[0] not in contacts:
        raise KeyError('There is no such contact.')
    for name, record in contacts.items():
        if name == data[0]:
            return record.info()

@input_error
def search(data):
    search_query = data[0].split()[0]
    return contacts.search_contacts(search_query)

def show():
    if len(contacts):
        contacts_list = ''
        page_number = 1
        for page in contacts.iterator(3):
            contacts_list += f'Page {page_number}:\n'
            for record in page:
                contacts_list += f'{record.info()}\n'
            page_number += 1
        return contacts_list
    else:
        return 'There are no any contacts.'

@input_error
def add_birthday(data):
    if data[0] not in contacts:
        raise KeyError('There is no such contact.')
    record = contacts.data[data[0]]
    record.add_birthday(data[1])
    return f'Birthday date {data[1]} for contact {data[0]} was successfully added.'

@input_error
def days_to_birthday(data):
    record = contacts.data[data[0]]
    message = f'{record.days_to_birthday()} days left until {data[0].title()}\'s birthday'
    return message

def close():
    return 'Good bye!'


commands = {
    'hello': hello,
    'add': add,
    'delete': delete,
    'change': change,
    'phone': phone,
    'search': search,
    'show all': show,
    'add_birthday': add_birthday,
    'days_to_birthday': days_to_birthday,
    'close': close
}


def main():
    try:
        while True:
            command_input = input('Enter command and data: ')
            if command_input in ('hello', 'show all'):
                print(commands.get(command_input)())
                continue
            if command_input in ('good bye', 'close', 'exit'):
                print(commands.get('close')())
                break
            parsed_input = parser(command_input)
            command = parsed_input[0]
            if command not in commands.keys():
                print('There is no such command.')
                continue
            data = parsed_input[1:]
            method = commands.get(command)
            print(method(data))
    finally:
        contacts.save_to_file()


if __name__ == '__main__':
    main()
