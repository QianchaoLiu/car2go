# encoding=utf-8
"""
date: 2016/11/30
"""
import os
import csv
import datetime
import pickle

def path_list(area):
    pathlist = []
    for root, dirs, files in os.walk('/Users/liuqianchao/Desktop/ra/od/data/{}'.format(area)):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            try:
                pathlist.append([file_path, int(file_name.split('_')[3].split('.')[0])])
            except Exception, e:
                print 'error'+file_name
    pathlist.sort(key=lambda x: x[1])
    return pathlist


def grid_size(area= "San Diego May-Oct2016"):
    # 25x25 grid
    min_lat = 32.71682
    max_lat = 32.71682
    min_lng = -117.15222
    max_lng = -117.15222

    pathlist = path_list(area)

    for path in pathlist:
        with open(path[0], 'r') as f:
            reader = csv.reader(f)
            for i, seq_item in enumerate(reader):
                if i > 0:
                    lat = float(seq_item[11])
                    lng = float(seq_item[12])
                    if lng > -110:
                        break
                        # 87.csv: St Paul?
                    if lat < min_lat:
                        min_lat = lat
                    if lat > max_lat:
                        max_lat = lat
                    if lng < min_lng:
                        min_lng = lng
                    if lng > max_lng:
                        max_lng = lng

    return min_lat, max_lat, min_lng, max_lng
    # (32.69223, 32.88993, -117.2596, -117.00902)


def id(grid, area="San Diego May-Oct2016"):
    result = [[0]*25 for _ in range(25)]

    # id
    pathlist = path_list(area)
    min_lat = grid[0]
    max_lat = grid[1]
    diff_lat_per_grid = (max_lat - min_lat)/25.0
    min_lng = grid[2]
    max_lng = grid[3]
    diff_lng_per_grid = (max_lng - min_lng)/25.0
    for path in pathlist:
        with open(path[0], 'r') as f:
            reader = csv.reader(f)
            for index, seq_item in enumerate(reader):
                if index > 0:
                    lat = float(seq_item[11])
                    lng = float(seq_item[12])
                    if lng > -110:
                        break
                    i = int((max_lat - lat)/diff_lat_per_grid)
                    j = int((lng - min_lng)/diff_lng_per_grid)
                    if i == 25:
                        i = 24
                    if j == 25:
                        j = 24

                    result[i][j] += 1

    id_list = []
    for i in range(25):
        for j in range(25):
            if result[i][j] != 0:
                id_list.append(25*i + j+1)
    return id_list

