import sys
import os
import time
import hashlib
import shutil
import logging


def safe_listdir(path:str, logger: logging.Logger):
    """
    function makes a permission safe listing of the folders content
    :param path:str - path to file
    :param logger
    :return a list of paths content or none if there is a permission problem
    """
    try:
        return os.listdir(path)
    except PermissionError:
        logger.error(f"No permission to read from {path}")
        return None

def safe_remove(path:str, logger: logging.Logger) -> bool:
    """
    function permissionwise safely removes  file or folder
    :param path:str - path to file
    :param logger
    :return bool - True if file/folder was safely removed, False if permission problem occurred

    """
    try:
        if os.path.isdir(path):
            shutil.rmtree(path)
            return True
        else:
            os.remove(path)
            return True
    except PermissionError:
        logger.error(f"No permission to write or delete in {path}")
        return False

def safe_mkdir(path:str, logger: logging.Logger) -> bool:
    """
       function permissionwise safely creates a folder
       :param path:str - path to new folder
       :param logger
       :return bool - True if folder was safely created, False if permission problem occurred

       """
    try:
        os.mkdir(path)
        return True
    except PermissionError:
        logger.error(f"No write permission for {path}")
        return False

def safe_copy(src_filepath:str, replica_path:str, logger: logging.Logger) -> bool:
    """
       function permissionwise safely copies file from src to replica
       :param src_filepath:str - path to src_file that need to be copied to replica
       :param replica_path:str - path to replica where copied file will be located
       :param logger
       :return bool - True if file was safely copied to replica, False if permission problem occurred

       """
    try:
        shutil.copy(src_filepath, replica_path)
        return True
    except PermissionError:
        logger.error(f" No write permission in {replica_path}")
        return False


def folder_check(src_path:str, replica_path:str, logger: logging.Logger) -> bool:
    """

    folder_check function checks if the paths are valid

    :param src_path:str -
    :param replica_path: str -
    :param  logger: logging.Logger - logger
    :return bool -  True if paths are valid and False if not
    """
    if not os.path.isdir(src_path):
        logger.error(f'No source folder ant the {src_path}')
        return False
    if not os.path.isdir(replica_path):
        logger.error(f'No replica folder ant the {replica_path}')
        return False

    return True

def log_setup() -> logging.Logger:
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

