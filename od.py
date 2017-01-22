# encoding=utf-8

import os
import csv
import datetime
import itertools




area_name = 'San Diego May-Oct2016'

path_list = []
for root, dirs, files in os.walk('/Users/liuqianchao/Desktop/ra/od/data/{}'.format(area_name)):
    for file_name in files:
        file_path = os.path.join(root, file_name)
        try:
            path_list.append([file_path, int(file_name.split('_')[3].split('.')[0])])
        except Exception, e:
            print 'error'+file_name
path_list.sort(key=lambda x: x[1])

vin_lat_lng = {}
od = {}


def match():
    # 仅仅用来产生match
    for path in path_list:
        file_path = path[0]
        print file_path
        with open(file_path, 'r') as f:
            reader = csv.reader(f)
            for index, sep_line in enumerate(reader):
                if index>0:
                    vin = sep_line[1]
                    engine_type = sep_line[2]
                    local_time = sep_line[4]
                    year = int(sep_line[5])
                    month = int(sep_line[6])
                    day = int(sep_line[7])
                    hour = int(sep_line[8])
                    minute = int(sep_line[9])
                    second = int(sep_line[10])
                    lat = sep_line[11]
                    lng = sep_line[12]
                    fuel = sep_line[13]
                    num_station = sep_line[14]
                    num_charging_status = sep_line[18]
                    num_exterior = sep_line[19]
                    num_interior = sep_line[20].strip('\r\n')
                    time = str(datetime.datetime(year, month, day, hour, minute, second))

                    # something about od
                    if vin in vin_lat_lng.keys():
                        # compare
                        if lat == vin_lat_lng[vin][2] and lng == vin_lat_lng[vin][3]:
                            # the same lat,lng, update vin_lat_lng
                            vin_lat_lng[vin] = [engine_type,time,lat,lng,fuel,num_station,num_charging_status,num_exterior,num_interior]
                        else:
                            if vin not in od.keys():
                                od[vin] = [[vin_lat_lng[vin], [time,lat,lng,fuel,num_station,num_charging_status,num_exterior,num_interior]]]
                                vin_lat_lng[vin] = [engine_type,time,lat,lng,fuel,num_station,num_charging_status,num_exterior,num_interior]
                            else:
                                od[vin].append([vin_lat_lng[vin], [time,lat,lng,fuel,num_station,num_charging_status,num_exterior,num_interior]])
                                vin_lat_lng[vin] = [engine_type,time,lat,lng,fuel,num_station,num_charging_status,num_exterior,num_interior]
                    else:
                        # this vin's first time appear
                        vin_lat_lng[vin] = [engine_type,time,lat,lng,fuel,num_station,num_charging_status,num_exterior,num_interior]



    to_write = []
    for key in od.keys():
        for item in od[key]:
            to_write.append(','.join([key]+item[0]+item[1]))

    with open('/Users/liuqianchao/Desktop/ra/od/May-Oct2016/{}_match.csv'.format(area_name), 'w') as wf:
        wf.write('vin,engine_type,time,lat,lng,fuel,num_station,num_charging_status,num_exterior,num_interior,time,lat,lng,fuel,num_station,num_charging_status,num_exterior,num_interior\n')
        for line in to_write:
            wf.write(line+'\n')

def compute_distance(lat1,lng1,lat2,lng2):
    return abs(float(lat1)-float(lat2))**2 + abs(float(lng1)-float(lng2))**2


