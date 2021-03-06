import logging
import math
import time

import cv2
import numpy as np


CAR_COLORS = [
    (0, 0, 255),
    (0, 106, 255),
    (0, 216, 255),
    (0, 255, 182),
    (0, 255, 76),
    (144, 255, 0),
    (255, 255, 0),
    (255, 148, 0),
    (255, 0, 178),
    (255, 0, 255),
]


class Vehicle(object):

    def __init__(self, id, position):
        self.id = id
        self.positions = [position]
        self.frames_since_seen = 0
        self.counted = False

    @property
    def last_position(self):
        return self.positions[-1]

    def add_position(self, new_position):
        self.positions.append(new_position)
        self.frames_since_seen = 0

    def draw(self, output_image):
        car_color = CAR_COLORS[self.id % len(CAR_COLORS)]
        if len(self.positions) > 10:
            for point in self.positions:
                cv2.circle(output_image, point, 2, car_color, -1)
                cv2.polylines(
                    output_image,
                    [np.int32(self.positions)],
                    False,
                    car_color,
                    1
                )


class VehicleCounter(object):

    def __init__(self, shape, divider):
        self.log = logging.getLogger('vehicle_counter')

        self.height, self.width = shape
        self.divider = divider

        self.vehicles = []
        self.next_vehicle_id = 0
        self.vehicle_count = 0
        self.max_unseen_frames = 7
        self.start_time = time.time()
        self.goci_samples = []

    @staticmethod
    def get_vector(a, b):
        """
        Calculates vector (distance, angle in degrees) from a to b

        Angle ranges from -180 to 180 degrees
        Vector with angle 0 points straight down on the image
        Values increase in clockwise direction
        """
        dx = float(b[0] - a[0])
        dy = float(b[1] - a[1])

        distance = math.sqrt(dx**2 + dy**2)

        if dy > 0:
            angle = math.degrees(math.atan(-dx / dy))
        elif dy == 0:
            if dx < 0:
                angle = 90.0
            elif dx > 0:
                angle = -90.0
            else:
                angle = 0.0
        else:
            if dx < 0:
                angle = 180 - math.degrees(math.atan(dx / dy))
            elif dx > 0:
                angle = -180 - math.degrees(math.atan(dx / dy))
            else:
                angle = 180.0

        return distance, angle

    @staticmethod
    def is_valid_vector(a):
        distance, angle = a
        threshold_distance = max(15.0, -0.008 * angle**2 + 0.4 * angle + 25.0)
        return distance <= threshold_distance

    def update_vehicle(self, vehicle, matches):
        # Find if any of the matches fits this vehicle
        for i, match in enumerate(matches):
            contour, centroid = match
            vector = self.get_vector(vehicle.last_position, centroid)

            if self.is_valid_vector(vector):
                vehicle.add_position(centroid)
                self.log.debug(
                    'Added match (%d, %d) to vehicle #%d. vector=%0.2f,%0.2f',
                    centroid[0], centroid[1], vehicle.id, vector[0], vector[1]
                )
                return i

        # No matches
        vehicle.frames_since_seen += 1
        self.log.debug(
            'No match for vehicle #%d. frames_since_seen=%d',
            vehicle.id,
            vehicle.frames_since_seen
        )
        return None

    def update_count(self, matches, output_image=None):
        self.log.debug('Updating count using %d matches', len(matches))

        for vehicle in self.vehicles:
            i = self.update_vehicle(vehicle, matches)
            if i is not None:
                del matches[i]

        for match in matches:
            contour, centroid = match
            new_vehicle = Vehicle(self.next_vehicle_id, centroid)
            self.next_vehicle_id += 1
            self.vehicles.append(new_vehicle)
            self.log.debug(
                'Created new vehicle #%d from match (%d, %d)',
                new_vehicle.id,
                centroid[0],
                centroid[1]
            )

        current_goci = self.vehicle_count / (time.time() - self.start_time)

        for vehicle in self.vehicles:
            if not vehicle.counted\
               and vehicle.last_position[1] > self.divider\
               and len(vehicle.positions) > 10:
                self.vehicle_count += 1
                self.goci_samples.append(current_goci)
                vehicle.counted = True
                self.log.debug(
                    'Counted vehicle #%d (total count %d)',
                    vehicle.id, self.vehicle_count
                )

        if output_image is not None:
            for vehicle in self.vehicles:
                vehicle.draw(output_image)

            cv2.putText(
                output_image,
                ('%02d Tracked' % self.vehicle_count),
                (72, 24),
                cv2.FONT_HERSHEY_DUPLEX,
                1.0,
                (128, 255, 255),
                1
            )

            avg_goci = sum(self.goci_samples) / len(self.goci_samples)\
                if len(self.goci_samples) else 0

            cv2.putText(
                output_image,
                ('GOCI: %0.2f  Avg: %0.2f' % (current_goci, avg_goci)),
                (72, 48),
                cv2.FONT_HERSHEY_COMPLEX_SMALL,
                1.0,
                (128, 255, 255),
                1
            )

        removed = [v.id for v in self.vehicles
                   if v.frames_since_seen >= self.max_unseen_frames]
        self.vehicles[:] = [v for v in self.vehicles if not
                            v.frames_since_seen >= self.max_unseen_frames]
        for id in removed:
            self.log.debug('Removed vehicle #%d', id)
        self.log.debug(
            'Count updated, tracking %d vehicles',
            len(self.vehicles)
        )
