import sys
import os
import time
import hashlib
import shutil
import logging


def folder_check(src_path:str, replica_path:str, logger) -> bool:
    """

    folder_check function checks if the paths are valid

    :param src_path:str -
    :param replica_path: str -
    :param logger:
    :return: True if paths are valid and false if not
    """
    if not os.path.isdir(src_path):
        logger.error(f'No source folder ant the {src_path}')
        return False
    if not os.path.isdir(replica_path):
        logger.error(f'No replica folder ant the {replica_path}')
        return False

    return True

def log_setup():
    """
    this loger setup is created in case that not enough arguments will be passed to the program,
    in this case we still have to give a valid log message
    :return logger: only for the console
    """
    logger = logging.getLogger('sync')
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter("{asctime} - {levelname} - {message}",style="{",datefmt="%Y-%m-%d %H:%M", )

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    if not logger.handlers:
        logger.addHandler(console_handler)
    return logger

def log_setup_wth_logpath(log_path):
    """
    this function is called only in case that enough arguments were passed to the program
    Setting up the logger for log file and console, checking if log_path is valid,
    creating log_file if doesnt exist
    :param log_path:
    :return: logger
    """
    logger = log_setup()
    formatter = logging.Formatter("{asctime} - {levelname} - {message}",style="{",datefmt="%Y-%m-%d %H:%M", )

    #Valid log path check, if not, giving an error and working with console only
    try:
        file_handler = logging.FileHandler(log_path)
        file_handler.setFormatter(formatter)
        if len(logger.handlers) == 1:
            logger.addHandler(file_handler)
    except FileNotFoundError:
        logger.error("Invalid log path")

    return logger

#makaing a hash for file
def hashing(file_path:str) -> str:
    """
    Makes a hash  for a file at given path, reads up to 4096 bytes at a time
    :param file_path:str - a pth to the file which is goint to be given a hash
    :return: hash of a file at file_path
    """
    hash_num = hashlib.md5()
    #in case of big file size read first 4096 bytes
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_num.update(chunk)
        return hash_num.hexdigest()




def copy_differnce(src_path:str, replica_path:str, logger) -> None:
    """
    Function is designed to copy files from src if they are absent in dst,
    and to delete content that exists only in dst.

    :param src_path:str - path to src folder
    :param replica_path:str - path to replica or dst folder
    :return: None
    """

    # Creating a lists of content in both folders
    src_content = os.listdir(src_path)
    replica_content = os.listdir(replica_path)

    # checking the difference in folders content via operations with sets
    if set(src_content) != set(replica_content):

        # a set of files/folders that exist only in src, and need to be added to dst
        diff_src = set(src_content) - set(replica_content)

        # a set of files that are unoque to both folders
        dif_src_and_dst = set(src_content) ^ set(replica_content)

        # a set of name of the files that exist only in dst folder, and need to be deleted
        to_delete = dif_src_and_dst - diff_src

        # deleting files from dst
        if len(to_delete) != 0:
            for name in to_delete:
                delete_replica_path = os.path.join(replica_path, name)
                # checking if we need to remove folder or file
                if os.path.isdir(delete_replica_path):
                    shutil.rmtree(delete_replica_path)
                    logger.info(f"Deleted a folder {name} from {replica_path}")
                else:
                    os.remove(delete_replica_path)
                    logger.info(f"Deleted file {name} from {replica_path}")

        # copying src's unique files and folders to dst
        if len(diff_src) != 0:
            for name in diff_src:
                new_src_path = os.path.join(src_path,name)
                if not os.path.isdir(new_src_path):
                    shutil.copy(new_src_path, replica_path)
                    logger.info(f'Copied the file {name} from {src_path} to {replica_path} ')
                elif os.path.isdir(new_src_path):
                    new_replica_path = os.path.join(replica_path,name)
                    os.mkdir(new_replica_path)
                    logger.info(f'Copied a folder {name} from {src_path} to {replica_path}')
                    #Recursive folder_synchronization
                    copy_differnce(new_src_path, new_replica_path, logger)
    else:
        for folder_name in src_content:
            new_src_path = os.path.join(src_path, folder_name)
            new_replica_path = os.path.join(replica_path, folder_name)
            if os.path.isdir(new_src_path) :
                copy_differnce(new_src_path, new_replica_path, logger)



def hash_check(src_path:str, dst_path:str, logger) -> None:
    """
    Function goes through all files and compares their hash in src and in replica, if not the same,
    delete the file/folder from replica and copy it from src
    :param src_path:srt - path to src folder
    :param dst_path:str - path to replica or dst folder
    :return: None
    """
    #Going through the content and comparing their hash, deleting and copying if hash is different
    for name in os.listdir(src_path):
        current_src_filepath: str = os.path.join(src_path, name)
        current_dst_filepath: str = os.path.join(dst_path, name)
        #Recursion if the current path points to folder
        if os.path.isdir(current_src_filepath):
            hash_check(current_src_filepath, current_dst_filepath, logger)
            continue
        if hashing(current_src_filepath) == hashing(current_dst_filepath):
            continue
        else:
            #if files are not the same, remove it from replica and copy from src
            os.remove(current_dst_filepath)
            shutil.copy(current_src_filepath, dst_path)
            logger.info(f'Removed {current_dst_filepath} form replica, due to different content, copied {current_src_filepath} to replica')

    return None




def folder_sync(src_path:str,replica_path:str,sync_count:int, interval:float, logger) -> None:
    """
    function combines copy diff and hash check.

    :param: srt_path, dst_path (str) - the paths to the src and dst folders
    :return: None, the function doesn't return anything, but makes dst an exact copy of src
    """

    if folder_check(src_path, replica_path, logger):
        logger.info("Synchronization started")
        for i in range(sync_count):
            copy_differnce(src_path, replica_path, logger)
            hash_check(src_path, replica_path, logger)
            if i < (sync_count - 1):
                time.sleep(interval)
        logger.info("Synchronization finihed")
    else:
        logger.info(f"Unable to start syncro, {src_path} or {replica_path} does not exist")


def arguments_count_validity(argument_count) -> bool:
    if argument_count != 6:
        logger = log_setup()
        logger.error("Not enough parameters")
        return False
    return True


def numbers_value_check(logger):
    try:
        interval = float(sys.argv[3])
    except ValueError:
        logger.error("Not valid interval type, should be float type")
        return False
    try:
        sync_count = int(sys.argv[4])
    except ValueError:
        logger.error("Not valid amount of synchronization, should be int type")
        return False
    return True



def main():
    """
    -takes arguments from CL
    -checks if enough arguments were passed: log.error console message if not
    -checks if paths have '/' in the end
    -setups a logger
    -checks if values for interval and sync count are valid
    -checks if paths are correct
    -starts a loop of in range of  sync_count
    -syncs 2 folders
    -sleeps for the given interval

    :return: synchronizes folders if they exist
    """
    if arguments_count_validity(len(sys.argv)):
        scrip_name = sys.argv[0]
        # checking if there is '/' in the end of paths, adding if not
        src_path = sys.argv[1] + '/' if sys.argv[1][-1] != '/' else sys.argv[1]
        replica_path = sys.argv[2] + '/' if sys.argv[2][-1] != '/' else sys.argv[2]

        log_path = sys.argv[5]
        logger = log_setup_wth_logpath(log_path)
        if numbers_value_check(logger):
            interval = float(sys.argv[3])
            sync_count = int(sys.argv[4])

            folder_sync(src_path,replica_path,sync_count,interval,logger)

if __name__ == "__main__":
    main()