def nearest_car():
    begin_time = datetime.datetime.now()
    time_lat_lng = {}  # likes {'time1':[[lat1,lng1],[lat2,lng2]], 'time2:...'}
    with open('/Users/liuqianchao/Desktop/ra/od/May-Oct2016/{}_match.csv'.format(area_name), 'r') as f:
        for index,line in enumerate(f):
            if 0 < index:
                sep_line = line.split(',')
                time1 = sep_line[2]
                lat1 = sep_line[3]
                lng1 = sep_line[4]
                #
                # time2 = sep_line[10]
                lat2 = sep_line[11]
                lng2 = sep_line[12]

                if time1 not in time_lat_lng:
                    time_lat_lng[time1] = [[lat1, lng1]]
                    time_lat_lng[time1].append([str((float(lat1)+float(lat2))/2.0), str((float(lng1)+float(lng2))/2.0)])
                    time_lat_lng[time1].append([lat2,lng2])
                else:
                    time_lat_lng[time1].append([lat1, lng1])
                    time_lat_lng[time1].append([str((float(lat1)+float(lat2))/2.0), str((float(lng1)+float(lng2))/2.0)])
                    time_lat_lng[time1].append([lat2,lng2])

                # if time2 not in time_lat_lng:
                #     time_lat_lng[time2] = [[lat2, lng2]]
                # else:
                #     time_lat_lng[time2].append([lat2, lng2])



    print datetime.datetime.now()-begin_time

    timelatlng_nearest5 = {}  # looks like {'2016-06-10 07:06:42lat1lng1':[result1,result2,result3,result4,result5],...} where resultx is also a list
    # 遍历整个数据集,产生 timelatlng_nearest5
    tmp_time_list = []  # 用于检验时间是否发生变化
    tmp_time_all_information = {}
    for path in path_list:
        file_path = path[0]
        print file_path
        if len(tmp_time_list)>10:
            tmp_time_list = tmp_time_list[-5:]
        with open(file_path, 'r') as f:
            reader = csv.reader(f)
            for index, sep_line in enumerate(reader):
                if index>0:
                    vin = sep_line[1]
                    engine_type = sep_line[2]
                    local_time = sep_line[4]
                    year = int(sep_line[5])
                    month = int(sep_line[6])
                    day = int(sep_line[7])
                    hour = int(sep_line[8])
                    minute = int(sep_line[9])
                    second = int(sep_line[10])
                    lat = sep_line[11]
                    lng = sep_line[12]
                    fuel = sep_line[13]
                    num_station = sep_line[14]
                    num_charging_status = sep_line[18]
                    num_exterior = sep_line[19]
                    num_interior = sep_line[20].strip('\r\n')
                    time = str(datetime.datetime(year, month, day, hour, minute, second))

                    tmp_time_list.append(time)

                    try:
                        if time != tmp_time_list[-2]:
                            # 迭代到新时间,可以对上一个时间区间(tmp_time_list[-2])进行迭代.
                            if tmp_time_list[-2] in time_lat_lng.keys():
                                for lat_lng in time_lat_lng[tmp_time_list[-2]]:
                                    lat = lat_lng[0]
                                    lng = lat_lng[1]
                                    distance_info = [] # looks like [[0.1,[]]]
                                    # lat,lng与tmp_time_all_information所有经纬度进行计算,得出距离小的的1-5个(距离最小的,index为0为本身)
                                    for item in tmp_time_all_information[tmp_time_list[-2]]:
                                        item_lat = item[3]
                                        item_lng = item[4]
                                        dis = compute_distance(lat, lng,item_lat,item_lng)
                                        distance_info.append([dis, item])
                                    distance_info.sort(key=lambda x: x[0])
                                    timelatlng_nearest5[tmp_time_list[-2]+lat+lng] = [info[1] for info in distance_info[1:6]]
                            tmp_time_all_information = {}
                            tmp_time_all_information[time] = [[vin, engine_type, time, lat, lng, fuel, num_station, num_charging_status, num_exterior, num_interior]]
                        else:
                            # 仍和上个区间一样,
                            tmp_time_all_information[time].append([vin, engine_type, time, lat, lng, fuel, num_station, num_charging_status, num_exterior, num_interior])
                    except Exception, error:
                        print error
                        tmp_time_all_information[time] = [[vin, engine_type, time, lat, lng, fuel, num_station, num_charging_status, num_exterior, num_interior]]

    to_write = []
    with open('/Users/liuqianchao/Desktop/ra/od/May-Oct2016/{}_match.csv'.format(area_name), 'r') as f:
        for index,line in enumerate(f):
            if 0 < index:
                line = line.strip('\n')
                sep_line = line.split(',')
                time = sep_line[2]
                lat1 = sep_line[3]
                lng1 = sep_line[4]
                #
                lat2 = sep_line[11]
                lng2 = sep_line[12]

                #
                middle_lat = str((float(lat1)+float(lat2))/2.0)
                middle_lng = str((float(lng1)+float(lng2))/2.0)

                fifteen_item = list(itertools.chain.from_iterable(timelatlng_nearest5[time+lat1+lng1])) + \
                               list(itertools.chain.from_iterable(timelatlng_nearest5[time+lat2+lng2])) + \
                               list(itertools.chain.from_iterable(timelatlng_nearest5[time+middle_lat+middle_lng]))



                to_write.append(sep_line+fifteen_item)



    with open('/Users/liuqianchao/Desktop/ra/od/May-Oct2016/{}_match_nearest.csv'.format(area_name), 'w') as wf:
        title_15 = 'vin, engine_type, time, lat, lng, fuel, num_station, num_charging_status, num_exterior, num_interior,'*15
        wf.write('vin,engine_type,time,lat,lng,fuel,num_station,num_charging_status,num_exterior,'
                 'num_interior,time,lat,lng,fuel,num_station,num_charging_status,num_exterior,num_interior,'+
                 title_15[:-1]+'\n')

        for item in to_write:
            wf.write(','.join(item)+'\n')

    print datetime.datetime.now() - begin_time


