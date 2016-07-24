import os
from hashlib import sha1
import pickle
import re


def data_file_name(filename, data_dirs=None):
    """Returns filename if a file exists. Also checks data_dirs for the file."""
    if os.path.exists(filename):
        return filename
    if data_dirs is not None:
        return find_file_in_folders(filename, data_dirs)
    return FileNotFoundError(filename)


def find_file_in_folders(filename, folders):
    """Searches for filename in folders, then return full path or raise FileNotFoundError
    Does not recurse into subdirectories
    """
    for folder in folders:
        full_path = os.path.join(folder, filename)
        if os.path.exists(full_path):
            return full_path
    raise FileNotFoundError(filename)


def load_pickle(filename, data_dirs=None):
    """Loads a pickle from filename"""
    with open(data_file_name(filename, data_dirs), mode='rb') as infile:
        return pickle.load(infile)


def save_pickle(stuff, filename):
    """Saves stuff in a pickle at filename"""
    with open(filename, mode='wb') as outfile:
        pickle.dump(stuff, outfile)


def hashablize(obj):
    """Convert a container hierarchy into one that can be hashed.
    See http://stackoverflow.com/questions/985294
    """
    try:
        hash(obj)
    except TypeError:
        if isinstance(obj, dict):
            return tuple((k, hashablize(v)) for (k, v) in sorted(obj.items()))
        elif hasattr(obj, '__iter__'):
            return tuple(hashablize(o) for o in obj)
        else:
            raise TypeError("Can't hashablize object of type %r" % type(obj))
    else:
        return obj


def deterministic_hash(thing):
    """Return a deterministic hash of a container hierarchy using hashablize, pickle and sha1"""
    return sha1(pickle.dumps(hashablize(thing))).hexdigest()


def process_files_in_config(config, data_dirs):
    """Replaces file name values in dictionary config with their files.
    Modifies config in-place
    """
    for k, v in config.items():
        if isinstance(v, str):
            _, ext = os.path.splitext(v)
            if ext == '.pkl':
                config[k] = load_pickle(v, data_dirs)
            # Add support for other formats here
