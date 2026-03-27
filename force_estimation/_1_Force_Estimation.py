import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../')

import cv2
import yaml
from shape_reconstruction import Sensor
from force_estimation import Estimator
from force_estimation import Visualizer

if __name__ == '__main__':
    shape_file = open("../shape_reconstruction/shape_config.yaml", 'r+', encoding='utf-8')
    shape_config = yaml.load(shape_file, Loader=yaml.FullLoader)
    sensor = Sensor(shape_config)

    force_file = open("force_config.yaml", 'r+', encoding='utf-8')
    force_config = yaml.load(force_file, Loader=yaml.FullLoader)
    estimator = Estimator(force_config)
    visualizer = Visualizer()

    print("Press 'q' to quit. Press 'g' to toggle standalone gel flow view.")
    show_gel_only = True

    while sensor.cap.isOpened():
        image = sensor.get_rectify_crop_image()
        img_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        representation, mixed_visualization = sensor.raw_image_2_representation(img_gray)
        # mixed_visualization is the red/green gel-flow style view used in ROS demos.
        cv2.imshow('Raw Image', image)
        cv2.imshow('Deformation Representation', representation)
        cv2.imshow('Gel Flow (mixed_visualization)', mixed_visualization)

        if show_gel_only:
            gel_flow = sensor.visualize_gel_deformation(image)
            cv2.imshow('Gel Flow (standalone)', gel_flow)
        else:
            cv2.destroyWindow('Gel Flow (standalone)')

        force = estimator.predict_force(representation)

        key = cv2.waitKey(1)
        if key == ord('q'):
            break
        if key == ord('g'):
            show_gel_only = not show_gel_only

        if not visualizer.vis.poll_events():
            break
        visualizer.update_force(force)

    cv2.destroyAllWindows()