def cut():
    cuts = []  # 用来存储所有>10min的cut [[2016-06-10 07:06:42, 2016-06-04 08:07:21]...]
    tmp_time_list = []  # 用于检验时间是否发生变化

    for path in path_list:
        file_path = path[0]
        print file_path
        if len(tmp_time_list)>10:
            tmp_time_list = tmp_time_list[-5:]
        with open(file_path, 'r') as f:
            reader = csv.reader(f)
            for index, sep_line in enumerate(reader):
                if index>0:
                    year = int(sep_line[5])
                    month = int(sep_line[6])
                    day = int(sep_line[7])
                    hour = int(sep_line[8])
                    minute = int(sep_line[9])
                    second = int(sep_line[10])
                    time = datetime.datetime(year, month, day, hour, minute, second)

                    tmp_time_list.append(time)
                    try:
                        time_1 = tmp_time_list[-2]
                        time_2 = time
                        delta_time = (time_2-time_1).total_seconds()
                        if delta_time > 600:
                            cuts.append([time_1, time_2])

                    except Exception,e:
                        print e

    to_write = []
    with open('/Users/liuqianchao/Desktop/ra/od/May-Oct2016/{}_match_nearest.csv'.format(area_name), 'r') as f:
        for index,item in enumerate(f):
            if index>0:
                item = item.strip('\n')
                item = item.split(',')
                o_time = datetime.datetime.strptime(item[2], "%Y-%m-%d %H:%M:%S")
                d_time = datetime.datetime.strptime(item[10], "%Y-%m-%d %H:%M:%S")
                for times in cuts:
                    time_1 = times[0]
                    time_2 = times[1]
                    if o_time <= time_1 and time_2 <= d_time:
                        # to_write.append(['cross_cuts:{} to {} interval time:{}s'.format(time_1,time_2,(time_2-time_1).total_seconds())]+item)
                        to_write.append([str((time_2-time_1).total_seconds())]+item)
                        break
                else:
                    to_write.append(['0'] + item)

    with open('/Users/liuqianchao/Desktop/ra/od/May-Oct2016/{}_match_nearest_cut.csv'.format(area_name),'w') as wf:
        title_15 = 'vin, engine_type, time, lat, lng, fuel, num_station, num_charging_status, num_exterior, num_interior,'*15
        wf.write('cut_status,vin,engine_type,time,lat,lng,fuel,num_station,num_charging_status,num_exterior,'
                 'num_interior,time,lat,lng,fuel,num_station,num_charging_status,num_exterior,num_interior,'+
                 title_15[:-1]+'\n')
        for item in to_write:
            wf.write(','.join(item)+'\n')

def revise_format():
    to_write = []
    vins = []
    with open('/Users/liuqianchao/Desktop/ra/od/May-Oct2016/{}_match_nearest_cut.csv'.format(area_name),'r') as f:
        for index, item in enumerate(f):
            if index > 0:
                item = item.strip('\n')
                item_sep = item.split(',')

                seq = [3] + [item for item in range(11,162,10)]
                for i in seq:
                    time = datetime.datetime.strptime(item_sep[i], "%Y-%m-%d %H:%M:%S")

                    day_of_year = (time - datetime.datetime.strptime('2016-01-01 0:0:0', "%Y-%m-%d %H:%M:%S")).days + 1
                    minute_of_day = time.hour * 60 + time.minute + time.second/60.0
                    content = item_sep[0:i] + [str(day_of_year)+','+str(minute_of_day)] + item_sep[i+1:]
                    item_sep = content
                to_write.append(content)
                vin = item_sep[1]

                if vin not in vins:
                    vins.append(vin)


    with open('/Users/liuqianchao/Desktop/ra/od/May-Oct2016/{}_select.csv'.format(area_name),'w') as wf:
        title_15 = 'vin, engine_type, day_of_year, minute_of_day, lat, lng, fuel, num_station, num_charging_status, num_exterior, num_interior,'*15
        wf.write('cut_status,vin,engine_type,day_of_year,minute_of_day,lat,lng,fuel,num_station,num_charging_status,'
                 'num_exterior,num_interior,day_of_year,minute_of_day,lat,lng,fuel,num_station,num_charging_status,num_exterior,num_interior,'+
                 title_15[:-1]+'\n')
        for line in to_write:
            # vins
            seq = [1] + [item for item in range(19,169,10)]
            for i in seq:
                to_convert_vin = line[i]
                if to_convert_vin not in vins:
                    vins.append(to_convert_vin)
                line = line[0:i] + [str(vins.index(line[i]) + 1)] + line[i+1:]
            # engine_type
            engine_type_seq = [2] + [item for item in range(20,169,10)]
            for i in engine_type_seq:
                if line[i] == 'CE':
                    line[i] = '0'
                elif line[i] == 'ED':
                    line[i] = '1'
                else:
                    print line[i]
            try:
                wf.write(','.join(line)+'\n')
            except Exception,e:
                print line

match()
nearest_car()
cut()
#revise_format()
            #print (time - datetime.datetime.strptime('2016-01-01 0:0:0', "%Y-%m-%d %H:%M:%S")).days
            # 26.csv 3345 1053
# 62.csv 1 82761  occur at line1 2016-06-04 08:07:21  2016-06-10 07:06:42
# 115.csv 26096 644
# 119.csv 23174 5023
# 129.csv 16178 1204
# 150.csv 1 1965
# 154.csv 25262 2081
# 196.csv 13511 800
# 224.csv 1 71745
# 256.csv 1 1135
# 279.csv 1 54944