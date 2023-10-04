import time
import math
import cv2
from pytesseract import pytesseract
from PIL import Image
import numpy as np
import datetime

parking_logs = []
vehicle_records = {}


def teseeract_ocr():
    # img_counter = 0
    frame_set = []
    start_time = time.time()

    camera = cv2.VideoCapture(0)

    path_to_tesseract = r"D:\Programs\Tesseract\tesseract.exe"
    pytesseract.tesseract_cmd = path_to_tesseract

    # limit what pytesseract can read

    while True:
        ret, frame = camera.read()
        new_frame = cv2.resize(frame, (640, 480))
        img = cv2.resize(frame, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gauss_gray = cv2.GaussianBlur(gray, (5, 5), 0)

        cv2.imshow("frame", new_frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            camera.release()
            cv2.destroyAllWindows()
            return
            break

        if (time.time() - start_time) >= 1:  # <---- Check if 1 sec passed
            img_name = "opencv_frame.png"
            cv2.imwrite(img_name, gauss_gray)

            text = pytesseract.image_to_string(
                Image.open(img_name),
                lang="eng",
                config="--psm 6 --oem 3 -c tessedit_char_whitelist=0123456ABEHMO",
            )
            # config="--psm 6 --oem 3 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
            ln = sorted(text.split("\n"), key=len)[-1]
            ln = ln.replace(" ", "")
            plate_number = ln[:-1]

            if len(plate_number) >= 9:
                if plate_number in vehicles_inside:
                    exit_vehicle(plate_number)
                else:
                    vehicle_type = int(
                        input(
                            "Enter the type of vehicle that entered with plate number "
                            + plate_number
                            + " :"
                        )
                    )
                    enter_vehicle(plate_number, vehicle_type, 1)
            start_time = time.time()


m = int(input("Enter the width of lot: "))
n = int(input("Enter the length of lot: "))

history = []

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

parking_logs.append("Parking lot created with " + str(n * m) + " spaces.")

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
        print("No lot available for vehicle with number : ", plate_number, "\n")
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

    entry_date_time = datetime.datetime.fromtimestamp(entry_time)

    vehicles_inside[plate_number] = [
        min_dist_point,
        entry_date_time,
        entry_date_time.strftime("%Y-%m-%d %H:%M:%S"),
    ]
    global n_vehicles
    n_vehicles += 1

    print_lot_mat()
    print(
        "Vehicle ",
        plate_number,
        " entered at time ",
        entry_date_time.strftime("%Y-%m-%d %H:%M:%S"),
        " at lot space ",
        min_dist_point,
        ".",
    )
    parking_logs.append(
        "Vehicle "
        + str(plate_number)
        + " entered at time "
        + entry_date_time.strftime("%Y-%m-%d %H:%M:%S")
        + " at lot space "
        + str(min_dist_point)
    )

    vehicle_records[plate_number] = [
        incoming_vehicle_type,
        entry_date_time,
        entry_point,
    ]
    print("TotaL vehicles inside:", n_vehicles)


def billing(plate_number, duration, lot):
    vehicle_type = full_lot_mat[lot[0]][lot[1]]

    hrs = duration / 360000
    min = math.ceil((duration % 360000) / 60)

    if vehicle_type == 1:
        return 20 * hrs + 1 * min
    elif vehicle_type == 2:
        return 50 * hrs + 2 * min
    elif vehicle_type == 3:
        return 120 * hrs + 3 * min
    elif vehicle_type == 4:
        return 150 * hrs + 4 * min
    elif vehicle_type == 5:
        return 200 * hrs + 10 * min


def exit_vehicle(plate_number):
    exit_time = time.time()

    if plate_number not in vehicles_inside:
        print("\nNo such vehicle parked here.")
        return

    lot = vehicles_inside[plate_number][0]
    entry_time = datetime.datetime.timestamp(vehicles_inside[plate_number][1])

    duration = exit_time - entry_time
    bill = 10 * billing(plate_number, duration, lot)

    duration = datetime.timedelta(seconds=duration)

    exit_date_time = datetime.datetime.fromtimestamp(exit_time).strftime(
        "%Y-%m-%d %H:%M:%S"
    )
    print(
        "\nVehicle with plate number ", plate_number, " exited at ", exit_date_time, "."
    )
    parking_logs.append(
        "Vehicle with plate number "
        + str(plate_number)
        + " exited at "
        + exit_date_time
        + "."
    )

    print("Duration of stay: ", duration, " seconds .")
    print("Total bill incurred : Rs.", bill, "\n")

    vehicle_records[plate_number].append(exit_date_time)
    vehicle_records[plate_number].append(str(duration))
    vehicle_records[plate_number].append(bill)
    vehicle_records[plate_number].append(lot)

    del vehicles_inside[plate_number]
    global n_vehicles
    n_vehicles -= 1

    curr_lot_mat[lot[0]][lot[1]] = full_lot_mat[lot[0]][lot[1]]

    print_lot_mat()


if __name__ == "__main__":
    print_lot_mat()

    teseeract_ocr()

    # To exit, show vehicle record, parking logs, or cotinue
    while True:
        print("1. Exit")
        print("2. Show vehicle record")
        print("3. Show parking logs")
        print("4. Resume Process")

        choice = int(input("Enter your choice: "))
        if choice == 1:
            break
        elif choice == 2:
            print("\nVehicle Records : \n")
            print(
                "Plate Number : [Vehicle Type, Entry Time, Entry Point, Exit Time, Duration, Bill, Parking Lot]"
            )
            for i, x in enumerate(vehicle_records):
                print(i + 1, " : ", x, " : ", vehicle_records[x])
            print("\nVehicles Inside : ", len(vehicles_inside), "\n")
        elif choice == 3:
            print("\nParking Logs : \n")
            for i, x in enumerate(parking_logs):
                print(i + 1, " : ", x)
        elif choice == 4:
            teseeract_ocr()
