#TODO : Create a check to see if the .npy file already exists. If so this will throw an error

import os
import tifffile as tiff
import numpy as np


def tiff_to_memmap(path_to_tiff, path_for_memmap, channel, chunk_size, suffix = '.tif', data_type = 'float32') -> None:

    '''
    Automatic conversion from large tif datasets to .npy memmaped arrays that allow dynamic loading and chunking to avoid
    memory issues. GPT generated.
    '''

    os.makedirs(path_for_memmap, exist_ok=True) #ensure folder exists, create it if not

    # Initialize a variable to track total number of frames
    total_frames = 0
    frame_shape = None

    # First pass: Calculate total number of frames and the frame shape
    for tiff_filename in os.listdir(path_to_tiff):
        if tiff_filename.endswith(suffix):
            tiff_path = os.path.join(path_to_tiff, tiff_filename)
            with tiff.TiffFile(tiff_path) as tif:
                total_frames += len(tif.pages)  # Count total number of frames
                if frame_shape is None:
                    frame_shape = tif.pages[0].shape  # Get shape of the first frame

    # create the memmap file for the entire output, for the channel used
    npy_filename = channel + '.npy'
    npy_path = os.path.join(path_for_memmap, npy_filename)
    npy_memmap = np.memmap(npy_path, dtype=data_type, mode='w+', shape=(total_frames, *frame_shape))


    # Second pass: Load TIFF stacks in chunks and write to the .npy memmap file
    current_frame = 0  # Tracks the position in the memmap array

    for tiff_filename in os.listdir(path_to_tiff):
        if tiff_filename.endswith(suffix):
            tiff_path = os.path.join(path_to_tiff, tiff_filename)

            # Load and convert the TIFF stack in chunks
            with tiff.TiffFile(tiff_path) as tif:
                num_frames = len(tif.pages)

                for i in range(0, num_frames, chunk_size):
                    end_frame = min(i + chunk_size, num_frames) # this is clever, gpt

                    # Read only the current chunk from the TIFF file
                    try:
                        chunk = np.array([page.asarray() for page in tif.pages[i:end_frame]])
                    except:
                        print('Last frame issue: exluding final frame') # if the last frame is blank (which happens) this will crash to aquisition. So last frame is excluded in this case
                        chunk = np.array([page.asarray() for page in tif.pages[i:end_frame-1]])

                    # Write the chunk to the appropriate location in the memmap file
                    npy_memmap[current_frame:current_frame + chunk.shape[0]] = chunk.astype(data_type)  # Adjust dtype if necessary
                    current_frame += chunk.shape[0]  # Update the frame position

                    print(f"Processed frames {i} to {end_frame} from {tiff_filename}")
        print('\n')

    npy_memmap.flush() # ensure everything is written to disk



def create_memmap_multichannel(path_to_directory, chunk_size, numpy_folder_name='numpy', suffix = '.tif', data_type = 'float32'):

    '''
    create a .npy memmap file for each channel folder in a given directory. Creates a new numpy folder in the directory
    '''

    numpy_folder = os.path.join(path_to_directory, numpy_folder_name)

    folders = [name for name in os.listdir(path_to_directory) if os.path.isdir(os.path.join(path_to_directory, name))]

    for folder in folders:
        path_to_tiff = os.path.join(path_to_directory, folder)
        tiff_to_memmap(path_to_tiff, numpy_folder, channel=folder, chunk_size=chunk_size, suffix=suffix, data_type=data_type)

