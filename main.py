import os
import shutil
import filecmp
import datetime
import time

time_interval = 60
log_path = None


def copy(filename, source, replica):
    """This function takes one file, the file path and where the file needs to be copied."""
    sourcefile = os.path.join(source, filename)
    try:
        shutil.copy(sourcefile, replica)
    except FileNotFoundError as e:
        log = f"{e}. Error raised from copy function."
    except PermissionError as p:
        log = f"{p}. Error raised from copy function"
    except OSError as o:
        log = f"{o}. Error raised from copy function"
    else:
        log = f"{datetime.datetime.now()}: File {filename} was copied from {source} to {replica}"
    finally:
        logging(log)


def create(filename, path):
    """This function takes the name of the directory and the path where it needs to create it."""
    sourcefile = os.path.join(path, filename)
    os.mkdir(sourcefile)
    log = f"{datetime.datetime.now()}: Directory {filename} was created in {path}"
    logging(log)


def remove(filename, replica):
    """This function takes the path of a file or directory and removes it in a cascade method"""
    path = os.path.join(replica, filename)
    if os.path.isfile(path):
        try:
            os.remove(path)
        except FileNotFoundError as e:
            log = f"{e}. Error raised from remove function for files"
        except PermissionError as p:
            log = f"{p}. Error raised from remove function for files"
        except OSError as o:
            log = f"{o}. Error raised from remove function for files"
        else:
            log = f"{datetime.datetime.now()}: File {filename} was deleted from {path}"
        finally:
            logging(log)
    else:
        for index in os.listdir(path):
            remove(index, path)
        try:
            os.rmdir(path)
        except FileNotFoundError as e:
            log = f"{e}. Error raised from remove function for directories"
        except PermissionError as p:
            log = f"{p}. Error raised from remove function for directories"
        except OSError as o:
            log = f"{o}. Error raised from remove function for directories"
        else:
            log = f"{datetime.datetime.now()}: Directory {filename} was deleted {path}"
        finally:
            logging(log)


def synchronize(source, replica):
    """This function takes the source path and the replica path to start synchronizing them"""
    file_object = filecmp.dircmp(source, replica)
    # Compares directories and copies files and directories that are only within the source path.
    try:
        for index in file_object.left_only:
            if os.path.isfile(rf"{source}\{index}"):
                copy(index, source, replica)
            else:
                create(index, replica)
                synchronize(os.path.join(source, index), os.path.join(replica, index))
    except FileNotFoundError as e:
        logging(str(e))
    # Searches in directories for files and other directories
    try:
        for index in file_object.common_dirs:
            synchronize(os.path.join(source, index), os.path.join(replica, index))
    except FileNotFoundError as e:
        logging(str(e))
    # Compares common files and copies them even if they are slightly different
    try:
        for index in file_object.common_files:
            source_file = os.path.join(source, index)
            replica_file = os.path.join(replica, index)
            if not filecmp.cmp(source_file, replica_file):
                copy(index, source, replica)
    except FileNotFoundError as e:
        logging(str(e))
    # Removes files and directories present only in the replica folder in a cascade method
    try:
        for index in file_object.right_only:
            remove(index, replica)
    except FileNotFoundError as e:
        logging(str(e))


def logging(text):
    """This function take a string and write it to a file."""
    global log_path
    try:
        with open(log_path, "a", encoding="utf-8") as file:
            file.write(f"{text}\n")
        print(text)
    except PermissionError as e:
        new_text = f"{str(e)}\n + {text}"
        logging(new_text)


def valid_path(path):
    """Verifies if the directory exists on the machine"""
    if os.path.exists(path):
        if not os.path.isdir(path):
            path = valid_path(rf"{input('Introduce the path of a directory: ')}")
    else:
        path = valid_path(rf"{input('Introduce a valid path: ')}")
    return path


def start_program():
    # Defining directories path and synchronizing time interval.
    global time_interval, log_path

    source_path = valid_path(rf"{input('Introduce the source directory absolute path: ')}")
    replica_path = valid_path(rf"{input('Introduce the replica directory absolute path: ')}")
    log_path = valid_path(rf"{input('Introduce the log file absolute path: ')}")
    log_path = rf"{log_path}\log_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.txt"
    # Verifying if the directories are the same
    true_ = True
    while true_:
        if source_path == replica_path:
            print("Introduce different directories")
            replica_path = valid_path(rf"{input('Introduce the replica directory absolute path: ')}")
        else:
            true_ = False
    # Verifying if the interval is indeed an integer number
    is_true = True
    while is_true:
        try:
            time_interval = int(input("Introduce the interval time for synchronization in seconds: "))
        except ValueError:
            print("Introduce a valid response")
        else:
            is_true = False
    # Synchronizing directories
    while True:
        synchronize(source_path, replica_path)
        log = f"{datetime.datetime.now()}: Synchronization completed"
        logging(log)
        time.sleep(time_interval)


start_program()
