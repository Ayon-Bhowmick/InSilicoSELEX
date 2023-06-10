"""This script takes a text file with RNA sequences and names and uses RNAComposer to generate pdb files for each sequence."""
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import concurrent.futures
import threading

WAIT_TIME = 600 # seconds to wait for processing
MAX_WORKERS = 30 # number of threads to use
PATH_TO_HERE = os.path.dirname(os.path.abspath(__file__))
TEXTAREA_XPATH = "/html/body/table/tbody/tr[2]/td[2]/div/table/tbody/tr/td/div/table/tbody/tr/td/div/form/table/tbody/tr[4]/td/textarea"
SUBMIT_XPATH = "/html/body/table/tbody/tr[2]/td[2]/div/table/tbody/tr/td/div/table/tbody/tr/td/div/form/table/tbody/tr[7]/td/table/tbody/tr/td[1]/input"
DOWNLOAD_XPATH = "/html/body/table/tbody/tr[2]/td[2]/div/table/tbody/tr/td/div/table/tbody/tr/td/div/table/tbody/tr[4]/td/div/table/tbody/tr/td[1]/b/a"

def download_pdb():
    thread_name = threading.current_thread().name
    # opens browser to RNAComposer
    driver = webdriver.Chrome(options=chrome_options)
    driver.get("https://rnacomposer.cs.put.poznan.pl/")
    while len(queue) > 0:
        sequence, i = queue.pop(0)
        driver.find_element("xpath", TEXTAREA_XPATH).clear()
        driver.find_element("xpath", TEXTAREA_XPATH).send_keys(f"#sequence number {i//2 + 1}\n>"+ str(i) + "\n" + sequence)
        driver.find_element("xpath", SUBMIT_XPATH).click()
        try:
            WebDriverWait(driver, WAIT_TIME).until(EC.presence_of_element_located(("xpath", DOWNLOAD_XPATH)))
            driver.find_element("xpath", DOWNLOAD_XPATH).click()
            print(f"Downloaded {i}.pdb for sequence #{i//2 + 1} in thread {thread_name}")
        except TimeoutException:
            print(f"Timed out for sequence #{i//2 + 1} in thread {thread_name}")
        except:
            print(f"Error for sequence #{i//2 + 1} in thread {thread_name}")
        driver.back()
    print(f"Thread {thread_name} finished")
    driver.quit()


if __name__ == "__main__":
    # makes directory for pdb files if it doesn't exist
    if not os.path.exists(f"{PATH_TO_HERE}\\pdbFiles"):
        os.mkdir(f"{PATH_TO_HERE}\\pdbFiles")
    # moves downloaded files to pdbFiles directory
    chrome_options = webdriver.ChromeOptions()
    prefs = {"download.default_directory" : f"{PATH_TO_HERE}\\pdbFiles"}
    chrome_options.add_experimental_option("prefs", prefs)
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("log-level=3")

    # read sequences from file
    name_directory = {}
    queue = []
    with open("GlnA sequences.txt", "r") as f:
        sequences = f.readlines()
        for i in range(0, len(sequences), 2):
            name = sequences[i].strip().split()[0].split("_")[0]
            name_directory[i] = name
            sequence = sequences[i + 1].strip()
            sequence = sequence.replace("T", "U")
            queue.append((sequence, i))

    # download files in parallel
    pool = concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS)
    for i in range(MAX_WORKERS):
        pool.submit(download_pdb)
    pool.shutdown(wait=True)

    # rename files
    for file in os.listdir(f"{PATH_TO_HERE}\\pdbFiles"):
        if file.endswith(".pdb"):
            os.rename(f"{PATH_TO_HERE}\\pdbFiles\\{file}", f"{PATH_TO_HERE}\\pdbFiles\\{name_directory[i.split('.')[0]]}.pdb")
