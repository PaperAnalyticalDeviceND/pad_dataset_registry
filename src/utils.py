import pandas as pd 
import matplotlib.pyplot as plt
import seaborn as sns
import requests
import hashlib
import concurrent.futures
import os
import logging
import csv
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
from PIL import ImageFile, Image
import urllib3
import numpy as np



ImageFile.LOAD_TRUNCATED_IMAGES = True
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Change the image name pattern in this function
def create_filename(x):
    """
    Create a standardized filename based on input data.

    Args:
        x (dict): A dictionary containing information to construct the filename.

    Returns:
        str: The constructed filename in the format "{id}__{sample_name}__{quantity}".

    Example:
        input_data = {
            'id': 123,
            'sample_name': 'Acetaminphen Codeine',
            'quantity': 5
        }
        filename = create_filename(input_data)
        # Resulting filename: "123__acetaminphen-codeine__5"
    """    
    # Convert `sample_name` to lowercase and replace spaces with hyphens
    transformed_name = x['sample_name'].lower().replace(' ', '-')
    
    # Create the filename
    #fname = f"{x['id']}__{transformed_name}__{x['quantity']}__{x['image_hash']}.png"
    fname = f"{x['id']}__{x['sample_id']}__{transformed_name}__{x['quantity']}.png"
    
    return fname

def get_iso8601_datetime():
    import pytz
    from datetime import datetime
    
    # Create a datetime object for the current time
    current_time = datetime.now()

    # Set the timezone to UTC
    current_time_utc = current_time.replace(tzinfo=pytz.UTC)

    # Format the datetime in ISO 8601 format
    iso8601_datetime = current_time_utc.strftime('%Y-%m-%dT%H:%M:%S%z')

    return iso8601_datetime

def standardize_names(name):
    return name.lower().replace(' ', '-')

def show_by_camera_type(df, sample_id):

    # select samples by sample_id    
    samples = df[df['sample_id'] == sample_id]

    # setup for ipyplot
    label_column = 'camera_type_1'
    images = samples['url'].values
    labels = samples[label_column].values
    labels_list_filtered = samples[label_column].unique().tolist()
    
    # Show with tabs
    ipyplot.plot_class_tabs(
        images, labels, tabs_order=labels_list_filtered, show_url=False,
    )

def list_url_by_camera_type(df, sample_id):
    samples = df[df['sample_id'] == sample_id]
    for _,sample in samples.iterrows():
      print(f"{sample['id']}\t{sample['sample_name']}\t{sample['camera_type_1']}\t\t{sample['quantity']}\t{sample['url']}")


def get_heatmap_table(df, rows, cols, values, rows_order = None):
    import pandas as pd 
    df_cat = df.copy()    
    df_cat[rows] = pd.Categorical(df_cat[rows])
    df_cat[rows] = df_cat[rows].cat.set_categories(rows_order) 
    df_cat.sort_values([rows], inplace=True)
    table = df_cat.pivot(index=rows, columns=cols, values=values)
    return table
    
# def show_heatmap_tables(table1, table2, save_name= None, figsize=(18, 8)):
#     #plt.rcParams["figure.figsize"] = [7.00, 3.50]
#     plt.rcParams["figure.autolayout"] = True
#     fig, axes = plt.subplots(1, 2, figsize=figsize)

#     sns.heatmap(table1, annot=True, annot_kws={"size": 9}, fmt='g', cmap='Blues', linewidths=.4,  ax=axes[0])
#     sns.heatmap(table2, annot=True, annot_kws={"size": 9}, fmt='g', cmap='Blues', linewidths=.4,  ax=axes[1])
#     plt.show()
#     if save_name: fig.savefig(save_name, bbox_inches='tight')    
    
def show_heatmap_tables(table1, table2, save_name=None, figsize=(18, 8),
                        caption="Your main caption here", title1="Table 1", title2="Table 2", cmap='Blues'):
    plt.rcParams["figure.autolayout"] = True
    fig, axes = plt.subplots(1, 2, figsize=figsize)

    sns.heatmap(table1, annot=True, annot_kws={"size": 9}, fmt='g', cmap=cmap, linewidths=.4, ax=axes[0])
    axes[0].set_title(title1)  # Title for the first heatmap

    sns.heatmap(table2, annot=True, annot_kws={"size": 9}, fmt='g', cmap=cmap, linewidths=.4, ax=axes[1])
    axes[1].set_title(title2)  # Title for the second heatmap

    plt.suptitle(caption)  # Main caption/title for the figure

    plt.show()
    
    if save_name: 
        fig.savefig(save_name, bbox_inches='tight')



