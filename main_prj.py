import time
import math

m = int(input("Enter the width of lot: "))
n = int(input("Enter the length of lot: "))

lot_matrix = [[-1 for x in range(m)] for y in range(n)]

print("Types of vehicles allowed with id.")
print("Parked : -1")
print("No parking : 0")
print("Bikes and Cycles : 1")
print("Mini Cars : 2")
print("Prime Sedan : 3")
print("Prime SUV : 4")
print("Prime Luxury : 5")

print("\nEnter types of vehicles allowed in lot spaces: ")

type_lots = {1: [], 2: [], 3: [], 4: [], 5: []}

for i in range(n):
    for j in range(m):
        print("Lot ", i + 1, "-", j + 1, ": ", end="")
        lot_matrix[i][j] = int(input())

    print()


vehicles_inside = {}

n_vehicles = len(vehicles_inside)

mm = m + 2
nn = n + int(n / 2) + 1
full_lot_mat = [[0 for x in range(mm)] for y in range(nn)]
entry_points = {1: [0, 0], 2: [nn - 1, mm - 1]}

cr = 0
for i in range(nn):
    if i % 3 == 0:
        cr += 1
    for j in range(mm):
        if i % 3 == 0 or j == 0 or j == mm - 1:
            full_lot_mat[i][j] = 0
        else:
            full_lot_mat[i][j] = lot_matrix[i - cr][j - 1]

        if full_lot_mat[i][j] != 0:
            type_lots[full_lot_mat[i][j]].append([i, j])


curr_lot_mat = [[0 for x in range(mm)] for y in range(nn)]
for i in range(nn):
    for j in range(mm):
        curr_lot_mat[i][j] = full_lot_mat[i][j]


for x in vehicles_inside:
    curr_lot_mat[vehicles_inside[x][0]][vehicles_inside[x][1]] = -1


def print_lot_mat():
    for i in range(nn):
        for j in range(mm):
            print(curr_lot_mat[i][j], end=" ")
        print()


def enter_vehicle(plate_number, incoming_vehicle_type, entry_point):
    print("\n")
    print(
        "Vehicle of type ",
        incoming_vehicle_type,
        " with plate number ",
        plate_number,
        " tried to look for a lot.",
    )
    entry_time = time.time()

    start_point = entry_points[entry_point]

    # Find nearest lot with value >= incoming_vehicle_type and not -1 using Dijkstra's algorithm and print path

    def find_path():
        visited = [[False for x in range(mm)] for y in range(nn)]
        dist = [[float("inf") for x in range(mm)] for y in range(nn)]
        dist[start_point[0]][start_point[1]] = 0

        # for storing path
        parent = [[None for x in range(mm)] for y in range(nn)]

        def min_dist():
            min_dist = float("inf")
            min_dist_point = None
            for i in range(nn):
                for j in range(mm):
                    if dist[i][j] < min_dist and not visited[i][j]:
                        min_dist = dist[i][j]
                        min_dist_point = [i, j]

            return min_dist_point

        def find_neighbours(point):
            neighbours = []
            if point[0] - 1 >= 0:
                neighbours.append([point[0] - 1, point[1]])
            if point[0] + 1 < nn:
                neighbours.append([point[0] + 1, point[1]])
            if point[1] - 1 >= 0:
                neighbours.append([point[0], point[1] - 1])
            if point[1] + 1 < mm:
                neighbours.append([point[0], point[1] + 1])

            return neighbours

        def relax(point, neighbour):
            if (
                curr_lot_mat[neighbour[0]][neighbour[1]] == 0
                or curr_lot_mat[neighbour[0]][neighbour[1]] >= incoming_vehicle_type
            ):
                if dist[neighbour[0]][neighbour[1]] > dist[point[0]][point[1]] + 1:
                    dist[neighbour[0]][neighbour[1]] = dist[point[0]][point[1]] + 1
                    parent[neighbour[0]][neighbour[1]] = point

        while True:
            point = min_dist()
            if point == None:
                break

            visited[point[0]][point[1]] = True

            for neighbour in find_neighbours(point):
                if not visited[neighbour[0]][neighbour[1]]:
                    relax(point, neighbour)

        return dist, parent

    dist, parent = find_path()

    min_dist = float("inf")
    min_dist_point = None

    for i in range(nn):
        for j in range(mm):
            if curr_lot_mat[i][j] >= incoming_vehicle_type:
                if dist[i][j] < min_dist:
                    min_dist = dist[i][j]
                    min_dist_point = [i, j]

    if min_dist_point == None:
        print("No lot available for vehicle type : ", incoming_vehicle_type, "\n")
        return

    path = []
    point = min_dist_point
    while point != None:
        path.append(point)
        point = parent[point[0]][point[1]]

    path.reverse()

    print("Distance to nearest lot: ", min_dist, " units")
    print("Path to nearest lot: ")
    for point in path:
        print(point, end="")
        if point != path[-1]:
            print("->", end="")
        else:
            print()

    # Update curr_lot_mat
    curr_lot_mat[min_dist_point[0]][min_dist_point[1]] = -1

    vehicles_inside[plate_number] = [min_dist_point, entry_time]
    global n_vehicles
    n_vehicles += 1

    print_lot_mat()
    print(
        "Vehicle ",
        plate_number,
        " entered at time ",
        entry_time,
        " at lot ",
        min_dist_point,
        ".",
    )
    print("TotaL vehicles inside:", n_vehicles)


def billing(plate_number, duration, lot):
    vehicle_type = full_lot_mat[lot[0]][lot[1]]

    hrs = duration / 3600
    min = math.ceil((duration % 3600) / 60)

    if vehicle_type == 1:
        return 50 * hrs + 1 * min
    elif vehicle_type == 2:
        return 100 * hrs + 2 * min
    elif vehicle_type == 3:
        return 150 * hrs + 3 * min
    elif vehicle_type == 4:
        return 250 * hrs + 4 * min
    elif vehicle_type == 5:
        return 1000 * hrs + 100 * min


def exit_vehicle(plate_number):
    exit_time = time.time()

    if plate_number not in vehicles_inside:
        print("\nNo such vehicle parked here.")
        return

    lot = vehicles_inside[plate_number][0]
    entry_time = vehicles_inside[plate_number][1]

    duration = exit_time - entry_time
    print("Vehicle ", plate_number, " exited at ", exit_time, ".")

    print("Duration of stay: ", duration, " seconds.")
    print("Total bill incurred : Rs.", 100 * billing(plate_number, duration, lot), "\n")

    del vehicles_inside[plate_number]
    global n_vehicles
    n_vehicles -= 1

    curr_lot_mat[lot[0]][lot[1]] = full_lot_mat[lot[0]][lot[1]]

    print_lot_mat()


if __name__ == "__main__":
    print_lot_mat()
    enter_vehicle("KA 01 AB 1234", 2, 2)
    enter_vehicle("KA 01 AB 1235", 3, 1)
    enter_vehicle("KA 01 AB 1236", 4, 2)
    enter_vehicle("KA 01 AB 1237", 5, 2)

    exit_vehicle("KA 01 AB 1234")
    enter_vehicle("KA 01 AB 1238", 1, 1)
    exit_vehicle("KA 01 AB 1235")
    exit_vehicle("KA 01 AB 1236")
    exit_vehicle("KA 01 AB 1237")
    exit_vehicle("KA 01 AB 1238")
