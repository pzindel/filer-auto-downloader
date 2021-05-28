import argparse
import configparser
from os.path import exists
from source_aggregator.source_aggregator import webscrap_links
from file_downloader.file_downloader import downloader


def load_settings():
    """
    Loads program settings from files using configparser. If the files are not
    found, settings are loaded using defaults.
    
    Parameters:
        None
        
    Returns:
        creds (ConfigParser): an object storing the user credentials
        config (ConfigParser): an object storing program settings
    """
    creds = configparser.ConfigParser()
    config = configparser.ConfigParser()
    
    try:
        creds.read("credentials.ini")
    except:
        creds["LoginDetails"] = {"Username": "",
                                    "Password": ""}
    
    try:
        config.read("config.ini")
    except:
        config["Configuration"] = {"DownloadDirectory": "../downloads",
                                   "LoginPageURL": "https://filer.net/login",
                                   "SourceFoldersURLs": "../data/source_list.txt",
                                   "FilesURLs": "../file_links.csv",
                                   "Verbose": True,
                                   "ForceURLsReload": False}

    return creds,config


def parse_flags(creds, config):
    """
    Parses the CLI flags entered during execution and updates the program
    settings accordingly.
    
    Parameters:
        creds (ConfigParser): an object with user credentials
        config (ConfigParser): an object with program settings
        
    Returns:
        creds (ConfigParser): an object with user credentials
        config (ConfigParser): an object with program settings
        save (dict): a dictionary with the save options
    """
    # Parse flags
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", 
                        "--username", 
                        help="Your username for filer.net"
                        type=str)
    parser.add_argument("-p",
                        "--password",
                        help="Your password for filer.net"
                        type=str)
    parser.add_argument("--save-credentials",
                        help="Store the username/password for future use",
                        default=False,
                        type=bool)
    parser.add_argument("--save-config",
                        help="Store the configuration settings for future use",
                        default=True,
                        type=bool)
    parser.add_argument("-d",
                        "--dl-dir",
                        help="The destination directory for downloads"
                        type=str)
    parser.add_argument("--force-reload",
                        help="Will force the program to reload the list of \
                        files stored in the cached file_links.csv"
                        type=bool)
    parser.add_argument("-v",
                        "--verbose",
                        help="Have the program output while running"
                        type=bool)
    args = parser.parse_args()

    # Encoding between flags and ConfigParser keys
    key = {"username": "Username",
           "password": "Password",
           "dl-dir": "DownloadDirectory",
           "force-reload": "ForceURLsReload",
           "verbose": "Verbose"}

    # Overwrite new settings
    for flag,value in vars(args).iteritems():
        if (value is not None) and (flag in vars(args).keys()):
            if (flag in ["username", "password"]):
                creds["LoginDetails"][key[flag]] = value
            else:
                config["Configuration"][key[flag]] = value

    return creds,config,{"save-creds": args.save_credentials,
                         "save-config": args.save_config}
    

def store_settings(creds, config, save):
    """
    Writes the settings to respective files based on the save options.

    Parameters:
        creds (ConfigParser): an object with user credentials
        config (ConfigParser): an object with program settings
        save (dict): a dictionary with the save options
    Returns:
        None
    """
    if save["save-creds"]:
        with open("credentials.ini", "w") as file:
            creds.write(file)
        
    if save["save-config"]:
        with open("config.ini", "w") as file:
            config.write(file)

    return
    

if (__name__ == __main__):
    # Load credentials and settings from files
    creds,config = load_settings()
    
    # Use CLI flags to overwrite settings
    creds,config,save = parse_flags(creds, config)
    
    # Save the settings to files
    store_settings(creds, config, save)
    
    # Run the webscraping module
    if (not exists(config["Configuration"]["FilesURLs"])) \
        or (config["Configuration"]["ForceURLsReload"]):
        webscrap_links(config["Configuration"]["SourceFoldersURLs"])
    
    # Test for required variables
    assert (args.username != ""), "No username provided to store."
    assert (args.password != ""), "No password provided to store."
    
    # Run auto downloader module
    downloader(config["Configuration"]["FilesURLs"],
               config["Configuration"]["DownloadDirectory"],
               config["Configuration"]["DownloadDirectory"],
               config["Configuration"]["Verbose"]
               creds["LoginDetails"]["Username"],
               creds["LoginDetails"]["Password"])