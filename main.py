"""
===================
Canny edge detector
===================

The Canny filter is a multi-stage edge detector. It uses a filter based on the
derivative of a Gaussian in order to compute the intensity of the gradients.The
Gaussian reduces the effect of noise present in the image. Then, potential
edges are thinned down to 1-pixel curves by removing non-maximum pixels of the
gradient magnitude. Finally, edge pixels are kept or removed using hysteresis
thresholding on the gradient magnitude.

The Canny has three adjustable parameters: the width of the Gaussian (the
noisier the image, the greater the width), and the low and high threshold for
the hysteresis thresholding.
"""
import os
import tempfile
import shutil
from tracking import tracking, export_to_csv, get_frames
from background_subtraction import nd2_background_subtraction
import ui

# Create UI and handle errors
try:
    app = ui.create_UI()
except ValueError as e:
    print("An error occurred in the UI:", e)
    exit(1)

# Utilize inputs from UI
ROI = app.get_roi()
input_file_path = app.file_path
input_folder_path = app.folder_path.get()
canny_lower = app.canny_lower.get()
canny_upper = app.canny_upper.get()


# # Parameters for tracking function
spots = []  # spot in spots = (x,y,w,h)
output_path = "nd2_results/frame_"  # If overlay = true, save here

if input_folder_path:
    files = [os.path.join(input_folder_path, f) for f in os.listdir(input_folder_path)]
if input_file_path:
    files = input_file_path

for index, nd2_file in enumerate(files):
    print(f"Processing file {index + 1} of {len(files)} in brittanys files: {nd2_file}")
    # Get the filename from brittany's files
    file_name = os.path.basename(nd2_file[:-4])

    # Make temp folder for images
    temp_dir = tempfile.mkdtemp()
    print("Temporary directory created:", temp_dir)

    # Convert nd2 file to png files and store into a folder
    nd2_background_subtraction(nd2_file, temp_dir)  # save to temp

    # Load frames from temp
    frame_directory = temp_dir
    print(f'Getting frames from {frame_directory}')
    frames = get_frames(parent_dir=frame_directory)

    # Perform tracking
    print("Tracking")
    overlay_frames, object_final_position, active_id_trajectory = tracking(frames, output_path, ROI, spots, canny_upper,
                                                                           canny_lower, draw_ROI=False,
                                                                           save_overlay=False)
    print("Creating csv files")
    # Create csv file from tracking info
    csv_filename = f"results/{file_name}_results.csv"
    export_to_csv(object_final_position, csv_filename)
    print(f"{csv_filename} saved")

    # # Create csv file from tracking info
    # csv_filename = f"results/active_id_trajectory.csv"
    # export_to_csv(active_id_trajectory, csv_filename)
    # print(f"{csv_filename} saved")

    shutil.rmtree(temp_dir)
    print("Temporary directory deleted:", temp_dir)

# ffmpeg to video code
# ffmpeg -framerate 10 -i frame_%d.png tracking.mp4

# TODO: diagnose overcounting
# TODO: GPU acceleration :)