def x(grid, id_list, area="San Diego May-Oct2016"):

    pathlist = path_list(area)
    min_lat = grid[0]
    max_lat = grid[1]
    diff_lat_per_grid = (max_lat - min_lat)/25.0
    min_lng = grid[2]
    max_lng = grid[3]
    diff_lng_per_grid = (max_lng - min_lng)/25.0

    fore5time = [-1,-1,-1,-1,-1,-1,-1]
    # time series
    tmp = ''
    result = {}
    for path in pathlist:
        print '{}/{}'.format(path[1], len(pathlist))
        with open(path[0], 'r') as f:
            reader = csv.reader(f)
            info = []
            for index, seq_item in enumerate(reader):
                if index > 0:
                    engine_type = seq_item[2]
                    fuel = float(seq_item[13])
                    year = int(seq_item[5])
                    month = int(seq_item[6])
                    day = int(seq_item[7])
                    hour = int(seq_item[8])
                    minute = int(seq_item[9])
                    second = int(seq_item[10])
                    time = str(datetime.datetime(year, month, day, hour, minute, second))
                    lat = float(seq_item[11])
                    lng = float(seq_item[12])
                    info.append([engine_type, fuel, lat, lng])
                    if time != tmp and tmp != '':
                        fore5time.pop(0)
                        fore5time.append(tmp)
                        # process previous time
                        process_id_list = []
                        for id in id_list:
                            index = tmp +'/' + str(id)
                            # ce#, ce_avg_fuel, max_fuel, min_fuel, ....
                            result[index] = [0, 0, 0, 0, 0, 0, 0, 0]

                        for item in info:
                            fuel = item[1]
                            lat = item[2]
                            lng = item[3]
                            if lng > -110:
                                break
                            i = int((max_lat - lat)/diff_lat_per_grid)
                            j = int((lng - min_lng)/diff_lng_per_grid)
                            if i == 25:
                                i = 24
                            if j == 25:
                                j = 24
                            id = i*25 + j+1
                            if id not in process_id_list:
                                process_id_list.append(id)

                            if item[0] == 'ED':
                                result[tmp + '/' + str(id)][4] += 1.0
                                result[tmp + '/' + str(id)][5] += fuel
                                if result[tmp + '/' + str(id)][4] == 1.0:
                                    result[tmp + '/' + str(id)][6] = fuel
                                    result[tmp + '/' + str(id)][7] = fuel
                                else:
                                    if fuel > result[tmp + '/' + str(id)][6]:
                                        result[tmp + '/' + str(id)][6] = fuel
                                    if fuel < result[tmp + '/' + str(id)][7]:
                                        result[tmp + '/' + str(id)][7] = fuel
                            elif item[0] == 'CE':
                                result[tmp + '/' + str(id)][0] += 1.0
                                result[tmp + '/' + str(id)][1] += fuel
                                if result[tmp + '/' + str(id)][0] == 1.0:
                                    result[tmp + '/' + str(id)][2] = fuel
                                    result[tmp + '/' + str(id)][3] = fuel
                                else:
                                    if fuel > result[tmp + '/' + str(id)][2]:
                                        result[tmp + '/' + str(id)][2] = fuel
                                    if fuel < result[tmp + '/' + str(id)][3]:
                                        result[tmp + '/' + str(id)][3] = fuel
                            else:
                                print 'error'
                        for id in process_id_list:
                            if result[tmp + '/' + str(id)][0]!=0:
                                result[tmp + '/' + str(id)][1] = result[tmp + '/' + str(id)][1]/result[tmp + '/' + str(id)][0]
                            if result[tmp + '/' + str(id)][4]!=0:
                                result[tmp + '/' + str(id)][5] = result[tmp + '/' + str(id)][5]/result[tmp + '/' + str(id)][4]

                        # current time: 8 grid around
                        for id in id_list:
                            index = tmp +'/' + str(id)
                            current_value = result[index]
                            neighbor_value = [0,0,0,0,0,0,0,0]
                            seq = [-26,-25,-24,-1,1,24,25,26]
                            for plus in seq:
                                try:
                                    value = result[tmp + '/' +str(id+plus)]
                                except Exception,e:
                                    pass
                                else:
                                    if value[0] != 0:
                                        neighbor_value[1] = (neighbor_value[0]*neighbor_value[1] + value[0]*value[1])/(neighbor_value[0] + value[0])
                                    neighbor_value[0] += value[0]
                                    neighbor_value[2] = max(neighbor_value[2], value[2])

                                    if neighbor_value[3] == 0:
                                        neighbor_value[3] = value[3]
                                    else:
                                        neighbor_value[3] = min(neighbor_value[3], value[3])


                                    if value[4] != 0:
                                        neighbor_value[5] = (neighbor_value[4]*neighbor_value[5] + value[4]*value[5])/(neighbor_value[4] + value[4])
                                    neighbor_value[4] += value[4]
                                    neighbor_value[6] = max(neighbor_value[6], value[6])
                                    if neighbor_value[7] == 0:
                                        neighbor_value[7] = value[7]
                                    else:
                                        neighbor_value[7] = min(neighbor_value[7], value[7])
                            result[index] = current_value + neighbor_value


                        # current grid, and previous time
                        for id in id_list:
                            index = tmp +'/' + str(id)
                            current_value = result[index]
                            previous_value = []

                            for foretime in fore5time[:-1][::-1]:
                                if foretime == -1:
                                    previous_value += [-1,-1,-1,-1,-1,-1,-1,-1]
                                else:
                                    previous_value += result[foretime+'/'+str(id)][0:8]

                            result[index] = current_value + previous_value

                        info = []
                        # print time
                    tmp = time

    with open('/Users/liuqianchao/Desktop/ra/demand/x1.csv','w') as wf:
        wf.write('time,id,ce#,ce_avg_fuel,ce_max_fuel,ce_min_fuel,ed#,ed_avg_fuel,ed_max_fuel,ed_min_fuel,n8_ce#,'
                 'n8_ce_avg_fuel,n8_ce_max_fuel,n8_ce_min_fuel,n8_ed#,n8_ed_avg_fuel,n8_ed_max_fuel,n8_ed_min_fuel\n')
        keylist = result.keys()
        keylist.sort()
        for key in keylist:
            time = key.split('/')[0]
            id = key.split('/')[1]
            value = result[key]
            content = [time,id]+value
            content = [str(item) for item in content]
            wf.write(','.join(content)+'\n')



