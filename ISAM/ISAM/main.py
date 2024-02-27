import random

from isam import ISAM
from indexFile import IndexFIle
from mainFile import MainFile
from overflowFile import OverflowFile
import struct

def generate_input_data(number_of_records, path):
    with open(path, 'w') as file:
        id=1
        for i in range(number_of_records):
            record_id = id
            id+=1
            numbers = [random.randint(1, 9) for _ in range(5)]
            numbers_str = ' '.join(map(str, numbers))
            numbers_str=numbers_str.replace(" ","")

            record_data = f'1 {record_id} {numbers_str}\n'
            file.write(record_data)
if __name__ == '__main__':
    indexFile=IndexFIle("C:\\Users\\48516\\PycharmProjects\\sbd_poprawka\\dataFiles\\indexFile.txt")
    mainFile=MainFile("C:\\Users\\48516\\PycharmProjects\\sbd_poprawka\\dataFiles\\mainFile.txt", 1)
    overflowFile=OverflowFile("C:\\Users\\48516\\PycharmProjects\\sbd_poprawka\\dataFiles\\overflowFile.txt", 1)
    inputFile="C:\\Users\\48516\\PycharmProjects\\sbd_poprawka\\dataFiles\\inputFile.txt"
    generate_input_data(200, inputFile)
    isam=ISAM(indexFile, mainFile, overflowFile, 0.5)
    isam.fill(inputFile)


