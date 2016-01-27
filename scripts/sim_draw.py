
import matplotlib.image as mpimg
import re
import os

numeric_const_pattern = r"""
    [-+]? # optional sign
    (?:
        (?: \d* \. \d+ ) # .1 .12 .123 etc 9.1 etc 98.1 etc
        |
         (?: \d+ \.? ) # 1. 12. 123. etc 1 12 123 etc
    )
    # followed by optional exponent part if desired
    (?: [Ee] [+-]? \d+ ) ?
    """
rx = re.compile(numeric_const_pattern, re.VERBOSE)


class Vehicle(object):
    def __init__(self):
        self.position = list()
        self.passengers_id = list()
        self.requests_scheduled = list()
        self.travel_schedule_order = list()
        self.travel_schedule_time = list()


class Person(object):
    def __init__(self):
        self.id = -1
        self.origin = list()
        self.destination = list()
        self.station_origin = -1
        self.station_origin_pos = list()
        self.station_dest = -1
        self.station_dest_pos = list()
        self.time_request = -1
        self.time_pickup = -1
        self.time_dropoff = -1
        self.travel_time_optim = -1
        self.assigned = -1
        self.vehicle = -1
        self.prediction = -1


class Path(object):
    def __init__(self):
        self.planned = list()
        self.executed = list()


# TODO: THERE IS A PROBLEM WHEN IMPORTING CLOSE TO ZERO VALUES IN NOTATION 1.154E-15!!!

# import data trips
save_folder_number = 1453681465
save_folder = '../data-sim/data-' + str(save_folder_number) + '/'
if os.path.isdir(save_folder) is not True:
    save_folder = ''
    print "The script is launched within the data folder"

