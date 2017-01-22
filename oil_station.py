# encoding=utf-8
'''
data 20170120
'''
import math
import matplotlib.pyplot as plt

# 返回两个地理点的直线距离
def lat_lng_distance(lat_1,lng_1,lat_2,lng_2):
    R = 6371
    lat1 = (math.pi/180)*float(lat_1)
    lat2 = (math.pi/180)*float(lat_2)
    lng1 = (math.pi/180)*float(lng_1)
    lng2 = (math.pi/180)*float(lng_2)
    return 1000.0*math.acos(math.sin(lat1)*math.sin(lat2)+math.cos(lat1)*math.cos(lat2)*math.cos(lng1-lng2))*R



# 使用trip.csv文件 识别加油点 4188次记录
def gas_station():
    lat_lng_list = []

    with open('/Users/liuqianchao/Desktop/ra/demand/trip.csv','r') as f:
        for i, line in enumerate(f):

            if i > 0:
                line = line.strip('\n')
                seq_line = line.split(',')

                origin_fule = seq_line[8]
                origin_lat = seq_line[6]
                origin_lng = seq_line[7]
                destination_fule = seq_line[17]
                destination_lat = float(seq_line[15])
                destination_lng = float(seq_line[16])


                if destination_fule == '100.0' and origin_fule=='100.0':
                    lat_lng_list.append([destination_lat, destination_lng])
                    #print str([destination_lat, destination_lng])

    max_lat = max([lat_lng[0] for lat_lng in lat_lng_list])
    min_lng = min([lat_lng[1] for lat_lng in lat_lng_list])


    min_lat = min([lat_lng[0] for lat_lng in lat_lng_list])
    max_lng = max([lat_lng[1] for lat_lng in lat_lng_list])


    diff_lat_lng_per_grid = 100.0/111000
    #212*125




    result = {}
    for lat_lng in lat_lng_list:
        lat = lat_lng[0]
        lng = lat_lng[1]
        i = int((max_lat - lat)/diff_lat_lng_per_grid)
        j = int((lng - min_lng)/diff_lat_lng_per_grid)
        key = str(i)+','+str(j)
        if key not in result.keys():
            result[key] = [[lat,lng]]
        else:
            result[key].append([lat,lng])

    to_aggregae = []
    for key in result.keys():
        # print '{},{}],'.format(str(result[key][0])[:-1], len(result[key]))
        refuel_cnt = len(result[key])
        if refuel_cnt > 30:
            lats = [lat_lng[0] for lat_lng in result[key]]
            lngs = [lat_lng[1] for lat_lng in result[key]]
            to_aggregae.append([sum(lats)/len(lats), sum(lngs)/len(lngs), refuel_cnt])

    refuel_location=[]
    for i in range(len(to_aggregae)):
        mark = 1
        lat1 = to_aggregae[i][0]
        lng1 = to_aggregae[i][1]
        refuel_cnt1 = to_aggregae[i][2]
        for j in range(i+1, len(to_aggregae)):
            lat2 = to_aggregae[j][0]
            lng2 = to_aggregae[j][1]
            refuel_cnt2 = to_aggregae[j][2]
            if lat_lng_distance(lat1, lng1, lat2, lng2) < 50.0:
                #print (lat1 + lat2)/2.0, (lng1 + lng2)/2.0
                refuel_location.append([(lat1 + lat2)/2.0, (lng1 + lng2)/2.0, refuel_cnt1+refuel_cnt2])
                mark = 0
        if mark == 1:
            #print lat1, lng1
            refuel_location.append([lat1, lng1, refuel_cnt1])

    return refuel_location


#
# lats = [lat_lng[0] for lat_lng in refuel_location]
# lngs = [lat_lng[1] for lat_lng in refuel_location]
# plt.scatter(lats, lngs)
# plt.show()
#
#
#



#
# dist = []
# for i in range(len(refuel_location)):
#     for j in range(i+1, len(refuel_location)):
#         dist.append(lat_lng_distance(refuel_location[i][0], refuel_location[i][1], refuel_location[j][0], refuel_location[j][1]))
# dist.sort(reverse=True)
# for item in dist:
#     pass
#     print item


# 存储 refuel location 信息: refuel location ID, lat, lng, Region ID, refueling frequency
def write_gas_station_info(grid, gas_station_list):
    min_lat = grid[0]
    max_lat = grid[1]
    diff_lat_per_grid = (max_lat - min_lat)/25.0
    min_lng = grid[2]
    max_lng = grid[3]
    diff_lng_per_grid = (max_lng - min_lng)/25.0


    fuel_station_info = []
    refuel_station_id = 0
    for gas_station in gas_station_list:
        refuel_station_id += 1
        lat = gas_station[0]
        lng = gas_station[1]
        freq = gas_station[2]

        i = int((max_lat - lat)/diff_lat_per_grid)
        j = int((lng - min_lng)/diff_lng_per_grid)
        if i == 25:
            i = 24
        if j == 25:
            j = 24
        id = i*25 + j+1
        fuel_station_info.append([refuel_station_id, lat, lng, id, freq])

    with open('/Users/liuqianchao/Desktop/ra/fuelstation/gastation.csv','w') as wf:
        wf.write('refuel_station_id,lat,lng,region_id,freq\n')
        for info in fuel_station_info:
            info = [str(item) for item in info]
            wf.write(','.join(info)+'\n')
    return fuel_station_info


