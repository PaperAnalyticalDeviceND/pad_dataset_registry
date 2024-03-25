import pandas as pd 
import matplotlib.pyplot as plt
import seaborn as sns
import requests
import hashlib
import concurrent.futures
import os
        

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
    import requests
    import pandas as pd
    import urllib3

    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
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

