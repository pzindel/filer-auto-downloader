from urllib.request import urlopen
import pandas as pd


def webscrap_links(source_list):
    """
    Iterates through a list of provided filer.net folder URLs, scrapes the 
    respective HTML pages, extracts the file download links, and saves them 
    to a CSV file.
    
    Parameters:
        source_list (str): the filepath for a text file containing filer.net
            folder URLs (one per line).
        
    Returns:
        None
    """
    # Read URLs into list
    urls = []
    with open(source_list, "r") as file:
        urls = [line for line in file]

    # Create Pandas DataFrame to store and save CSV data
    dl_files = pd.DataFrame(columns=["filename", "url"])

    # Retrieve source HTML per URL and process
    for url in urls:
        source = str(urlopen(url).read())

        # Raise an error if there are two tables
        assert source.count("<tbody>") == 1

        # Select subset of source
        source = source[int(source.find("<tbody>")):int(source.find("</tbody>"))]

        # Split table per item (discard first bit)
        source = source.split("<tr>")[1:]

        # For each entry, strip and extract download url and name
        prefix = "https://filer.net"
        for item in source:
            # Extract download url
            dl_url = item[item.find("\"")+1:]
            dl_url = dl_url[:dl_url.find("\"")]
            dl_url = prefix + dl_url

            # Extract download file name
            name = item[item.find("\">")+2:]
            name = name[:name.find("</a>")]

            # Add link to Dat
            dl_files = dl_files.append({"filename": name, "url": dl_url}, ignore_index=True)

    # Save DataFrame to CSV file
    dl_files.to_csv("../data/file_links.csv", index=False)
    
    return
