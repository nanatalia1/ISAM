import shutil
import struct
from record import Record
from indexFile import IndexFIle
from mainFile import MainFile
from overflowFile import OverflowFile
import math

class ISAM():
    def __init__(self, indexFile, mainFile, overflowFile, alpha):
        self.indexFile= indexFile
        self.mainFile=mainFile
        self.overflowFile=overflowFile
        self.commandSize= 28
        self.alpha=alpha
        self.num_of_disc_operations=0
        self.reorganization_counter=0

    def fill(self, source_file_path=None):
        if source_file_path is None:
            self.interactiveMode()
        else:
            self.readFromInputFile(source_file_path)


    def interactiveMode(self):
        print('''Commands:
        1 - insert record
        2 - get
        3 - reorganize
        4 - print
        5- exit
        ''')
        while True:
            command=int(input("Insert command"))
            if command==5:
                self.num_of_disc_operations=self.mainFile.num_of_disc_operations+self.indexFile.num_of_disc_operations+self.overflowFile.num_of_disc_operations
                print("Number of disc operations: ")
                print(self.num_of_disc_operations)
                print("Number of automatic reorganizations: ")
                print(self.reorganization_counter)

                break
            if command==1:
                id=int(input("Insert id"))
                values=[]
                for i in range(5):
                    value = int(input(f"Insert {i + 1} value: "))
                    values.append(int(value))

                command_byte = struct.pack('<I', command)
                id_byte = struct.pack('<I', id)
                values_bytes = struct.pack('<5I', *values)

                packed_data = command_byte + id_byte + values_bytes
                self.processCommand(packed_data)
            if command==4:
                command_byte = struct.pack('<I', command)
                self.processCommand(command_byte)
            if command==3:
                self.reorganize()
            if command==2:
                id = int(input("Insert id"))
                record=self.get_record(id)
                if record==None:
                    print(f"Can't find record with id: {id}")
                else:
                    print("Found record: ")
                    print(f" Record ID: {record.id}, Numbers: {record.numbers}, Pointer: {record.pointer}, isEmpty: {record.isEmpty}")

    def get_record(self, index):
        page_to_insert = self.indexFile.find_page_for_record(index)
        records_on_page = self.mainFile.get_page(page_to_insert)
        for r in records_on_page:
            if r.id==index:
                return r
        for i in range(self.overflowFile.overflow_pages):
            records_on_page = self.overflowFile.get_page(i)
            for r in records_on_page:
                if r.id == index:
                    return r
        return None

    def readFromInputFile(self, path):
        try:
            with open(path, 'r') as file:
                for line in file:
                    if not line:
                        break
                    line = line.split()
                    command_type=int(line[0])
                    if command_type==1:#INSERT
                        index = int(line[1])
                        byte = 8
                        number = line[2]
                        values = [int(digit) for digit in str(number)]


                        command_byte = struct.pack('<I', command_type)
                        id_byte = struct.pack('<I', index)
                        values_bytes = struct.pack('<5I', *values)

                        packed_data = command_byte + id_byte + values_bytes
                        self.processCommand(packed_data)
                    elif command_type==2: #GET
                        index = line[2]
                        ...
                    elif command_type==3:#REORGANIZE
                        ...
                    elif command_type==4:#PRINT
                        self.print_files()
                    else:
                        print("wrong command type")


            self.interactiveMode()
        except FileNotFoundError:
            print(f"File not found: {path}")

    def processCommand(self, command):
        command_type=struct.unpack('<I', command[0:4])[0]

        if command_type==1:#INSERT
            index = struct.unpack('<I', command[4:8])[0]
            values = []
            byte = 8
            for i in range(5):
                end_byte = byte + 4
                value = struct.unpack('<I', command[byte:end_byte])[0]
                values.append(int(value))
                byte = end_byte
            record = Record(index, values)
            self.insert_record(record)
        elif command_type==2: #GET
            index = struct.unpack('<I', command[4:8])[0]
            ...
        elif command_type==3:#REORGANIZE
            self.reorganize()
        elif command_type==4:#PRINT
            self.print_files()
        else:
            print("wrong command type")

    def insert_record(self, record):
        page_to_insert=self.indexFile.find_page_for_record(record.id)
        if page_to_insert!=-1:
            is_page_full=self.mainFile.check_if_page_is_full(page_to_insert)
            records_on_page = self.mainFile.get_page(page_to_insert)
            if is_page_full:
                self.insert_to_overflow(records_on_page, record, page_to_insert)
            else:
                self.insert_to_mainFile(records_on_page, record, page_to_insert)


        else:
            print(f"Can't insert {record.id}")
        #self.print_files()
    def insert_to_mainFile(self, records_on_page, record, page_to_insert):
        self.mainFile.stored_records+=1
        for r in records_on_page:
            if r.isEmpty == 1:
                r.id = record.id
                r.numbers = record.numbers
                r.isEmpty = 0
                r.pointer = -1
                break
        sorted_records = sorted(
            records_on_page,

            key=lambda record: (record.isEmpty, record.id)  # Sortowanie wg. aktywności i wartości klucza
        )
        self.mainFile.update_page(page_to_insert, sorted_records, self.mainFile.path)
    def overflow_full(self):
        for p in range(self.overflowFile.overflow_pages):
            page=self.overflowFile.get_page(p)
            self.overflowFile.num_of_disc_operations-=1
            for r in page:
                if r.isEmpty==1:
                    return False
        return True

    def insert_to_overflow(self, records_on_page, record, page_to_insert):
        self.overflowFile.stored_records+=1
        for r in records_on_page:
            if r == records_on_page[-1]:
                previous = r
                break
            if r.id > record.id:
                break
            else:
                previous = r

        if previous.pointer==-1:
            previous.pointer=self.overflowFile.next_pointer
            self.overflowFile.update_next_pointer()
            self.overflowFile.insert(record)
            self.mainFile.update_page(page_to_insert, records_on_page, self.mainFile.path)
        else:
            previous_pointer=-1 #plik main
            self.overflowFile.insert_to_overflow(previous, record, previous_pointer)
            self.mainFile.update_page(page_to_insert, records_on_page, self.mainFile.path)
        if self.overflowFile.check_if_page_is_full(self.overflowFile.current_active_page):
            if self.overflowFile.current_active_page==self.overflowFile.overflow_pages:
                self.reorganize()
            else:
                self.overflowFile.current_active_page+=1
        if self.overflow_full():
            self.reorganize()
        # if self.overflow_full():
        #     self.reorganize()

    def print_files(self):
        print("Index file: ")
        self.indexFile.print_file()
        print("Main file: ")
        self.mainFile.print_file()
        print("Overflow file: ")
        self.overflowFile.print_file()

    # def get_next_record(self, record):
    #     page_to_insert = self.indexFile.find_page_for_record(record.id)
    #     next_record=None
    #     while page_to_insert < self.mainFile.num_of_pages:
    #         if record.pointer!=-1:
    #             next_record=self.overflowFile.get_record(record.pointer)
    #         else:
    #
    #                 records_on_page = self.mainFile.get_page(page_to_insert)
    #                 for r in records_on_page:
    #                     if r.id>record.id:
    #                         next_record=r
    #                         break
    #         page_to_insert+=1
    #     return next_record
    def get_next_record_from_main(self, page_num, record):
        if page_num>=self.mainFile.num_of_pages:
            return None
        records_on_page = self.mainFile.get_page(page_num)

        for r in records_on_page:
            if r.id>record.id and r.isEmpty==0:
                return r
        return self.get_next_record_from_main(page_num+1, record)

    def get_next_record(self, record):
        page_to_insert = self.indexFile.find_page_for_record(record.id)
        if record.pointer!=-1:
            return self.overflowFile.get_record(record.pointer)
        else:
            return self.get_next_record_from_main(page_to_insert, record)

    def reorganize(self):
        self.reorganization_counter+=1
        # print("Main file pre: ")
        # self.mainFile.print_file()
        # print("Overflow file pre: ")
        # self.overflowFile.print_file()
        # print("Index file pre: ")
        # self.indexFile.print_file()
        new_main_page_num=math.ceil((self.mainFile.stored_records+self.overflowFile.stored_records)/(self.mainFile.max_entries_on_page*self.alpha))
        new_index_page_num=math.ceil(new_main_page_num/self.indexFile.max_entries_on_page)
        new_overflow_page_num=math.ceil(0.2*new_main_page_num)
        if new_overflow_page_num==0:
            new_overflow_page_num=1
        num_of_full_records_on_page=int(self.alpha*self.mainFile.max_entries_on_page)
        num_of_empty_records_on_page=self.mainFile.max_entries_on_page-num_of_full_records_on_page
        #stworzenie nowych plików
        indexFile_temp = IndexFIle("C:\\Users\\48516\\PycharmProjects\\sbd_poprawka\\dataFiles\\indexFile_temp.txt")
        indexFile_temp.max_number_of_pages=new_index_page_num
        mainFile_temp = MainFile("C:\\Users\\48516\\PycharmProjects\\sbd_poprawka\\dataFiles\\mainFile_temp.txt", new_main_page_num)
        overflowFile_temp = OverflowFile("C:\\Users\\48516\\PycharmProjects\\sbd_poprawka\\dataFiles\\overflowFile_temp.txt", new_overflow_page_num)
        overflowFile_temp.overflow_pages=new_overflow_page_num

        new_page=[]
        records_on_first_page=self.mainFile.get_page(0)
        current_record=records_on_first_page[0]
        new_page.append(current_record)
        current_page=0
        add_index=False
        while current_record!=None:
            current_record=self.get_next_record(current_record)

            if current_record==None:

                if new_page and current_page<=new_main_page_num:
                    self.mainFile.update_page(current_page, new_page, mainFile_temp.path)
                break

            if add_index==True:
                #self.indexFile.add_entry(current_record.id)
                indexFile_temp.entries.append(current_record.id)
                add_index=False
            new_page.append(current_record)
            if len(new_page)==num_of_full_records_on_page:
                for i in range(num_of_empty_records_on_page):
                    empty_record=Record(-1, [0,0,0,0,0])
                    empty_record.isEmpty=1
                    empty_record.pointer=-1
                    new_page.append(empty_record)
                # for r in new_page:
                #     r.pointer=-1
                mainFile_temp.update_page(current_page, new_page, mainFile_temp.path)
                new_page.clear()
                current_page+=1
                add_index=True

        for n in range(new_main_page_num):
            records_on_page=mainFile_temp.get_page(n)
            for r in records_on_page:
                r.pointer=-1
            mainFile_temp.update_page(n, records_on_page, mainFile_temp.path)
        # print("new main")
        # mainFile_temp.print_file()


        indexFile_temp.write_index_to_file()
        shutil.move(mainFile_temp.path, self.mainFile.path)
        shutil.move(indexFile_temp.path, self.indexFile.path)
        shutil.move(overflowFile_temp.path, self.overflowFile.path)
        self.overflowFile.next_pointer=0
        #self.overflowFile.stored_records=0
        self.overflowFile.current_active_page=0
        #self.mainFile.stored_records=0
        print("Reorganized")
        self.mainFile.num_of_pages=mainFile_temp.num_of_pages
        self.indexFile.current_num_of_pages=indexFile_temp.current_num_of_pages
        self.indexFile.entries=indexFile_temp.entries
        self.overflowFile.current_active_page=0
        self.overflowFile.overflow_pages=overflowFile_temp.overflow_pages
        self.indexFile.max_number_of_pages = new_index_page_num

        print("new main:")
        self.mainFile.print_file()
        print("new index: ")
        self.indexFile.print_file()
        print("new overflow:")
        self.overflowFile.print_file()