def show_heatmap(df, rows, cols, values, rows_order = None, save_name= None, figsize=(6, 6)):
    import pandas as pd 
    import matplotlib.pyplot as plt
    import seaborn as sns
    
    df_cat = df.copy()
    df_cat[rows] = pd.Categorical(df[rows], rows_order)
    table = df_cat.pivot(index=rows, columns=cols, values=values)
    
    fig, _ = plt.subplots(figsize=figsize)
    sns.heatmap(table, annot=True, annot_kws={"size": 9}, fmt='g', cmap='Blues', linewidths=.4)
    plt.show()
    if save_name: fig.savefig(save_name,bbox_inches='tight') 
    

def check_duplicates_by_hash(df):
    num_samples = df['url_status_code'].isin([200]).sum()
    x = df.groupby(['hashlib_md5']).size().reset_index(name='counts')
    one_sample_hash = x[x['counts']==1]
    two_more_sample_hash = x[x['counts']>1]

    if len(one_sample_hash.index) < len(x.index):
        print('Summary:')
        print(f"Total unique hash codes : {len(x.index)}")
        print(f"Total of hash code with one sample: {len(one_sample_hash.index)}")
        print(f"Total of hash code with two or more samples: {len(two_more_sample_hash.index)}")
        
        print('')
        print(f"Total of samples: {num_samples}")
        print(f"Total of samples without duplicates: {len(x.index)}")
        print(f"Total of samples in some duplicate case (will be deleted): {num_samples-len(x.index)}")

        return two_more_sample_hash

    else:
        print('There is no duplicates.')
        return 0
    
    
    
# Filter by sample_name column
def filter_by_sample_name(df, sample_name):
    return df[df['sample_name'].str.contains(sample_name, case=False)].copy()

# Filter by not empty and not null column_name
def filter_by_not_empty_column(df, column_name):
    if column_name not in df.columns:
        raise ValueError("The column name is not in the dataframe")
    else:
        return df[df[column_name].notnull() & (df[column_name] != "")].copy()

# Filter by not empty and not null column_name
def filter_by_empty_column(df, column_name):
    if column_name not in df.columns:
        raise ValueError("The column name is not in the dataframe")
    else:
        return df[(df[column_name].isnull()) or (df[column_name] == "")].copy()
    
    
# Filter by 'unknown' column_name
def filter_by_unknown_column(df, column_name):
    if column_name not in df.columns:
        raise ValueError("The column name is not in the dataframe")
    else:
        return df[df[column_name] == "unknown"].copy()
    
# Filter by column_name and value
def filter_by_value_column(df, column_name, value):
    if column_name not in df.columns:
        raise ValueError(f"The column name {column_name} is not in the dataframe")
    else:
        return df[df[column_name] == value].copy()    

# Filter by column_name and value
def filter_by_no_value_column(df, column_name, value):
    if column_name not in df.columns:
        raise ValueError(f"The column name {column_name} is not in the dataframe")
    else:
        return df[df[column_name] != value].copy()    


def url_pad(file_location):
  return PAD_URL + str(file_location)
    

def get_project_data(project_id):

    
    API_URL = f"https://pad.crc.nd.edu/api/v2/projects/{project_id}/cards"
    try:
        # fetch_data_from_api
        r = requests.get(url=API_URL,verify=False)  # NOTE: Using verify=False due to a SSL issue, I need a valid certificate, then I will remove this parameter.
        r.raise_for_status() # Raise an exception if the status is not 200
        data = r.json()
        df = pd.json_normalize(data)
        return df
    except requests.exceptions.RequestException as e:
        print(e)
        print(f"Error accessing project data {project_id}: {r.status_code}")
        return None

def check_url(df):
    # Initialize an empty DataFrame to store bad URLs and their status codes
    bad_urls_df = pd.DataFrame(columns=['url', 'status_code'])
    
    # Check if the 'url' column has valid data
    if 'url' in df:
        # Check if URLs are formed correctly
        for url in df['url']:
            # Try to access the image
            response = requests.head(url, verify=False)
            if response.status_code != 200:
                # If the URL is bad, add it to the DataFrame
                bad_urls_df = bad_urls_df.append({'url': url, 'status_code': response.status_code}, ignore_index=True)
    else:
        print("DataFrame doesn't contain 'url' column.")
        
    # Return the DataFrame containing bad URLs
    return bad_urls_df


