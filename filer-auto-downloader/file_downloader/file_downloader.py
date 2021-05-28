from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import pandas as pd
from time import sleep, time
from glob import glob
from datetime import datetime


def downloader(dl_links_fp, dl_dir_path, login_url, verbose, user, passw):
    """
    Uses Selenium to log in to a filer.net profile and download the files
    listed in the dl_links CSV file.
    
    Parameters:
        dl_links_fp (str): the filepath for a CSV file containing the file
            download links
        dl_dir_path (str): the directory path for where to store the downloaded
            files
        login_url (str): the login page URL for filer.net
        verbose (bool): the option to output logs while running
        user (str): the username for filer.net
        passw (str): the password for filer.net
        
    Returns:
        None
    """
    # Open dl_links
    dl_links = pd.read_csv(dl_links_fp)

    # Set Chrome download folder
    chrome_opts = Options()
    chrome_opts.add_argument("--log-level=OFF")
    chrome_opts.add_experimental_option("prefs",
        {"download.default_directory": dl_dir_path,
         "download.prompt_for_download": False,
         "download.directory_upgrade": True})

    # Start webdriver
    driver = webdriver.Chrome(options=chrome_opts)
    driver.set_page_load_timeout(10)

    # Open filer.net login page
    driver.get(login_url)
    sleep(3)

    # Log in
    username = driver.find_element_by_id("username")
    username.send_keys(user)
    password = driver.find_element_by_id("password")
    password.send_keys(passw)
    login = driver.find_element_by_id("_submit")
    login.click()
    sleep(3)

    # Get list of already downloaded files to avoid duplicates
    downloaded = glob(dl_dir_path + "\\*")
    downloaded = [i.split("\\")[-1] for i in downloaded]

    print("Starting downloads...")
    skipped_count = 0
    batch_count = 0
    file_dl_count = 0
    start_time = time()

    # Iterate dl_links and download files in batches of 10
    for i,entry in dl_links.iterrows():
        # Skip downloaded files
        if (entry.filename in downloaded):
            if verbose: print("Item {:03d} skipped.".format(i))
            skipped_count += 1
            continue
        
        # Wait 3 seconds between each file
        sleep(3)
        
        # Start download
        while True:
            try:
                driver.get(entry.url)
                break
            except:
                driver.refresh()

        if verbose: print("Item {:03d} downloading...".format(i))
        file_dl_count += 1
        
        # Wait 5 minutes between batches
        if (i % 10 == 0):
            batch_count += 1
            if verbose: 
                print("Pausing at {} for 3 minutes to download batch {}".format(
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"), batch_count))
            sleep(180)

    # Print final outputs & close program
    if verbose:
        print("Downloads compeleted at {}".format(
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        print("""Report:
            Files skipped: {}
            Batches processed: {}
            Files downloaded: {}
            Time to downloade: {:.2f} minutes\n""".format(skipped_count,
                                                batch_count,
                                                file_dl_count,
                                                time()/60 - start_time/60))

    sleep(300)
    if verbose: print("Shutting down...")
    driver.close()
    
    return