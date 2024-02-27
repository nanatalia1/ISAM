import struct
class IndexFIle():
    def __init__(self, path):
        self.ENTRY_SIZE_IN_BYTES = 4
        self.PAGE_SIZE_IN_BYTES = 10*4
        self.max_entries_on_page=10
        self.entries=[]
        self.blocking_factor=self.PAGE_SIZE_IN_BYTES/self.ENTRY_SIZE_IN_BYTES
        #self.blocking_factor=4
        self.path=path
        self.current_num_of_pages=1
        self.max_number_of_pages=1
        self.record_format='i'
        self.last_page_last_entry=None
        self.initialize_index_file()
        self.num_of_disc_operations=0


    def initialize_index_file(self):
        with open(self.path, 'wb') as file:
            file.truncate(0)
        #self.entries.clear()
        #na początku tylko jedna strona
        self.entries.append(-1)
        self.write_index_to_file()

    def write_index_to_file(self):
        with open(self.path, 'wb') as file:
            for i in self.entries:
                format='i'
                data=struct.pack(format, i)
                file.write(data)

    def update_page(self):
        self.num_of_disc_operations+=1
        page_offset = self.PAGE_SIZE_IN_BYTES * self.current_num_of_pages
        with open(self.path, 'r+b') as file:
            file.seek(page_offset)

            for record in self.entries:

                record_data = struct.pack(self.record_format, record.id, *record.numbers, record.pointer, record.isEmpty)
                file.write(record_data)


    def add_entry(self, entry):
        self.entries.append(entry)
        if len(self.entries)==self.blocking_factor:
            self.update_page()
            self.current_num_of_pages+=1

    def get_page(self, page_num):
        self.num_of_disc_operations+=1
        with open(self.path, 'rb') as file:
            page=[]
            record_size = struct.calcsize(self.record_format)
            file.seek(page_num * self.ENTRY_SIZE_IN_BYTES * self.max_entries_on_page)
            for e in range(self.max_entries_on_page):
                record_data = file.read(record_size)
                if not record_data:
                    break  # Koniec pliku

                unpacked_data = struct.unpack(self.record_format, record_data)
                index = unpacked_data[0]
                page.append(index)
        #print(page)
        return page
    def check_entries(self, index):
        if len(self.entries)==1:
          return 0
        for e in self.entries:
            if index<e:
                page_index = self.entries.index(e)
                if page_index==0:
                    if not self.last_page_last_entry:
                        return -1
                    return self.last_page_last_entry
                return page_index-1
        return len(self.entries)



    def check_page(self, index, page_num):
        page=self.get_page(page_num)#strona pliku indexowego

        if len(page)==1:
            return 0
        for p in page:
            if index<p:
                page_index=int(page.index(p)+(self.blocking_factor*page_num))
                if page_index==self.max_entries_on_page:
                    self.last_page_last_entry=index
                if page_index==0:
                    if not self.last_page_last_entry:
                        return -1
                    return self.last_page_last_entry
                return page_index-1
        if page:
            self.last_page_last_entry=page[-1]
            self.last_page_page=page_num
        if page:
            if page_num==self.max_number_of_pages-1:
                if page[-1]<=index:
                    page_index=int(page.index(page[-1])+(self.blocking_factor*page_num))
                    return page_index
        elif not page:
            if self.last_page_last_entry<index:
                return self.last_page_page
        return -1

    def find_page_for_record(self, index):
        #return self.check_entries(index)
        self.last_page_last_entry=None
        self.last_page_page=None
        for page in range(self.max_number_of_pages):
            page_to_put=self.check_page(index, page)
            if page_to_put!=-1:
                return page_to_put
        return -1

    def print_file(self):
        with open(self.path, 'rb') as file:

            record_size = struct.calcsize(self.record_format)
            while True:
                record_data = file.read(record_size)
                if not record_data:
                    break  # Koniec pliku

                unpacked_data = struct.unpack(self.record_format, record_data)
                record_id, = unpacked_data
                print(f" Record ID: {record_id}")