def check_hash(sample, output_folder):
    filename = create_filename(sample)
    filepath = os.path.join(output_folder, filename)
    if os.path.exists(filepath):
        if sample['image_hash'] == hashlib.md5(open(filepath,'rb').read()).hexdigest():
            return True
        else:
            return False
    else:
        return False
    
def get_hash(sample, folder):
    filename = create_filename(sample)
    filepath = os.path.join(folder, filename)
    #print(sample['id'], sample['url_status_code'], filepath)
    if sample['url_status_code'] == 200:
        if os.path.isfile(filepath):
            hashlib_md5 = hashlib.md5(open(filepath,'rb').read()).hexdigest()
            #print(hashlib_md5)
            return hashlib_md5
        else:
            print(f"File not found {filepath}. Downloading...")
            status_code = save_image_from_url(sample, folder)
            if status_code == 200:
                hashlib_md5 = hashlib.md5(open(filepath,'rb').read()).hexdigest()
                return hashlib_md5
            else:
                print(f"Error downloading {sample['id']}. File not found {filepath}")
                return None
    else:        
        return None


def save_image_from_url(sample, output_folder):
    r = requests.get(sample.url, verify=False)
    output_path = os.path.join(
        output_folder, create_filename(sample)
    )
    with open(output_path, "wb") as f:
        f.write(r.content)
        
    status_code = r.status_code
    r.close()
    return status_code


def delete_image(sample, folder):
    filename = create_filename(sample)
    filepath = os.path.join(folder, filename)
    print(filepath)
    if os.path.exists(filepath):
        os.remove(filepath)


def get_url_status_code(url):
    r = requests.head(url, verify=False)
    return r.status_code

def get_hash_all(df, folder):    
    column_exists = "url_status_code" in df.columns
    
    if ~column_exists:
        df['url_status_code'] = df['url'].apply(lambda x: get_url_status_code(x))
    
    hash_codes = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        future_to_url = {
            executor.submit(get_hash, sample, folder): sample for _, sample in df.iterrows()
        }
        for future in concurrent.futures.as_completed(
            future_to_url
        ):
            sample = future_to_url[future]
            try:               
                #print(sample['id'], sample['url'], sample['url_status_code'] ,future.result())
                hash_codes.append([sample['id'], sample['url_status_code'], future.result()])
                
            except Exception as exc:
                print(
                    "%s generated an exception: %s" % (sample['id'], exc)
                )
    return hash_codes

# Set up logging to file
logging.basicConfig(filename='download_errors.log', level=logging.ERROR,
                    format='%(asctime)s %(levelname)s:%(message)s')