def y(grid, pkl=True):
    output = []

    min_lat = grid[0]
    max_lat = grid[1]
    diff_lat_per_grid = (max_lat - min_lat)/25.0
    min_lng = grid[2]
    max_lng = grid[3]
    diff_lng_per_grid = (max_lng - min_lng)/25.0

    if not pkl:
        time_demand = {}
        with open('/Users/liuqianchao/Desktop/ra/od/May-Oct2016/San Diego May-Oct2016_match_nearest_cut.csv') as f:
            for index, line in enumerate(f):
                if index > 0:
                    if index %1000 ==0:
                        print index
                    seq_line = line.split(',')
                    cut_status = seq_line[0]
                    engine_type = seq_line[2]
                    time = seq_line[3]
                    lat = float(seq_line[4])
                    lng = float(seq_line[5])
                    fuel = seq_line[6]

                    # id
                    i = int((max_lat - lat)/diff_lat_per_grid)
                    j = int((lng - min_lng)/diff_lng_per_grid)
                    if i == 25:
                        i = 24
                    if j == 25:
                        j = 24
                    id = i*25 + j+1

                    key = time + '/' + str(id)
                    if key in time_demand.keys():
                        time_demand[key].append([cut_status, engine_type, fuel])
                    else:
                        time_demand[key] = [[cut_status, engine_type, fuel]]
        pickle.dump(time_demand, open('/Users/liuqianchao/Desktop/ra/od/May-Oct2016/time_demand_dict.pkl','w'))
    else:
        time_demand = pickle.load(open('/Users/liuqianchao/Desktop/ra/od/May-Oct2016/time_demand_dict.pkl','r'))


    keylist = time_demand.keys()
    timelist = [item.split('/')[0] for item in keylist]
    timelist = list(set(timelist))
    timelist.sort()
    time_next5time ={}
    for i, time in enumerate(timelist):
        time_next5time[time] = []
        for j in range(1,6):
            try:

                time_next5time[time] += [timelist[i+j]]
            except:
                # 最后五个time
                time_next5time[time] += [-1]

    print 'begin computing demand:'
    with open('/Users/liuqianchao/Desktop/ra/demand/x1.csv') as f:
        for index, line in enumerate(f):
            if index > 0:
                if index%10000 == 0:
                    print '{}%'.format(index/7057261.0)
                line = line.strip('\n')
                seq_line = line.split(',')
                time = seq_line[0]
                id = seq_line[1]

                x = seq_line

                post_time_list = [time+'/'+id]
                for i in range(0,5):
                    try:
                        # time_index = timelist.index(time)
                        post_time_list.append(time_next5time[time][i]+'/'+id)
                    except Exception,e:
                        post_time_list.append(-1)
                rst = []
                cut = []
                for current_index, time_id in enumerate(post_time_list):
                    ce_demand = []
                    ed_demand = []

                    try:
                        time_demand[time_id]
                    except Exception,e:
                        # no
                        ce_demand_num = 0
                        ed_demand_num = 0
                        ce_avg_fuel = 0
                        ed_avg_fuel = 0
                        ce_max_fuel = 0
                        ed_max_fuel = 0
                    else:
                        for demand in time_demand[time_id]:
                            cut_status = demand[0]

                            engine_type = demand[1]
                            # lat = float(demand[2])
                            # lng = float(demand[3])
                            fuel = float(demand[2])
                            # i = int((max_lat - lat)/diff_lat_per_grid)
                            # j = int((lng - min_lng)/diff_lng_per_grid)
                            # if i == 25:
                            #     i = 24
                            # if j == 25:
                            #     j = 24
                            # demand_id = i*25 + j+1

                            if engine_type == 'CE':
                                # CE
                                ce_demand.append(fuel)
                            elif engine_type == 'ED':
                                # ED
                                ed_demand.append(fuel)
                            else:
                                print 'error', engine_type
                        else:
                            # 最后一次迭代
                            if cut_status != '0':
                                if str(current_index+1) not in cut:
                                    cut.append(str(current_index+1))
                        ce_demand_num = len(ce_demand)
                        ed_demand_num = len(ed_demand)
                        if ce_demand_num!=0:
                            ce_avg_fuel = sum(ce_demand)/ce_demand_num
                            ce_max_fuel = max(ce_demand)
                        else:
                            ce_avg_fuel = 0
                            ce_max_fuel = 0
                        if ed_demand_num!=0:
                            ed_avg_fuel = sum(ed_demand)/ed_demand_num
                            ed_max_fuel = max(ed_demand)
                        else:
                            ed_avg_fuel = 0
                            ed_max_fuel = 0


                    rst.append([ce_demand_num, ce_avg_fuel, ce_max_fuel, ed_demand_num, ed_avg_fuel, ed_max_fuel])

                y = []
                for i, item in enumerate(rst):
                    ce_demand_num = item[0]
                    ce_avg_fuel = item[1]
                    ce_max_fuel = item[2]
                    ed_demand_num = item[3]
                    ed_avg_fuel = item[4]
                    ed_max_fuel = item[5]
                    for j in range(i):

                        if rst[j][0] != 0:
                            ce_avg_fuel = (ce_demand_num*ce_avg_fuel + rst[j][0]*rst[j][1])/(ce_demand_num+rst[j][0])

                        ce_demand_num += rst[j][0]
                        ce_max_fuel = max(ce_max_fuel, rst[j][2])


                        if rst[j][3] != 0:
                            ed_avg_fuel = (ed_demand_num*ed_avg_fuel + rst[j][3]*rst[j][4])/(ed_demand_num+rst[j][3])

                        ed_demand_num += rst[j][3]
                        ed_max_fuel = max(ed_max_fuel, rst[j][5])
                    y += [ce_demand_num, ce_avg_fuel, ce_max_fuel, ed_demand_num, ed_avg_fuel, ed_max_fuel]
                if cut == []:
                    cut = '0'
                else:
                    cut = '/'.join(cut)
                output.append(x + y + [cut])

    with open('/Users/liuqianchao/Desktop/ra/demand.csv','w') as wf:
        title = 'time,id,ce#,ce_avg_fuel,ce_max_fuel,ce_min_fuel,ed#,ed_avg_fuel,ed_max_fuel,ed_min_fuel,n8_ce#, ' \
                'n8_ce_avg_fuel,n8_ce_max_fuel,n8_ce_min_fuel,n8_ed#,n8_ed_avg_fuel,n8_ed_max_fuel,n8_ed_min_fuel,'
        seq = [-5,-10,-15,-20,-25,-30]
        for pre in seq:
            pre = str(pre)
            title += '{}ce#,{}ce_avg_fuel,{}ce_max_fuel,{}ce_min_fuel,{}ed#,{}ed_avg_fuel,{}ed_max_fuel,{}ed_min_fuel,'.format(pre,pre,pre,pre,pre,pre,pre,pre)
        seq = [5,10,15,20,25,30]
        for pre in seq:
            pre = str(pre)
            title += '{}ce_demand_num,{}ce_avg_fuel,{}ce_max_fuel,{}ed_demand_num,{}ed_avg_fuel,{}ed_max_fuel,'.format(pre,pre,pre,pre,pre,pre)
        title += 'cut_status'
        title += '\n'
        wf.write(title)
        for content in output:
            content = [str(item) for item in content]
            wf.write(','.join(content) + '\n')

