import re


def read_file(file_name):
    try:
        with open(file_name, "r") as f:
            fft_data = f.readlines()
        f.close()
    except FileNotFoundError:
        print("File not found")
        return None
    else:
        return fft_data


def is_number(num):
    try:
        float(num)
    except ValueError:
        return False
    else:
        return True


def find_start_index(fft_data):
    for i, line in enumerate(fft_data):
        if is_number(line[0:5]):
            return i - 1
        else:
            return None


def parse_data(file_name):
    fft_data = read_file(file_name)
    start_index = find_start_index(fft_data)

    header = fft_data[start_index]
    header = header.replace("Time (s),", " ")
    header = re.sub("AI 1/AmplFFT \(", "", header)
    header = re.sub("(?<=\d) Hz\)", ",", header)
    del fft_data[0:start_index]

    fft_data[0] = header

    for i, value in enumerate(fft_data):
        value = list(value.split(","))[0:-1]
        value = [float(ele) for ele in value]
        fft_data[i] = value
    return fft_data


file_name = "file3.txt"
fft_data_parsed = parse_data(read_file(file_name))