def download_file(url, filename, images_path):
    """Download a file from a URL and save it to a local file."""
    try:
        response = requests.get(url, stream=True, verify=False)
        if response.status_code == 200:
            path = os.path.join(images_path, filename)
            with open(path, 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            # print(f"File '{filename}' successfully downloaded to '{images_path}'")
        else:
            # Log error if the response status code is not 200
            logging.error(f"Failed to download the file. URL: {url} returned status code: {response.status_code}")
            raise Exception(f"Failed to download the file. URL: {url} returned status code: {response.status_code}")
    except Exception as e:
        # Log any other exceptions during the download process
        logging.error(f"An error occurred while downloading the file: {e}")
        # Optionally, you can re-raise the exception if you want it to be noticed by the calling function
        raise


def download_files_from_csv_file(file_path, images_path):
    """Download files in parallel based on URLs from a CSV file with a progress bar."""
    # Open the CSV file and parse its content
    with open(file_path, newline='') as csvfile:
        rows = list(csv.DictReader(csvfile)) # Convert to list for tqdm

        # Initialize tqdm for the progress bar
        pbar = tqdm(total=len(rows), desc="Downloading files")

        def update(*args):
            # Update the progress bar by one each time a file is downloaded
            pbar.update()

        # Use ThreadPoolExecutor to download files in parallel
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = []
            for row in rows:
                url = row['url']
                filename = row['image_name']
                
                # check if filename is already downloaded
                if os.path.exists(os.path.join(images_path, filename)):
                    continue
                  
                # Schedule the download task
                future = executor.submit(download_file, url, filename, images_path)
                future.add_done_callback(update)
                futures.append(future)

            # Wait for all futures to complete
            for future in futures:
                future.result()

        # Close the progress bar
        pbar.close()



##****************************************************************************##
# Preprocessing functions: Extract RGB Information for FHI360
##****************************************************************************##
import os
import csv
import math
import warnings
import cv2 as cv
import pandas as pd
import urllib.request
from datetime import datetime
import ssl

SAVE_DIR = './pixel_data/'
REQS = {'LOG':'log.txt'}

HORIZONTAL_BORDER = 12
VERTICAL_BORDER = 0

BLACK_THRESH_S = 35
BLACK_THRESH_V = 70

#!touch temp.png # Creates a temporary file for image processing
with open('temp.png', 'a'):
    pass

#Takes a list of pixels and a BGR image and returns the average
# Lab pixel values
def px_avgPixelsLAB(pixels, img):
  """Calculate the average Lab pixel values for a list of pixels in a BGR image."""
  workingImg = cv.cvtColor(img, cv.COLOR_BGR2Lab)
  totalL = 0
  totalA = 0
  totalB = 0
  for pixel in pixels:
    x = pixel[0]
    y = pixel[1]
    l, a, b = workingImg[x,y,:]
    totalL += l
    totalA += a
    totalB += b
  if len(pixels) != 0:
    totalL /= len(pixels)
    totalA /= len(pixels)
    totalB /= len(pixels)
  return int(totalL + 0.5), int(totalA + 0.5), int(totalB + 0.5)


#Takes a list of pixels and a BGR image and returns the average
# RGB pixel values
def px_avgPixels(pixels, img):
  """Calculate the average RGB pixel values for a list of pixels in a BGR image."""
  totalB = 0
  totalG = 0
  totalR = 0
  for pixel in pixels:
    x = pixel[0]
    y = pixel[1]
    b,g,r = img[x,y,:]
    totalB += b
    totalG += g
    totalR += r
  if len(pixels) != 0:
    totalB /= len(pixels)
    totalG /= len(pixels)
    totalR /= len(pixels)
  return int(totalR + 0.5), int(totalG + 0.5), int(totalB + 0.5)


#Takes a distance from a center and returns a weight between 0 and 1
# determined by cosine such that a point at the cetner has weight 1,
# and a point at the extremes has weight ~0.
def intFind_cosCorrectFactor(dx, dy, centerX, centerY):
  """Determine a weight between 0 and 1 based on distance from center, using a cosine function."""
  relevantD = max((dx/centerX), dy/centerY)
  relevnatDRads = (math.pi/2) * relevantD
  return math.cos(relevnatDRads)

#Takes a HSV image and returns a list of the most intense pixels in it,
# after applying filtering to minimize black bars on the edges
def intFind_findMaxIntensitiesFiltered(img):
  """Return a list of pixels with maximum intensity, filtering out black bars on edges."""
  imgS = img[:,:,1]
  imgV = img[:,:,2]
  maxI = 0
  maxSet = []
  centerX = imgS.shape[0]/2
  centerY = imgS.shape[1]/2

  for i in range(imgS.shape[0]):
    dX = abs(centerX-i)
    for j in range(imgS.shape[1]):
      dY = abs(centerY-j)
      sF = intFind_cosCorrectFactor(dX,dY,centerX,centerY)
      cS = sF*imgS[i,j]
      cV = sF*imgV[i,j]
      if cS <= BLACK_THRESH_S and cV <= BLACK_THRESH_V:
        pass
      else:
        maxSet.append((i,j))
  return maxSet

def fm_genIndex(regions, ColorList = ['R', 'G', 'B']):
  """Generate an index for CSV column headers based on the number of regions and color list."""

  index = ['Image', 'Contains', 'Drug %', 'PAD S#']
  for letter in ['A','B','C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L']:
    for j in range(1,regions+1):
      for color in ColorList:
        tempStr = letter+str(j)+'-'+color
        index.append(tempStr)
  return index

def fm_checkFormating(dir=SAVE_DIR, errorsFile=None):
  """Check formatting and required files in the specified directory."""
  if not os.path.isdir(dir):
    os.mkdir(dir)
  if errorsFile is None:
    errors = open(dir+REQS['LOG'], 'a')
  else:
    errors = errorsFile
  files = os.listdir(dir)
  #print(files)
  for item in REQS.values():
    if item not in files:
      errorString = str.format("Required file %s not found, creating.\n" %(item))
      errors.write(errorString)
      warnings.warn(errorString)
      if item is REQS['LOG']:
        temp = open(dir+item, 'w')
        temp.close()
      else:
        os.mkdir(dir+item)
  if errorsFile is None:
    errors.close()

def _regionGen(regions, region):
  """Generate start and end points for a given region."""
  start = 359
  totalLength = 273
  regionStart = start + math.floor(totalLength * (region/regions)) + VERTICAL_BORDER
  regionEnd = start + math.floor(totalLength * ((region+1)/regions)) - VERTICAL_BORDER
  return regionStart, regionEnd

def _fullRoutine(img, roiFunc, df, RGB=True, regions=3):
  """Complete routine for processing an image and extracting pixel information."""

  letters = ['A','B','C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L']
  rList = []
  gList = []
  bList = []
  imgHSV = cv.cvtColor(img, cv.COLOR_BGR2HSV)
  for lane in range(1,13):
    laneStart = 17 + (53*lane)+HORIZONTAL_BORDER
    laneEnd = 17 + (53*(lane+1))-HORIZONTAL_BORDER
    letter = letters[lane-1]
    for region in range(regions):
      regionStart, regionEnd = _regionGen(regions, region)
      roi = imgHSV[regionStart:regionEnd,laneStart:laneEnd,:]
      rgbROI = img[regionStart:regionEnd,laneStart:laneEnd,:]
      pixels = roiFunc(roi)
      tempString = letter + str(region+1) + "-"
      #Switches between RGB and Lab
      if(RGB):
        r, g, b = px_avgPixels(pixels, rgbROI)
        df[tempString+'R'] = r
        df[tempString+'G'] = g
        df[tempString+'B'] = b
      else:
        l, a, blu = px_avgPixelsLAB(pixels, rgbROI)
        df[tempString+'L'] = l
        df[tempString+'a'] = a
        df[tempString+'b'] = blu
  return df


def addIndex(runSettings):
  """Add index information to run settings based on regions and color mode (RGB or Lab)."""
  for setting in runSettings:
    regions = runSettings[setting]['regions']
    if(runSettings[setting]['RGB']):
      runSettings[setting]['Index'] = fm_genIndex(regions)
    else:
      runSettings[setting]['Index'] = fm_genIndex(regions, ['L','a','b'])
  return runSettings

def regionRoutine(target, runSettings, save_dir=SAVE_DIR):
  """Read a CSV file and process images according to the run settings."""

  ssl._create_default_https_context = ssl._create_unverified_context
  
  startTime = datetime.now()
  url = 'https://pad.crc.nd.edu'
  dest = 'temp.png'
  fm_checkFormating(save_dir)
  errors = open(save_dir+REQS['LOG'], 'a')
  #print("Starting...")
  with open(target) as csvfile:
    csvreader = csv.reader(csvfile, )
    i = 0
    next(csvreader)  # Skip the first line
    for row in csvreader:
      cTime = datetime.now()
      i+=1
      try:
        urllib.request.urlretrieve(row[5], dest)
        #urllib.request.urlretrieve(row[7], dest)
        img = cv.imread(dest)
        if (1250, 730, 3) != img.shape and (1220, 730, 3) != img.shape:
          errorString = str.format("Error with file %s. Expected shape %s, found shape %s.\n" %(file, '(1250, 730, 3) or (1220, 730, 3)', str(img.shape)))
          errors.write(errorString)
          warnings.warn(errorString)
        else:
          for setting in runSettings:
            data = {}
            data = _fullRoutine(img, intFind_findMaxIntensitiesFiltered, data, runSettings[setting]['RGB'], runSettings[setting]['regions'])
            #data['Image'] = row[0]
            #data['Contains'] = row[1]
            #data['Drug %'] = row[18]
            #data['PAD S#'] = row[17]

            data['Image'] = row[0]
            data['Contains'] = row[2]
            data['Drug %'] = row[3]
            data['PAD S#'] = row[1]


            df = pd.DataFrame(data, columns=runSettings[setting]['Index'], index=[data['Image']])
            if(not os.path.exists(save_dir+setting)):
              df.to_csv(save_dir+setting, mode='w', header=True)
            else:
              df.to_csv(save_dir+setting, mode='a', header=False)
          elapsedTime = datetime.now() - cTime
          # print("Finished image ",row[0]," in ",elapsedTime)
      except Exception as e:
        errorString = str.format("Error %s with file %s.\n" %(str(e), row[0]))
        errors.write(errorString)
        warnings.warn(errorString)
      os.remove(dest)
    errors.close()
    endTime = datetime.now()
    regions = 3+12+20
    print('Time: ',endTime-startTime, ' time saved = ',i*regions*13/60.0)
    

def convert_from_cv2_to_image(img: np.ndarray) -> Image:
    # return Image.fromarray(img)
    return Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))


def convert_from_image_to_cv2(img: Image) -> np.ndarray:
    # return np.asarray(img)
    return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
  