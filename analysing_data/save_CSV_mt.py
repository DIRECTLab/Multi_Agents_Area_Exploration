# import os
# import csv
# import threading
# import pandas as pd
# from multiprocessing import Pool
# import tqdm
# import time


# # Global lock for thread synchronization
# lock = threading.Lock()

# def search_folders(root_folder, level=0):
#     csv_files = []
#     # Recursively search folders for CSV files
#     for root, dirs, files in os.walk(root_folder):
#         for file in files:
#             if file.endswith(".csv"):
#                 file_path = os.path.join(root, file)
#                 csv_files.append(file_path)

#         for dir in dirs:
#             csv_files.extend(search_folders(dir, level=level+1))

#     return csv_files


# def merg_two_csv(path1,path2):
#     return pd.concat([pd.read_csv(path1),
#                       pd.read_csv(path2)],ignore_index=True)

# def merge_csv(result):
#     return 

# def work_on_chunck(chunck):
#     # Merge all CSV files in the chunk
#     restults = []
#     if type(chunck[0]) != str:
#         return pd.concat(chunck, ignore_index=True)
    
#     for item in chunck:
#         restults.append(pd.read_csv(item))
#     return pd.concat(restults, ignore_index=True)


# if __name__ == "__main__":
#     root_folder = "data"
#     csv_files = search_folders(root_folder)
#     print(len(csv_files))

#     # cet the numer of cores
#     cores = os.cpu_count() -2
#     print(f"Using {cores} cores")

#     # split the files into chunks
#     chunks = [csv_files[i::cores] for i in range(cores)]
#     chunks = chunks[:cores]
#     while len(chunks)>1:

#         with Pool(cores) as p:
#             r = list(tqdm.tqdm(p.imap(work_on_chunck, chunks), total=len(chunks), colour="MAGENTA", desc=">>⏰ Chuncking Progress"))

#         chunks = [r[i::cores] for i in range(cores)]

#     # Save the merged CSV file
#     r.to_csv("merged.csv", index=False)




import os
import csv
import threading
import pandas as pd
from multiprocessing import Pool
import tqdm
import time


# Global lock for thread synchronization
lock = threading.Lock()

def search_folders(root_folder):
    csv_files = []

    # Recursively search folders for CSV files
    for root, dirs, files in os.walk(root_folder):
        for file in files:
            if file.endswith(".csv"):
                file_path = os.path.join(root, file)
                csv_files.append(file_path)

        for dir in dirs:
            csv_files.extend(search_folders(dir))

    return csv_files


def merg_two_csv(path1,path2):
    return pd.concat([pd.read_csv(path1),
                      pd.read_csv(path2)],ignore_index=True)

def work_on_chunck(chunck):
    # Merge all CSV files in the chunk
    merged_csv = pd.concat([pd.read_csv(file) for file in chunck])

    return merged_csv

if __name__ == "__main__":
    root_folder = "data"
    csv_files = search_folders(root_folder)
    print(len(csv_files))

    # cet the numer of cores
    cores = os.cpu_count() -2
    print(f"Using {cores} cores")

    # split the files into chunks
    chunks = [csv_files[i::cores] for i in range(cores)]

    with Pool(cores) as p:
        r = list(tqdm.tqdm(p.imap(work_on_chunck, chunks), total=len(chunks), colour="MAGENTA", desc=">>⏰ Experiments Progress"))

    # Merge all CSV files in the chunk
    merged_csv = pd.DataFrame()
    for result in tqdm.tqdm(r, colour="GREEN", desc="Saving Data", total=len(r)):
        merged_csv = pd.concat([merged_csv, result], ignore_index=True)



    # Save the merged CSV file
    merged_csv.to_csv("data_copy/MT_all_data.csv", index=False)