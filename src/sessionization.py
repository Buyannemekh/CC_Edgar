import csv
import datetime
import time
import os

dirpath = os.getcwd()
print("current directory is : " + dirpath)

path_to_file = './input/'
os.chdir(path_to_file)
print("current directory is : " + os.getcwd())

# get inactivity period from .txt
inactivity_period_file = open('inactivity_period.txt', mode='r')
inactivity_period = int(inactivity_period_file.read())

# datastructure that holds info from the input file
info = {}


# convert HH:MM:SS to seconds
def get_sec(time_str):
    # print(time_str)
    h, m, s = time_str.split(':')
    return int(h) * 3600 + int(m) * 60 + int(s)


# check if IP exists in the previous time frame, if it exists save IP information and
# remove from the previous time
def check_if_ip_exists_before(cur_time, inact_time, ip, new_ip_time_data):
    global info
    for t in range(cur_time - 1, cur_time - inact_time - 1, -1):
        if t >= 0:
            if t in info and ip in info[t]:
                new_ip_time_data['old datetime'] = info[t][ip]['old datetime']
                new_ip_time_data['doc'] = info[t][ip]['doc'] + 1
                info[t].pop(ip)
    return new_ip_time_data


# if time already exists, write new IP address information if IP is not there, else update doc
def copy_data_IP(cur_time, inact_time, ip, new_ip_time_data):
    # if IP exists in the current time, update number of documents
    global info
    if ip in info[cur_time]:
        new_ip_time_data['doc'] = new_ip_time_data['doc'] + 1
    else:
        new_ip_time_data = check_if_ip_exists_before(cur_time, inact_time, ip, new_ip_time_data)
    return new_ip_time_data


# convert 2017-06-30 00:00:00 to epoch, so that it's feasible to keep track of inactivity_period
def convert_datetime_to_ecoch(my_time):
    my_format = "%Y-%m-%d %H:%M:%S"
    epoch = int(time.mktime(time.strptime(my_time, my_format)))
    return epoch


# convert epoch to date time, this is useful when writing the information to output file
def convert_epoch_to_datetime(ts_epoch):
    ts = datetime.datetime.fromtimestamp(ts_epoch).strftime('%Y-%m-%d %H:%M:%S')
    return ts


# find expired sessions and delete it from dictionary
def print_and_delete_expired_session(cur_time_in_sec, inactivity_period, f):
    output = ""
    expired_timel = []
    global info
    for t in info.keys():
        if (cur_time_in_sec - t) > inactivity_period:
            for ip in info[t].keys():
                output = ip
                olddatetime = info[t][ip]['old datetime']
                datetime = info[t][ip]['datetime']
                duration = datetime - olddatetime + 1
                doc = info[t][ip]['doc']
                output = output + "," + convert_epoch_to_datetime(olddatetime) + "," + convert_epoch_to_datetime(
                    datetime) + "," + str(duration) + "," + str(doc)
                # write to file
                # print(output)
                f.write(output + "\n")

            expired_timel.append(t)
    # delete inactive time records
    for t_to_pop in expired_timel:
        info.pop(t_to_pop)


# take corresponding column values from a row
def take_info_from_row(row, ip_index, date_index, time_index):
    global info
    ip = row[ip_index]
    date = row[date_index]
    # date = datetime.datetime.strptime(date, '%m/%d/%y').strftime('%Y-%m-%d')
    time = row[time_index]
    my_time = date + " " + time
    doc = 1
    new_ip_time_data_epoch = {
        'old datetime': convert_datetime_to_ecoch(my_time),
        'datetime': convert_datetime_to_ecoch(my_time),
        'doc': doc}
    return ip, new_ip_time_data_epoch


# add the row information from csv to dictionary
def add_to_dict(row, ip_index, date_index, time_index, inactivity_period, f):
    global info
    ip, new_ip_time_data = take_info_from_row(row, ip_index, date_index, time_index)
    cur_time_in_sec = new_ip_time_data['datetime']
    # if current time is in the dictionary,
    # 1. check if current IP reading is in the current time
    # 2. check if current IP reading is in the previous time
    if cur_time_in_sec in info:
        new_ip_time_data = copy_data_IP(cur_time_in_sec, inactivity_period, ip, new_ip_time_data)
        info[cur_time_in_sec][ip] = new_ip_time_data
    # if current time is not in the dictionary,
    # 1. check if the current IP reading is in the previous time
    else:
        new_ip_time_data = check_if_ip_exists_before(cur_time_in_sec, inactivity_period, ip, new_ip_time_data)
        info[cur_time_in_sec] = {ip: new_ip_time_data}

    # print and delete expired record
    print_and_delete_expired_session(cur_time_in_sec, inactivity_period, f)


# once it finishes reading all rows from csv, and
# if dictionary is not empty, print it out in instructed order
def print_remaining(info):
    sort_this_dict = {}
    # convert dictionary to list
    for t, value in info.items():
        sort_this_dict = {**sort_this_dict, **value}
    # sort the list by first accessed date and last accessed date
    dr = sorted(sort_this_dict.items(), key=lambda dct: (dct[1]['old datetime'], dct[1]['datetime']))
    print_from_list(dr, f)


# printing sorted remaining information
def print_from_list(dr, f):
    output = ""
    for i in range(0, len(dr)):
        row = dr[i]
        ip = row[0]
        output = ip
        olddatetime = row[1]['old datetime']
        datetime = row[1]['datetime']
        duration = datetime - olddatetime + 1
        doc = row[1]['doc']
        output = output + "," + convert_epoch_to_datetime(olddatetime) + "," + convert_epoch_to_datetime(
            datetime) + "," + str(duration) + "," + str(doc)
        # write to file
        f.write(output + "\n")
        # print(output)


# read csv file line by line and get Time as key,
# value is in list that includes all IP addresses that accessed at the Time
with open('log.csv', mode='r', encoding='utf-8-sig') as infile:
    reader = csv.reader(infile)
    headers = next(reader)
    ip_index = headers.index("ip")
    date_index = headers.index("date")
    time_index = headers.index("time")
    path_to_file = '../output/'
    os.chdir(path_to_file)
    f = open('sessionization.txt', 'w')
    # read each row
    for row in reader:
        add_to_dict(row, ip_index, date_index, time_index, inactivity_period, f)
    # print(info)
    if bool(info):
        print_remaining(info)
    f.close()