def revise_format():
    output= []
    with open('/Users/liuqianchao/Desktop/ra/demand/demand.csv') as f:
        for i,line in enumerate(f):
            if i > 0:
                seq_line = line.split(',')
                time = seq_line[0]

                time = datetime.datetime.strptime(time, "%Y-%m-%d %H:%M:%S")

                day_of_year = (time - datetime.datetime.strptime('2016-01-01 0:0:0', "%Y-%m-%d %H:%M:%S")).days + 1
                minute_of_day = time.hour * 60 + time.minute + time.second/60.0
                output.append([seq_line[0]]+[str(day_of_year),str(minute_of_day)]+seq_line[1:])
                # line = line.strip('\n')
                #
                # print line.split(',')[:3]
                # # print line.split(',')[-1]

    with open('/Users/liuqianchao/Desktop/ra/demand/demand_revise.csv','w') as wf:
        title = 'time,day,min,id,ce#,ce_avg_fuel,ce_max_fuel,ce_min_fuel,ed#,ed_avg_fuel,ed_max_fuel,ed_min_fuel,n8_ce#, ' \
                'n8_ce_avg_fuel,n8_ce_max_fuel,n8_ce_min_fuel,n8_ed#,n8_ed_avg_fuel,n8_ed_max_fuel,n8_ed_min_fuel,'
        seq = [-5,-10,-15,-20,-25,-30]
        for pre in seq:
            pre = str(pre)
            title += '{}ce#,{}ce_avg_fuel,{}ce_max_fuel,{}ce_min_fuel,{}ed#,{}ed_avg_fuel,{}ed_max_fuel,{}ed_min_fuel,'.format(pre,pre,pre,pre,pre,pre,pre,pre)
        seq = [5,10,15,20,25,30]
        for pre in seq:
            pre = str(pre)
            title += '{}ce_demand_num,{}ce_avg_fuel,{}ce_max_fuel,{}ed_demand_num,{}ed_avg_fuel,{}ed_max_fuel,'.format(pre,pre,pre,pre,pre,pre)
        title += 'cut_status'
        title += '\n'
        wf.write(title)
        for item in output:
            wf.write(','.join(item))