def log_setup_wth_logpath(log_path) -> logging.Logger:
    """
    this function is called only in case that enough arguments were passed to the program
    Setting up the logger for log file and console, checking if log_path is valid,
    creating log_file if it doesn't exist
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
    except PermissionError:
        logger.error(f"No permission write for {log_path}, using console log only")

    return logger

#makaing a hash for file
def hashing(file_path:str, logger: logging.Logger) -> str|None:
    """
    Makes a hash  for a file at given path, reads up to 4096 bytes at a time
    :param file_path:str - a pth to the file which is goint to be given a hash
    :param logger - logger
    :return: hash of a file at file_path and None if permission problem occurred
    """
    try:
        hash_num = hashlib.md5()
        #in case of big file size read first 4096 bytes
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_num.update(chunk)
            return hash_num.hexdigest()
    except PermissionError:
        logger.error(f"No permission to read {file_path}")
        return None




def copy_difference(src_path:str, replica_path:str, logger: logging.Logger) -> bool:
    """
    Function copies files from src if they are absent in dst,
    and to delete content that exists only in dst.

    :param src_path:str - path to src folder
    :param replica_path:str - path to replica or dst folder
    :param  logger: logging.Logger - logger
    :return: bool - True if the difference is copied/deleted,
    False if function stumbles upon file or folder with not fitting permissions
    """

    # Creating a lists of content in both folders
    src_content = safe_listdir(src_path, logger)
    replica_content = safe_listdir(replica_path,logger)
    # src_content = os.listdir(src_path)
    # replica_content = os.listdir(replica_path)

    if src_content is None or replica_content is None:
        return False


    # checking the difference in folders content via operations with sets
    if set(src_content) != set(replica_content):

        # a set of files/folders that exist only in src, and need to be added to dst
        diff_src = set(src_content) - set(replica_content)

        # a set of files that are unique for both folders
        dif_src_and_dst = set(src_content) ^ set(replica_content)

        # a set of name of the files that exist only in dst folder, and need to be deleted
        to_delete = dif_src_and_dst - diff_src

        # deleting files from dst
        if len(to_delete) != 0:
            for name in to_delete:
                delete_replica_path = os.path.join(replica_path, name)
                # checking if we need to remove folder or file
                # if os.path.isdir(delete_replica_path):
                #     shutil.rmtree(delete_replica_path)
                #     logger.info(f"Deleted a folder {name} from {replica_path}")
                # else:
                #     os.remove(delete_replica_path)
                #     logger.info(f"Deleted file {name} from {replica_path}")
                if not safe_remove(delete_replica_path, logger):
                    return False
                logger.info(f"Deleted  {name} from {replica_path}")





        # copying src's unique files and folders to dst
        if len(diff_src) != 0:
            for name in diff_src:
                new_src_path = os.path.join(src_path,name)
                if not os.path.isdir(new_src_path):
                    if not safe_copy(new_src_path,replica_path, logger):
                        return False
                    # shutil.copy(new_src_path, replica_path)
                    logger.info(f'Copied the file {name} from {src_path} to {replica_path} ')
                elif os.path.isdir(new_src_path):
                    new_replica_path = os.path.join(replica_path,name)
                    if not safe_mkdir(new_replica_path, logger):
                        return False
                    # os.mkdir(new_replica_path)
                    logger.info(f'Copied a folder {name} from {src_path} to {replica_path}')
                    #Recursive folder_synchronization
                    if not copy_difference(new_src_path, new_replica_path, logger):
                        return False
    else:
        for folder_name in src_content:
            new_src_path = os.path.join(src_path, folder_name)
            new_replica_path = os.path.join(replica_path, folder_name)
            if os.path.isdir(new_src_path) :
                if not copy_difference(new_src_path, new_replica_path, logger):
                    return False
    return True



def hash_check(src_path:str, dst_path:str, logger: logging.Logger) -> bool:
    """
    Function goes through all files and compares their hash in src and in replica, if not the same,
    delete the file/folder from replica and copy it from src
    :param src_path:srt - path to src folder
    :param dst_path:str - path to replica or dst folder
    :param  logger: logging.Logger - logger
    :return: bool - True if no problem occurred and operation finished, False if permission problem occurred
    """
    #Going through the content and comparing their hash, deleting and copying if hash is different
    for name in os.listdir(src_path):
        current_src_filepath: str = os.path.join(src_path, name)
        current_dst_filepath: str = os.path.join(dst_path, name)
        #Recursion if the current path points to folder
        if os.path.isdir(current_src_filepath):
            if not hash_check(current_src_filepath, current_dst_filepath, logger):
                return False
            continue
        src_hash = hashing(current_src_filepath, logger)
        dst_hash = hashing(current_dst_filepath,logger)
        if src_hash is None or dst_hash is None:
            return False
        else:
            if src_hash == dst_hash:
                continue
            else:
                #if files are not the same, remove it from replica and copy from src
                # os.remove(current_dst_filepath)
                if not safe_remove(current_dst_filepath, logger):
                    return False
                # shutil.copy(current_src_filepath, dst_path)
                if not safe_copy(current_src_filepath, dst_path, logger):
                    return False
                logger.info(f'Removed {current_dst_filepath} form replica, due to different content, copied {current_src_filepath} to replica')

    return True




def folder_sync(src_path:str,replica_path:str,sync_count:int, interval:float, logger: logging.Logger) -> bool:
    """
    function combines copy diff and hash check.

    :param src_path:str - path to the src folder
    :param replica_path:str - a path to replica folder
    :param  logger: logging.Logger - logger
    :param sync_count:int - a number of times that synchronization will run
    :param interval:float - a time interval between the synchronizations
    :return: bool -  returns true if synchronization was successful and False if not
    """

    if folder_check(src_path, replica_path, logger):
        logger.info("Synchronization started")
        for i in range(sync_count):
            if not copy_difference(src_path, replica_path, logger):
                return False
            if not hash_check(src_path, replica_path, logger):
                return False
            if i < (sync_count - 1):
                time.sleep(interval)
        logger.info("Synchronization finished")
        return True
    else:
        logger.info(f"Unable to start synchronization, {src_path} or {replica_path} does not exist")
        return False


def arguments_count_validity(argument_count) -> bool:
    """
    functon checks if enough arguments were passed to the program
    :param argument_count:
    :return:bool - true if enough arguments were passed to the program, false if not
    """
    if argument_count != 6:
        logger = log_setup()
        logger.error("Not enough parameters")
        return False
    return True


def numbers_value_check(logger: logging.Logger)->bool:
    """
    function checks if number arguments were passed properly
    :param logger:
    :return: bool - True if both sync_count and interval were passed properly and False if not
    """

    try:
        interval = float(sys.argv[3])
    except ValueError:
        logger.error("Not valid interval type, should be float type")
        return False
    try:
        sync_count = int(sys.argv[4])
    except ValueError:
        logger.error("Not valid type of synchronization count, should be int type")
        return False
    return True



def main():
    """
    this main function combines and gives a working folder synchronizer
    (a lot of checks and validations placed int the functions themselves)
    - checks if a right amount of arguments is passed to the program
    - checking if there is '/' in the end of paths, adding if not
    - checks the values of interval and synchronization_count
    - synchronizes folders if checks were passed

    :return: synchronizes folders or Log with problems that occurred
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

            if not folder_sync(src_path,replica_path,sync_count,interval,logger):
                logger.error(f"Synchronization was not completed")

if __name__ == "__main__":
    main()