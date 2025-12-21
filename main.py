import sys
import os
import time
import hashlib
import shutil
import logging

SCRIPT_NAME = sys.argv[0]
SRC_PATH = sys.argv[1]
REPLICA_PATH = sys.argv[2]
INTERVAL = float(sys.argv[3])
SYNC_COUNT = int(sys.argv[4])
# LOG_PATH = sys.argv[5]

#checking if there is '/' in the end of paths, adding if not
if SRC_PATH[-1] != '/':
    SRC_PATH += '/'
if REPLICA_PATH[-1] != '/':
    REPLICA_PATH+= '/'



#makaing a hash for file
def hashing(file_path:str) -> str:
    """
    Makes a hash  for a file at given path
    :param file_path:str - a pth to the file which is goint to be given a hash
    :return: hash of a file at file_path
    """
    with open(file_path, "rb") as f:
        content:bytes = f.read()
        hash = hashlib.md5(content)
        return hash.hexdigest()




def copy_differnce(src_path:str, dst_path:str) -> None:
    """
    Function is designed to copy files from src if they are absent in dst,
    and to delete content that exists only in dst.

    :param src_path:str - path to src folder
    :param dst_path:str - path to replica or dst folder
    :return: None
    """

    # Creating a lists of content in both folders
    src_content = os.listdir(src_path)
    dst_content = os.listdir(dst_path)

    # checking the difference in folders content via operations with sets
    if src_content != dst_content:

        # a set of files/folders that exist only in src, and need to be added to dst
        diff_src = set(src_content) - set(dst_content)

        # a set of files that are unoque to both folders
        dif_src_and_dst = set(src_content) ^ set(dst_content)

        # a set of name of the files that exist only in dst folder, and need to be deleted
        to_delete = dif_src_and_dst - diff_src

        # deleting files from dst
        if len(to_delete) != 0:
            for file in to_delete:
                if os.path.isdir(dst_path + file):
                    shutil.rmtree(dst_path + file)
                else:
                    os.remove(dst_path + file)
                print(f'Removed{dst_path + file}')

        # copying src's unique files and folders to dst
        if len(diff_src) != 0:
            for file in diff_src:
                if not os.path.isdir(src_path + file):
                    shutil.copy(src_path + file, dst_path)
                    print(f'copied {src_path + file} to {dst_path}')
                elif os.path.isdir(src_path + file):
                    os.mkdir(dst_path + file)
                    print(f'created a folder in replica {dst_path + file}')
                    copy_differnce(src_path + file + '/', dst_path + file + '/')
    else:
        for folder in src_content:
            if os.path.isdir(src_path + folder) :
                copy_differnce(src_path + folder + '/', dst_path + folder + '/')



def hash_check(src_path:str, dst_path:str) -> None:
    """
    Function goes through all files and compares their hash in src and in replica, if not the same,
    delete the file/folder from replica and copy it from src
    :param src_path:srt - path to src folder
    :param dst_path:str - path to replica or dst folder
    :return: None
    """
    src_content = os.listdir(src_path)
    dst_content = os.listdir(dst_path)
    if src_content != dst_content:
        print (src_content)
        print (dst_content)
        raise ValueError("The folders are not the same")

    else:
    #Going through the content and comparing their hash, deleting and copying if hash is different
        for index in range(len(src_content)):
            current_src_filepath:str = src_path + src_content[index]
            current_dst_filepath: str = dst_path + dst_content[index]
            if os.path.isdir(current_src_filepath):
                hash_check(current_src_filepath + '/', current_dst_filepath + '/')
                continue
            if hashing(current_src_filepath) is hashing(current_dst_filepath):
                continue
            else:
                os.remove(current_dst_filepath)
                shutil.copy(current_src_filepath, dst_path)

    return None




def folder_sync(src_path:str, dst_path:str):
    """
    function combines copy diff and hash check.

    :param: srt_path, dst_path (str) - the paths to the src and dst folders
    :return: None, the function doesn't return anything, but makes dst an exact copy of src
    """
    copy_differnce(src_path,dst_path)


    hash_check(src_path,dst_path)






def main():

    # print("Script: ", SCRIPT_NAME)
    # print('Src: ', SRC_PATH)
    # print('Replica: ', REPLICA_PATH)
    # print('Interval: ', INTERVAL)
    # print('Sync_count: ', SYNC_COUNT)
    # print('Log_path: ', LOG_PATH)


    for  i in range(SYNC_COUNT):
        folder_sync(SRC_PATH, REPLICA_PATH)
        if i < (SYNC_COUNT - 1):
            time.sleep(INTERVAL)



main()