# grid = grid_size()
grid = (32.69223, 32.88993, -117.2596, -117.00902)
# id_list = id(grid=grid)
id_list = [5, 8, 33, 202, 210, 212, 251, 252, 253, 276, 277, 278, 279, 301, 302, 303, 305, 306, 310, 326, 327, 328, 335, 340, 351, 352, 361, 363, 364, 365, 370, 375, 376, 377, 381, 382, 383, 384, 385, 386, 387, 388, 389, 390, 401, 402, 405, 406, 407, 408, 409, 410, 411, 412, 413, 414, 415, 416, 426, 427, 428, 429, 430, 431, 432, 433, 434, 435, 436, 437, 438, 439, 440, 441, 451, 452, 453, 455, 457, 458, 459, 460, 461, 462, 463, 464, 465, 476, 477, 478, 480, 483, 484, 485, 486, 487, 488, 489, 490, 502, 503, 505, 506, 507, 509, 510, 511, 512, 513, 514, 515, 528, 534, 535, 536, 537, 538, 539, 540, 546, 559, 560, 561, 562, 563, 564, 565, 567, 568, 585, 586, 587, 588, 589, 614]
#x(grid=grid, id_list=id_list)
grid = (32.69223, 32.88993, -117.2596, -117.00902)
y(grid, True)


#
# [0, 0, 0, 0, 28, 0, 0, 71, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
# [0, 0, 0, 0, 0, 0, 0, 60, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
# [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
# [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
# [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
# [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
# [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
# [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
# [0, 64, 0, 0, 0, 0, 0, 0, 0, 131, 0, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
# [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
# [83640, 33157, 112637, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
# [147568, 133253, 115446, 5534, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
# [93447, 58594, 89501, 0, 4045, 43313, 0, 0, 0, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
# [34839, 7502, 71962, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 448, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
# [37581, 17893, 0, 0, 0, 0, 0, 0, 0, 0, 107359, 0, 2967, 14926, 23527, 0, 0, 0, 0, 131346, 0, 0, 0, 0, 1]
# [48014, 31976, 0, 0, 0, 3920, 103960, 51706, 46839, 47938, 54047, 150910, 91022, 98330, 48297, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
# [13952, 4451, 0, 0, 3, 35879, 42860, 44697, 62758, 61868, 96613, 246000, 178886, 170841, 144576, 12265, 0, 0, 0, 0, 0, 0, 0, 0, 0]
# [32356, 211208, 57237, 2, 289, 49633, 214457, 80172, 175811, 272293, 135393, 203227, 234592, 112930, 117676, 48537, 0, 0, 0, 0, 0, 0, 0, 0, 0]
# [91099, 146326, 120144, 0, 5163, 0, 46690, 146456, 166371, 299918, 112140, 172976, 144864, 131563, 81804, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
# [25131, 69064, 15619, 0, 331811, 0, 0, 4214, 185418, 296337, 7906, 67732, 65243, 101706, 10881, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
# [0, 48747, 11, 0, 6, 78612, 21, 0, 118932, 457029, 46672, 30639, 78601, 72420, 18959, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
# [0, 0, 1, 0, 0, 0, 0, 0, 53204, 336820, 197130, 137161, 221575, 135823, 4988, 0, 0, 0, 0, 0, 139, 0, 0, 0, 0]
# [0, 0, 0, 0, 0, 0, 0, 0, 23066, 203468, 403612, 254871, 138160, 40537, 102, 0, 2, 559, 0, 0, 0, 0, 0, 0, 0]
# [0, 0, 0, 0, 0, 0, 0, 0, 0, 14395, 35904, 52000, 21407, 18800, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
# [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1553, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]