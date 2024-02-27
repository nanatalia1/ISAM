import math
import struct
from record import Record
class OverflowFile():
    def __init__(self, path, init_pages):
        self.path=path
        self.ENTRY_SIZE_IN_BYTES = 32
        self.PAGE_SIZE_IN_BYTES = 10*32
        self.max_entries_on_page = 10
        self.record_format = 'i' + 'IIIII' + 'i' + 'I'
        self.initialize_overflowFile(init_pages)
        self.next_pointer=0
        self.overflow_pages=init_pages #ile mamy stron
        self.current_active_page=0 #na ta strone bedziemy dodawac
        self.stored_records=0
        self.num_of_disc_operations=0

    def initialize_overflowFile(self, num_pages):
        for i in range(num_pages):
            self.initialize_overflowFile_page(i)

    def initialize_overflowFile_page(self, num_page):
        page=[]
        for i in range(self.max_entries_on_page):
            record=Record(-1, [0,0,0,0,0])
            page.append(record)
        if num_page==0:
            self.write_empty_page_to_file(page)
        else:
            self.write_empty_page_to_file2(page)

    def write_empty_page_to_file(self, page):
        with open(self.path, 'wb') as file:
            for record in page:

                numbers=record.numbers
                record_data = struct.pack(self.record_format, record.id, *numbers, -1, 1)
                file.write(record_data)

    def write_empty_page_to_file2(self, page):
        with open(self.path, 'ab') as file:
            for record in page:

                numbers=record.numbers
                record_data = struct.pack(self.record_format, record.id, *numbers, -1, 1)
                file.write(record_data)

    def write_page(self, page_id, records_on_page):
        record_size = struct.calcsize(self.record_format)
        page_offset = self.PAGE_SIZE_IN_BYTES * page_id
        with open(self.path, 'w+b') as file:
            file.seek(page_offset)

            for record in records_on_page:
                if record.id==0:
                    ...
                numbers = record.numbers
                record_data = struct.pack(self.record_format, record.id, *numbers, -1, 1)
                file.write(record_data)
    def update_next_pointer(self):
        self.next_pointer+=self.ENTRY_SIZE_IN_BYTES

    def insert(self, record):
        records_on_page=self.get_page(self.current_active_page)
        for r in records_on_page:
            if r.isEmpty == 1:
                r.id = record.id
                r.numbers = record.numbers
                r.isEmpty = 0
                r.pointer = -1
                break
        self.update_page(self.current_active_page, records_on_page)

    def insert_to_overflow(self, previous, record, previous_pointer):
        record_from_pointer=self.get_record(previous.pointer)
        if record_from_pointer.pointer==-1:
            if record_from_pointer.id>record.id:
                record.pointer=previous.pointer
                previous.pointer=self.next_pointer
                if previous_pointer!=-1:
                    self.write_record(previous_pointer, previous)
                self.update_next_pointer()
                self.write_record(previous.pointer, record)
            else:
                record_from_pointer.pointer=self.next_pointer
                self.write_record(previous.pointer, record_from_pointer)
                self.update_next_pointer()
                record.pointer=-1
                self.write_record(record_from_pointer.pointer, record)
        elif record_from_pointer.id>record.id:
            previous.pointer=self.next_pointer
            self.write_record(previous.pointer - self.ENTRY_SIZE_IN_BYTES, previous)
            self.update_next_pointer()
            record.pointer=previous.pointer
            self.write_record(previous.pointer, record)
        else:

            self.insert_to_overflow(record_from_pointer, record, previous.pointer)


    def get_page(self, page_num):
        self.num_of_disc_operations+=1
        with open(self.path, 'rb') as file:
            page = []
            record_size = struct.calcsize(self.record_format)
            file.seek(page_num * self.ENTRY_SIZE_IN_BYTES * self.max_entries_on_page)
            for e in range(self.max_entries_on_page):
                record_data = file.read(record_size)
                if not record_data:
                    break  # Koniec pliku

                unpacked_data = struct.unpack(self.record_format, record_data)
                index, *numbers, pointer, isEmpty = unpacked_data
                record = Record(index, numbers)
                record.pointer = pointer
                record.isEmpty = isEmpty
                page.append(record)
        return page

    def check_if_page_is_full(self, page_id):
        record_size = struct.calcsize(self.record_format)
        page_offset=self.PAGE_SIZE_IN_BYTES*page_id
        with open(self.path, 'rb') as file:
            file.seek(page_offset)

            num_of_full_records=0 #nie do usuniecia
            for _ in range(self.max_entries_on_page):
                record_data = file.read(record_size)
                if record_data==b'':
                    break #koniec pliku
                unpacked_data = struct.unpack(self.record_format, record_data)
                record_id, *numbers, pointer, isEmpty= unpacked_data
                if isEmpty ==0:
                    num_of_full_records+=1
            if num_of_full_records==self.max_entries_on_page: return True
            return False

    def update_page(self, page_id, records_on_page):
        self.num_of_disc_operations+=1
        record_size = struct.calcsize(self.record_format)
        page_offset = self.PAGE_SIZE_IN_BYTES * page_id
        with open(self.path, 'r+b') as file:
            file.seek(page_offset)

            for record in records_on_page:

                record_data = struct.pack(self.record_format, record.id, *record.numbers, record.pointer, record.isEmpty)
                file.write(record_data)

    def write_record(self, pointer, record):
        with open(self.path, 'r+b') as file:
            file.seek(pointer)
            record_data = struct.pack(self.record_format, record.id, *record.numbers, record.pointer, 0)
            file.write(record_data)


    def calculate_page_num(self, pointer):
        return math.floor(pointer/self.PAGE_SIZE_IN_BYTES)

    def get_record(self, pointer):
        with open(self.path, 'r+b') as file:
            record_size = struct.calcsize(self.record_format)
            file.seek(pointer)
            record_data = file.read(record_size)
            unpacked_data = struct.unpack(self.record_format, record_data)
            index, *numbers, pointer, isEmpty = unpacked_data
            record = Record(index, numbers)
            record.pointer = pointer
            record.isEmpty = isEmpty
            return record

    def print_file(self):
        with open(self.path, 'rb') as file:

            record_size = struct.calcsize(self.record_format)
            while True:
                record_data = file.read(record_size)
                if not record_data:
                    break  # Koniec pliku

                unpacked_data = struct.unpack(self.record_format, record_data)
                record_id,  *numbers, pointer, isEmpty= unpacked_data
                print(f" Record ID: {record_id}, Numbers: {numbers}, Pointer: {pointer}, isEmpty: {isEmpty}")
