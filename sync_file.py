import os
import filecmp
import shutil
import time
from loguru import logger
import sys

#logger
logger.remove(0)
logger_path = input("Please enter a path to logger: ")
logger.add(logger_path, format = "{level}| Message : {message}| @ {time}")
logger.add(lambda msg: print(msg, end=''))

#input variables
folder = input("Please input your source folder: ")
backup = input("Please input your replica folder: ")
input_time = input("Please input update time: ")

def are_dir_trees_equal(dir1, dir2):
    '''Function to compare two directory trees to check if their contents are equal.

    Params:
        dir1 (str): path to the first directory.
        dir2 (str): path to the second directory.

    Returns:
        bool: True if the directory trees are equal, False otherwise.'''
    # Compare the directory structures
    dirs_cmp = filecmp.dircmp(dir1, dir2)
    # Check directories present only in one tree
    if len(dirs_cmp.left_only)>0 or len(dirs_cmp.right_only)>0:
        return False
    # Compare files within the common directory
    (_, mismatch, errors) =  filecmp.cmpfiles(
        dir1, dir2, dirs_cmp.common_files, shallow=False)
    # Check for file mismatches or errors
    if len(mismatch)>0 or len(errors)>0:
        return False
    # Recursively compare common subdirectories
    for common_dir in dirs_cmp.common_dirs:
        new_dir1 = os.path.join(dir1, common_dir)
        new_dir2 = os.path.join(dir2, common_dir)
        if not are_dir_trees_equal(new_dir1, new_dir2):
            return False
    return True


def copy(file_list, src, dest):
    ''' This method copies a list of files from a source folder to a backup folder
     Params:
        file_list (list): List of files to copy.
        src (str): Path to the source folder.
        dest (str): Path to the destination folder.
    '''
    for f in file_list:
        #get the source path
        srcpath = os.path.join(src, os.path.basename(f))
        # Check if the file is a directory
        if os.path.isdir(srcpath):
            # Copy the directory and its contents recursively
            shutil.copytree(srcpath, os.path.join(dest, os.path.basename(f)))
        # Copy the file to the destination folder
        else:
            shutil.copy2(srcpath, dest)

def delete(file_list, src):
    ''' This method deletes a list of files from a source folder to a backup folder
    Args:
        file_list (list): List of files to delete.
        src (str): Path to the source folder.
    '''
    for f in file_list:
        # Get the source file path
        srcpath = os.path.join(src, os.path.basename(f))
        # Check if the file is a directory
        if os.path.isdir(srcpath):
            # Remove the directory and its contents recursively
            shutil.rmtree(srcpath)
        else:
            # Remove the file
            os.remove(srcpath)


def compare_directories(left, right):
    '''This method compares two directories and syncs them. If there is a common directory, the
    algorithm must compare what is inside of the directory by calling this recursively.
    Args:
        left (str): Path to the source directory.
        right (str): Path to the backup directory.'''
    comparison = filecmp.dircmp(left, right)
    # Recursively compare common subdirectories
    if comparison.common_dirs:
        for d in comparison.common_dirs:
            compare_directories(os.path.join(left, d), os.path.join(right, d))
    #copy directories or files if the are not in backup folder
    if comparison.left_only:
        file_list = comparison.left_only
        logger.info(", ".join([f"{file} was created" for file in file_list]))
        copy(file_list, left, right)
        logger.info(", ".join([f"{file} was copied" for file in file_list]))
     #modify the files to match content of the source folder
    if filecmp.dircmp(left, right).diff_files:
        file_list = filecmp.dircmp(left, right).diff_files
        copy(file_list, left, right)
        logger.info(", ".join([f"{file} was modified" for file in file_list]))
     #delete file from backup if this file is not in source folder
    if comparison.right_only:
        delete(comparison.right_only, right)
        logger.info(", ".join([f"{file} was deleted" for file in comparison.right_only]))


logger.info("Start")
while True:
    # check if folder is same with backup
    if are_dir_trees_equal(folder, backup):
        # sleep time
        time.sleep(int(input_time))
        continue
    #run the sync function
    compare_directories(folder, backup)




