import struct
from record import Record
class MainFile():
    def __init__(self, path, init_num_pages):
        self.path=path
        self.ENTRY_SIZE_IN_BYTES = 32
        self.PAGE_SIZE_IN_BYTES = 10*32
        self.max_entries_on_page = 10
        self.record_format = 'i' + 'IIIII' + 'i' + 'I'
        self.initialize_mainFile(init_num_pages)
        self.stored_records=1
        self.num_of_disc_operations=0
        self.num_of_pages=init_num_pages

    def initialize_mainFile(self, num_pages):
        for i in range(num_pages):
            self.initialize_mainFile_page(i)


    def initialize_mainFile_page(self, num_page):
        page=[]
        for i in range(self.max_entries_on_page):
            record=Record(-1, [0,0,0,0,0])
            if i ==0:
                record.isEmpty=0 #pierwszy rekord na każdej stronie nie usuwam
            page.append(record)
        if num_page == 0:
            self.write_empty_page_to_file(page)
        else:
            self.write_page(num_page, page)


    def write_empty_page_to_file(self, page):
        with open(self.path, 'wb') as file:
            for record in page:
                numbers=record.numbers
                record_data = struct.pack(self.record_format, record.id, *numbers, -1, record.isEmpty)
                file.write(record_data)

    def write_page(self, page_id, records_on_page):
        record_size = struct.calcsize(self.record_format)
        page_offset = self.PAGE_SIZE_IN_BYTES * page_id
        with open(self.path, 'r+b') as file:
            file.seek(page_offset)

            for record in records_on_page:
                numbers = record.numbers
                record_data = struct.pack(self.record_format, record.id, *numbers, -1, 1)
                file.write(record_data)

    def update_page(self, page_id, records_on_page, path):
        self.num_of_disc_operations+=1
        record_size = struct.calcsize(self.record_format)
        page_offset = self.PAGE_SIZE_IN_BYTES * page_id
        with open(self.path, 'r+b') as file:
            file.seek(page_offset)

            for record in records_on_page:

                record_data = struct.pack(self.record_format, record.id, *record.numbers, record.pointer, record.isEmpty)
                file.write(record_data)
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