def revise_trip(grid):
    min_lat = grid[0]
    max_lat = grid[1]
    diff_lat_per_grid = (max_lat - min_lat)/25.0
    min_lng = grid[2]
    max_lng = grid[3]
    diff_lng_per_grid = (max_lng - min_lng)/25.0

    fuel_station_info = []
    # 读入 gas station 文件
    with open('/Users/liuqianchao/Desktop/ra/fuelstation/gastation.csv') as f:
        for i, line in enumerate(f):
            if i > 0:
                line = line.strip('\n')
                fuel_station_info.append(line.split(','))

    # 读入 demand 文件:
    demand_dict = {}
    with open('/Users/liuqianchao/Desktop/ra/demand/demand.csv') as f:
        for i,line in enumerate(f):
            if i>0:
                line = line.strip('\n')
                line_seq = line.split(',')
                day = line_seq[1]
                min = line_seq[2]
                id = line_seq[3]
                ce = line_seq[4]
                ed = line_seq[8]
                n8_ce = line_seq[12]
                n8_ed = line_seq[16]

                key = '{}/{}/{}'.format(day, min, id)
                demand_dict[key] = [ce, ed, n8_ce, n8_ed]

    to_write = []
    # 给 trip 文件 每一辆车加上 region id, 以及对于trip 的起点 加上 current grid and n8 grid 可供使用的汽车的数量,以及 refuel location ID for each vehicle(<100)
    with open('/Users/liuqianchao/Desktop/ra/demand/trip.csv') as f:
        for i,line in enumerate(f):
            if i == 0:
                titles = line.strip('\n')
                titles = titles.split(',')
                titles[3] = 'region_id'
                to_write_titles = titles[:4] + ['refuel_id'] + titles[4:6] + ['ce', 'ed', 'n8_ce', 'n8_ed'] + \
                                  titles[6:17]
                for times in range(16):
                    to_write_titles += ['region_id', 'refuel_id']
                    to_write_titles += titles[17+times*11: 28+times*11]

                to_write.append(to_write_titles)
            if i > 0:
                line = line.strip('\n')
                line_seq = line.split(',')

                day_of_year = line_seq[4]
                minute_of_day = line_seq[5]
                origin_lat = float(line_seq[6])
                origin_lng = float(line_seq[7])

                origin_region_id = line_seq[3]

                key = '{}/{}/{}'.format(day_of_year, minute_of_day, origin_region_id)

                try:
                    origin_available = demand_dict[key]
                except Exception, e:
                    pass


                to_add_id = []

                # origin refuel station id
                refuel_location_id_distance = []
                for info in fuel_station_info:
                    id_fuel_station = info[0]
                    lat_fuel_station = float(info[1])
                    lng_fuel_station = float(info[2])
                    dist = lat_lng_distance(origin_lat, origin_lng, lat_fuel_station, lng_fuel_station)
                    refuel_location_id_distance.append([id_fuel_station, dist])
                refuel_location_id_distance.sort(key=lambda x: x[1])
                if refuel_location_id_distance[0][1]<100.0:
                    refuel_id = refuel_location_id_distance[0][0]
                else:
                    refuel_id = '0'


                to_add_id.append(refuel_id)

                for times in range(16):
                    lat = float(line_seq[15+times*11])
                    lng = float(line_seq[16+times*11])
                    refuel_location_id_distance = []
                    for info in fuel_station_info:
                        id_fuel_station = info[0]
                        lat_fuel_station = float(info[1])
                        lng_fuel_station = float(info[2])
                        dist = lat_lng_distance(lat, lng, lat_fuel_station, lng_fuel_station)
                        refuel_location_id_distance.append([id_fuel_station, dist])
                    refuel_location_id_distance.sort(key=lambda x: x[1])
                    if refuel_location_id_distance[0][1]<100.0:
                        refuel_id = refuel_location_id_distance[0][0]
                    else:
                        refuel_id = '0'

                    i = int((max_lat - lat)/diff_lat_per_grid)
                    j = int((lng - min_lng)/diff_lng_per_grid)
                    if i == 25:
                        i = 24
                    if j == 25:
                        j = 24
                    region_id = i*25 + j+1
                    to_add_id += [region_id, refuel_id]

                to_write_line = line_seq[:4] + [to_add_id[0]] + line_seq[4:6] + origin_available + \
                                line_seq[6:17]

                for times in range(16):
                    to_write_line += [to_add_id[1+i], to_add_id[2+i]]
                    to_write_line += line_seq[17+times*11: 28+times*11]

                to_write.append(to_write_line)
    with open('/Users/liuqianchao/Desktop/ra/fuelstation/trip_added_info','w') as wf:
        for content in to_write:
            content = [str(item) for item in content]
            wf.write(','.join(content)+'\n')

#gas_station_list = gas_station()
grid = (32.69223, 32.88993, -117.2596, -117.00902)
#fuel_station_info = write_gas_station_info(grid, gas_station_list)


revise_trip(grid)