time_now = 0
time_step = 30
index_iter = 0
while time_now >- 1: # breaks when files end

    print "loading %d" % time_now
    figurename = save_folder + "sim/sim-%05d.jpg" % (index_iter)
    if os.path.exists(figurename) is not True:

        # Import data
        vehicles = list()
        requests = list()
        passengers = list()
        filename = save_folder + 'graphs/data-graphs-' + str(time_now) + '.txt'
        with open(filename,'r') as f:
            strLine = f.readline()

            # requests
            strLine = f.readline()
            elementList = rx.findall(strLine)
            for w in elementList:
                n_req = int(w)
            requests = []
            for i in range(0, n_req):
                strLine = f.readline()
                elementList = rx.findall(strLine)
                elementList = [float(x) for x in elementList]

                person = Person()

                person.id = i
                person.origin = [elementList[0], elementList[1]]
                person.destination = [elementList[2], elementList[3]]
                person.station_origin = elementList[4]
                person.station_origin_pos = [elementList[5], elementList[6]]
                person.station_dest = elementList[7]
                person.station_dest_pos = [elementList[8], elementList[9]]
                person.time_request = elementList[10]
                person.assigned = elementList[11]
                person.vehicle = elementList[12]
                person.prediction = elementList[13]

                requests.append(person)

            # vehicles
            strLine = f.readline()
            strLine = f.readline()
            elementList = rx.findall(strLine)
            for w in elementList:
                n_veh = int(w)
            for i in range(0, n_veh):

                strLine = f.readline()
                data_veh_aux = strLine.split('%')

                vehicle = Vehicle()
                data_aux = rx.findall(data_veh_aux[0])
                vehicle.position = [float(x) for x in data_aux]
                data_aux = rx.findall(data_veh_aux[1])
                vehicle.passengers_id = [int(x) for x in data_aux]
                data_aux = rx.findall(data_veh_aux[2])
                vehicle.requests_scheduled = [int(x) for x in data_aux]
                data_aux = rx.findall(data_veh_aux[3])
                vehicle.travel_schedule_order = [int(x) for x in data_aux]
                data_aux = rx.findall(data_veh_aux[4])
                vehicle.travel_schedule_time = [float(x) for x in data_aux]

                vehicles.append(vehicle)

            # passengers
            strLine = f.readline()
            strLine = f.readline()
            elementList = rx.findall(strLine)
            for w in elementList:
                n_pass_total = int(w)
            passengers = []
            for i in range(0, n_pass_total):
                strLine = f.readline()
                elementList = rx.findall(strLine)
                elementList = [float(x) for x in elementList]

                person = Person()

                person.id = elementList[0]
                person.origin = [elementList[1], elementList[2]]
                person.destination = [elementList[3], elementList[4]]
                person.station_origin = elementList[5]
                person.station_origin_pos = [elementList[6], elementList[7]]
                person.station_dest = elementList[8]
                person.station_dest_pos = [elementList[9], elementList[10]]
                person.time_request = elementList[11]
                person.time_pickup = elementList[12]
                person.time_dropoff = elementList[13]
                person.travel_time_optim = elementList[14]
                person.assigned = 1
                person.vehicle = elementList[15]

                passengers.append(person)

                if person.id == n_pass_total - 1:
                    break

            # performance
            strLine = f.readline()
            strLine = f.readline()
            strLine = f.readline()
            l = rx.findall(strLine)
            n_pickups = int(l[0])
            n_total_pickups = int(l[1])
            n_dropoffs = int(l[2])
            n_total_dropoffs = int(l[3])
            n_ignored = int(l[4])
            n_total_ignored = int(l[5])

            # R-V graph
            strLine = f.readline()
            strLine = f.readline()
            strLine = f.readline()
            RVgraph_RRedges = []
            strLine = f.readline()
            while len(re.findall("#", strLine)) == 0:
                elementList = rx.findall(strLine)
                elementList = [int(x) for x in elementList]
                size = len(elementList)
                for i in range(0,size/2):
                    RVgraph_RRedges.append([elementList[2*i], elementList[2*i+1]])
                strLine = f.readline()
            RVgraph_VRedges = []
            strLine = f.readline()
            while len(re.findall("#", strLine)) == 0:
                elementList = rx.findall(strLine)
                elementList = [int(x) for x in elementList]
                size = len(elementList)
                for i in range(0,size/2):
                    RVgraph_VRedges.append([elementList[2*i], elementList[2*i+1]])
                strLine = f.readline()

            # Trips
            elementList = rx.findall(strLine)
            for w in elementList:
                n_trips = int(w)
            trips = []
            for i in range(0, n_trips):
                strLine = f.readline()
                w_trip = strLine.split('%')
                aux_strLine = [];
                for j in range(0, len(w_trip)):
                    aux = rx.findall(w_trip[j])
                    aux = [int(x) for x in aux]
                    aux_strLine.append(aux)
                trips.append(aux_strLine)

        print "n_pickups = %d (%d), n_dropoffs = %d(%d), n_ignored = %d (%d)" \
                % (n_pickups, n_total_pickups, n_dropoffs, n_total_dropoffs,
                   n_ignored, n_total_ignored)

        # import data assignment
        filename = save_folder + 'assignment/data-assignment-' + str(time_now) + '.txt'
        with open(filename,'r') as f:
            strLine = f.readline()
            strLine = f.readline()
            elementList = rx.findall(strLine)
            n_links = int(elementList[0])
            links_assignment = []

            n_assign_float = 0;
            n_assign_all = 0;
            for l in range(0,n_links):
                strLine = f.readline()
                elementList = rx.findall(strLine)
                id_trip = int(elementList[0])
                id_veh = int(elementList[1])
                cost_link = float(elementList[2])

                assign_link = 0
                if float(elementList[3])>0.999:
                    assign_link = 1
                    n_assign_all += 1
                elif float(elementList[3]) > 0.001:
                    n_assign_float +=1

                links_assignment.append([id_trip,id_veh,cost_link,assign_link])

        n_assign_all += n_assign_float
        print "Number of links %d" % len(links_assignment)
        if n_assign_float>0:
            print "Non binary assignments = %d / %d!" % (n_assign_float, n_assign_all)

        # # Store the travel for each trip
        # travels_order = [];
        # travels = [];
        # travels_pickup = [];
        # link_id = 0
        # for t in range(0, n_trips):
        #   for i in range(2, len(trips[t])):
        #       travel_order = trips[t][i]
        #       travels_order.append(travel_order);

        #       link = links_assignment[link_id]
        #       if link[3] == 1:
        #           travel = []
        #           travel_pick = []
        #           vehicle = vehicles[link[1]]
        #           pos = [vehicle.position[0], vehicle.position[1], link[1]]
        #           n_passengers = len(vehicle.passengers_id)
        #           travel.append(pos)
        #           travel_pick.append(pos)
        #           for i_travel in travel_order:
        #               if i_travel < 0: # passenger/request drop-off
        #                   i_travel = abs(i_travel) - 1
        #                   if i_travel < n_passengers: # it was a passenger
        #                       id_pas = int(vehicle.passengers_id[i_travel])
        #                       pos = [passengers[id_pas][2], passengers[id_pas][3], id_pas]
        #                   else: # it was a request
        #                       id_req = trips[t][0][i_travel - n_passengers]
        #                       pos = [requests[id_req][2], requests[id_req][3], id_req]
        #               else: # request pick-up
        #                   i_travel = i_travel - 1
        #                   id_req = trips[t][0][i_travel - n_passengers]
        #                   pos = [requests[id_req][0], requests[id_req][1], id_req]
        #                   travel_pick.append(pos)
        #               travel.append(pos)
        #           travels.append(travel)
        #           travels_pickup.append(travel_pick)
        #       link_id += 1

        # # Store the travel for each vehicle
        # car_travels = [];
        # for i_veh in range(0, n_veh):
        #   vehicle = vehicles[i_veh]
        #   car_travel = []
        #   pos = [vehicle.position[0], vehicle.position[1], i_veh]
        #   n_passengers = len(vehicle.passengers_id)
        #   car_travel.append(pos)

        #   for i_travel in vehicle.travel_schedule_order:

        #       if i_travel < 0: # passenger/request drop-off
        #           i_travel = abs(i_travel) - 1
        #           if i_travel < n_passengers: # it was a passenger
        #               id_pas = vehicle.passengers_id[i_travel]
        #               pos = [passengers[id_pas][2], passengers[id_pas][3], id_pas]
        #           else: # it was a request
        #               id_req = vehicle.requests_scheduled[i_travel - n_passengers]
        #               pos = [requests[id_req][2], requests[id_req][3], id_req]
        #       else: # request pick-up
        #           i_travel = i_travel - 1
        #           id_req = vehicle.requests_scheduled[i_travel - n_passengers]
        #           pos = [requests[id_req][0], requests[id_req][1], id_req]
        #           travel_pick.append(pos)

        #       car_travel.append(pos)

        #   car_travels.append(car_travel)

        # import data paths
        filename = save_folder + 'paths/data-paths-' + str(time_now) + '.txt'
        vehicle_paths = list()
        with open(filename,'r') as f:
            strLine = f.readline()
            elementList = rx.findall(strLine)
            for w in elementList:
                n_veh = int(w)
            for i in range(0, n_veh):

                strLine = f.readline()
                data_paths_aux = strLine.split('%')

                path = Path()
                data_aux = rx.findall(data_paths_aux[0])
                data_aux = [float(x) for x in data_aux]
                for j in range(0, len(data_aux)/2):
                    path.executed.append([data_aux[2*j], data_aux[2*j + 1]])

                data_aux = rx.findall(data_paths_aux[1])
                data_aux = [float(x) for x in data_aux]
                for j in range(0, len(data_aux)/2):
                    path.planned.append([data_aux[2*j], data_aux[2*j + 1]])

                vehicle_paths.append(path)

        #-------------------------------------------------------
        # Plot figures
        #-------------------------------------------------------
        import matplotlib.pyplot as plt

        print ("Data imported - plotting " + str(time_now))

        veh_colors = ['g','b','y','orange','r'];
        trip_colors = ['darkviolet','saddlebrown','cyan','deepskyblue','green'];
        trip_line_format = ['k-','k:','k--','k.-'];

        # plot requests-vehicles at their start/current position

        fig1 = plt.figure(time_now)

        # Display assignment links vehicles - requests
        # for travel in travels_pickup:
        #   for i in range(1,len(travel)):
        #       p1 = travel[i - 1]
        #       p2 = travel[i]
        #       plt.plot([p1[1], p2[1]], [p1[0], p2[0]], 'k', linewidth = 1, alpha = 0.1)

        # Travel trip
        # for t in range(0, n_veh):
        #   for i in range(1,len(vehicle_paths[t].executed)):
        #       p1 = vehicle_paths[t].executed[i-1]
        #       p2 = vehicle_paths[t].executed[i]
        #       plt.plot([p1[1], p2[1]], [p1[0], p2[0]], c = "yellow", linewidth = 1, alpha = 0.05)

        #   for i in range(1,len(vehicle_paths[t].planned)):
        #       p1 = vehicle_paths[t].planned[i-1]
        #       p2 = vehicle_paths[t].planned[i]
        #       plt.plot([p1[1], p2[1]], [p1[0], p2[0]], c = "grey", linewidth = 1, alpha = 0.05)

        for w in requests:
            if w.assigned == 1 :
                plt.plot(w.origin[1], w.origin[0], 'k*', markersize = 3, alpha = 0.3)
            else:
                plt.plot(w.origin[1], w.origin[0], 'r*', markersize = 3, alpha = 0.3)

        for w in vehicles:
            num_pass = len(w.passengers_id)
            plt.plot(w.position[1], w.position[0], 'o', c = veh_colors[num_pass],
                    markersize = 3, alpha = 0.5)

        if len(RVgraph_RRedges) < 1:
            for w in RVgraph_RRedges:
                p1 = requests[w[0]].origin
                p2 = requests[w[1]].origin
                plt.plot([p1[0], p2[0]], [p1[1], p2[1]], 'r:')
            for w in RVgraph_VRedges:
                p1 = vehicles[w[0]].position
                p2 = requests[w[1]].origin
                plt.plot([p1[0], p2[0]], [p1[1], p2[1]], 'g:')

        # Display N vehicles on top
        n_vehicles_highlight = 2

        for t in range(0, min(n_vehicles_highlight, n_veh)):
            # # Travel trip
            # for i in range(1,len(car_travels[t])):
            #   p1 = car_travels[t][i - 1]
            #   p2 = car_travels[t][i]
            #   plt.plot([p1[1], p2[1]], [p1[0], p2[0]], c = trip_colors[t], linewidth = 2, alpha = 1)

            for i in range(1,len(vehicle_paths[t].executed)):
                p1 = vehicle_paths[t].executed[i-1]
                p2 = vehicle_paths[t].executed[i]
                plt.plot([p1[1], p2[1]], [p1[0], p2[0]], c = "yellow", linewidth = 2, alpha = 1)

            for i in range(1,len(vehicle_paths[t].planned)):
                p1 = vehicle_paths[t].planned[i-1]
                p2 = vehicle_paths[t].planned[i]
                plt.plot([p1[1], p2[1]], [p1[0], p2[0]], trip_colors[t], linewidth = 2, alpha = 1)

            # Requests
            for i in range(0,len(vehicles[t].requests_scheduled)):
                id_req = vehicles[t].requests_scheduled[i]
                p1 = requests[id_req].station_origin_pos
                plt.plot(p1[1], p1[0], 'k*', markersize = 7, alpha = 1)
                p2 = requests[id_req].station_dest_pos
                plt.plot(p2[1], p2[0], 'kv', markersize = 6, alpha = 1)

            # Passengers
            for id_pass in vehicles[t].passengers_id:
                for id_aux in range(0,len(passengers)):
                    if passengers[id_aux].id == id_pass:
                        p2 = passengers[id_aux].station_dest_pos
                        plt.plot(p2[1], p2[0], 'kv', markersize = 6, alpha = 1)

            # Position car
            num_pass = len(vehicles[t].passengers_id)
            plt.plot(vehicles[t].position[1], vehicles[t].position[0], 'o',
                 c = veh_colors[num_pass], markersize = 5, alpha = 1)

        # Make figure pretty
        m, s = divmod(time_now, 60)
        h, m = divmod(m, 60)

        plt.title('%d Req, %d Veh, t = %02d:%02d:%02d, pick = %d(%d), drop = %d(%d), ignore = %d(%d)' \
            % (n_req, n_veh, h, m, s, n_pickups, n_total_pickups,
                n_dropoffs, n_total_dropoffs, n_ignored, n_total_ignored))

        # image = mpimg.imread("../map/map-manhattan-1.png")
        # axis = [-73.993498, -73.957058, 40.752273, 40.766382] # manhattan
        # image = mpimg.imread(save_folder + "../../map/soho.png")
        # axis = [-74.01002602762065, -73.96044289997499, 40.7354687066417, 40.77202074228057] # soho
        image = mpimg.imread(save_folder + "../../map/manhattan-downtown.png")
        axis = [-74.01824376474143, -73.94812921425887, 40.73320343981938, 40.77082617894838] # downtown
        plt.imshow(image, zorder=0, extent=axis, alpha = 1)

        # plt.axis([103.6, 104.1, 1.2, 1.5])
        # plt.axis([-74.02, -73.91, 40.7, 40.875])
        plt.axis(axis)
        plt.axes().set_aspect('equal')
        plt.axes().get_xaxis().set_visible(False)
        plt.axes().get_yaxis().set_visible(False)

        # plt.draw()
        plt.savefig(figurename, dpi=200)

        plt.close()

    time_now += time_step
    index_iter += 1

# generate movie
# ffmpeg -f image2 -r 1 -i sim/sim-%05d.jpg -vcodec mpeg4 -y movie.mp4
