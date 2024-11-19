#TODO : Create a check to see if the .npy file already exists. If so this will throw an error!

import os
import tifffile as tiff
import numpy as np
import json


def tiff_to_memmap(path_to_tiff, path_for_memmap, channel, chunk_size, suffix = '.tif', data_type = 'uint16'
                   , collect_image_statistics = False) -> None:

    '''
    Automatic conversion from large tif datasets to .npy memmapped arrays that allow dynamic loading and chunking to avoid
    memory issues.
    '''

    os.makedirs(path_for_memmap, exist_ok=True) #ensure folder exists, create it if not

    # Initialize a variable to track total number of frames
    total_frames = 0
    frame_shape = None
    original_image_metadata = None # this is the metadata directly read from the original tif stack. Contains imaging parameters

    # First pass: Calculate total number of frames and the frame shape
    for tiff_filename in os.listdir(path_to_tiff):
        if tiff_filename.endswith(suffix):
            tiff_path = os.path.join(path_to_tiff, tiff_filename)
            with tiff.TiffFile(tiff_path) as tif:
                total_frames += len(tif.pages)  # Count total number of frames
                if frame_shape is None:
                    frame_shape = tif.pages[0].shape  # Get shape of the first frame
                if original_image_metadata is None:
                    original_image_metadata = {tag.name : tag.value for tag in tif.pages[0].tags} # get metadata from first frame


    # create the memmap file for the entire output, for the channel used
    npy_filename = channel + '.npy' #saving as .npy means the metadata will be contained in the file - can load without specifying later
    npy_path = os.path.join(path_for_memmap, npy_filename)
    if os.path.exists(npy_path):
        raise FileExistsError('.npy file already exists, remove the file or use a new name')

    try:
        npy_memmap = np.memmap(npy_path, dtype=data_type, mode='w+', shape=(total_frames, *frame_shape))
    except Exception as e:
        print('Failed to create memmap file, is there already a .npy file of the same name in this folder \n')
        print(e) 

    # Second pass: Load TIFF stacks in chunks and write to the .npy memmap file
    current_frame = 0  # Tracks the position in the memmap array
    image_statistics = None

    for tiff_filename in os.listdir(path_to_tiff):
        if tiff_filename.endswith(suffix):
            tiff_path = os.path.join(path_to_tiff, tiff_filename)

            # Load and convert the TIFF stack in chunks
            with tiff.TiffFile(tiff_path) as tif:
                num_frames = len(tif.pages)

                for i in range(0, num_frames, chunk_size):
                    end_frame = min(i + chunk_size, num_frames)

                    # Read only the current chunk from the TIFF file
                    try:
                        chunk = np.array([page.asarray() for page in tif.pages[i:end_frame]])
                    except:
                        print('Last frame issue: excluding final frame') # if the last frame is blank (which happens) this will crash to acquisition. So last frame is excluded in this case
                        chunk = np.array([page.asarray() for page in tif.pages[i:end_frame-1]])

                    # Write the chunk to the appropriate location in the memmap file
                    npy_memmap[current_frame:current_frame + chunk.shape[0]] = chunk.astype(data_type)  # Adjust dtype if necessary
                    current_frame += chunk.shape[0]  # Update the frame position


                    # NOTE: When averaging averages, a weighted sum of averages must be used (weighted by chunk size). Since these chunks are mostly the same size I'm ignoring this
                    if collect_image_statistics:
                        if image_statistics == None:
                            image_statistics = {'mean' : chunk.mean(), 'min' : chunk.min(), 'max' : chunk.max(), 'bottom_quantile' : np.quantile(chunk, 0.005), 'top_quantile' : np.quantile(chunk, 0.999)}
                        else:
                            image_statistics['mean'] = np.mean( (chunk.mean() , image_statistics['mean']) ).item() # JSON can't store numpy type (such as int16) These need converted to the nearest python standard type
                            image_statistics['min'] = np.min( (chunk.min() , image_statistics['min']) ).item()
                            image_statistics['max'] = np.max( (chunk.max() , image_statistics['max']) ).item()
                            image_statistics['bottom_quantile'] = np.mean( (np.quantile(chunk, 0.005) , image_statistics['bottom_quantile']) ).item()
                            image_statistics['top_quantile'] = np.mean( (np.quantile(chunk, 0.999) , image_statistics['top_quantile']) ).item()
                                                                                                          

                    print(f"Processed frames {i} to {end_frame} from {tiff_filename}")
        print('\n')

    npy_memmap.flush() # ensure everything is written to disk

    #save metadata for future loading
    # metadata = {'data_type' : data_type, 'shape' : (total_frames, *frame_shape)
    #             , 'original_image_metadata' : original_image_metadata, 'image_statistics' : image_statistics}
    metadata = {'data_type' : data_type, 'shape' : (total_frames, *frame_shape)
                , 'image_statistics' : image_statistics}
    metadata_filename = channel + '_meta' + '.json'
    metadata_path = os.path.join(path_for_memmap, metadata_filename)
    with open(metadata_path, 'w') as f: 
        json.dump(metadata, f)



def create_memmap_multichannel(path_to_directory, chunk_size, numpy_folder_name='numpy', suffix = '.tif', data_type = 'float32', collect_image_metadata = False):

    '''
    create a .npy memmap file for each channel folder in a given directory. Creates a new numpy folder in the directory
    '''

    numpy_folder = os.path.join(path_to_directory, numpy_folder_name)

    folders = [name for name in os.listdir(path_to_directory) if os.path.isdir(os.path.join(path_to_directory, name))]

    for folder in folders:
        path_to_tiff = os.path.join(path_to_directory, folder)
        tiff_to_memmap(path_to_tiff, numpy_folder, channel=folder, chunk_size=chunk_size, suffix=suffix, data_type=data_type, collect_image_metadata = collect_image_metadata)



# Loading memmmaps utilities

def open_memmap(path_to_memmap, path_to_metadata):

    with open(path_to_metadata, 'r') as f:
        metadata = json.load(f)
    
    data = np.memmap( path_to_memmap, dtype = metadata['data_type'], mode='r', shape = tuple(metadata['shape']) )

    return data


def open_metadata(path_to_metadata, field_name = None):

    with open(path_to_metadata, 'r') as f:
        metadata = json.load(f)

    if field_name:
        return metadata[field_name]
    else:
        return metadata