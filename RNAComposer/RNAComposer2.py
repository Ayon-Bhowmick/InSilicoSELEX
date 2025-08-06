"""This script takes a text file with RNA sequences and names and uses RNAComposer to generate pdb files for each sequence."""
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import concurrent.futures
import threading
from hashlib import sha256
import time
from tqdm import tqdm

WAIT_TIME = 600 # seconds to wait for processing
MAX_WORKERS = 1 # number of threads to use
PATH_TO_HERE = "\\".join(os.path.dirname(os.path.abspath(__file__)).split("\\")[:-1])
TEXTAREA_XPATH = "/html/body/table/tbody/tr[2]/td[2]/div/table/tbody/tr/td/div/table/tbody/tr/td/div/form/table/tbody/tr[4]/td/textarea"
SUBMIT_XPATH = "/html/body/table/tbody/tr[2]/td[2]/div/table/tbody/tr/td/div/table/tbody/tr/td/div/form/table/tbody/tr[7]/td/table/tbody/tr/td[1]/input"
DOWNLOAD_XPATH = "/html/body/table/tbody/tr[2]/td[2]/div/table/tbody/tr/td/div/table/tbody/tr/td/div/table/tbody/tr[4]/td/div/table/tbody/tr/td[1]/b/a"
queue = []

def download_pdb():
    """Downloads pdb files from RNAComposer."""
    thread_name = threading.current_thread().name
    # opens browser to RNAComposer
    print(f"Thread {thread_name} started")
    driver = webdriver.Chrome(options=chrome_options)
    driver.get("https://rnacomposer.cs.put.poznan.pl/")
    while len(queue) > 0:
        sequence, i = queue.pop(0)
        driver.find_element("xpath", TEXTAREA_XPATH).clear()
        driver.find_element("xpath", TEXTAREA_XPATH).send_keys(f"#sequence number {i}\n>{i}\n{sequence}")
        driver.find_element("xpath", SUBMIT_XPATH).click()
        try:
            WebDriverWait(driver, WAIT_TIME).until(EC.presence_of_element_located(("xpath", DOWNLOAD_XPATH)))
            driver.find_element("xpath", DOWNLOAD_XPATH).click()
            # check if file downloaded
            while True:
                if f"{i}.pdb" in os.listdir(f"{PATH_TO_HERE}\\pdbFiles"):
                    break
            print(f"Downloaded {i}.pdb for sequence #{i//2 + 1} in thread {thread_name}")
        except TimeoutException:
            print(f"Timed out for sequence #{i} in thread {thread_name}")
            error_handler(i, "timeout", driver)
        except Exception as e:
            print(f"Error for sequence #{i} in thread {thread_name}: {e}")
            error_handler(i, "error", driver)
        bar.update(1)
        driver.back()
    print(f"Thread {thread_name} finished")
    driver.quit()

def error_handler(i, message, driver):
    """Takes a screenshot of the error and saves it to the errorFiles directory."""
    if not os.path.exists(f"{PATH_TO_HERE}\\RNAComposer\\errorFiles"):
        os.mkdir(f"{PATH_TO_HERE}\\RNAComposer\\errorFiles")
    driver.save_screenshot(f"errorFiles\\{i}_{message}.png")

if __name__ == "__main__":
    start = time.time()
    # makes directory for pdb files if it doesn't exist
    if not os.path.exists(f"{PATH_TO_HERE}\\pdbFiles"):
        os.mkdir(f"{PATH_TO_HERE}\\pdbFiles")
    # moves downloaded files to pdbFiles directory
    chrome_options = webdriver.ChromeOptions()
    prefs = {"download.default_directory" : f"{PATH_TO_HERE}\\pdbFiles",
                            "savefile.default_directory": f"{PATH_TO_HERE}\\RNAComposer\\errorFiles"}
    chrome_options.add_experimental_option("prefs", prefs)
    # chrome_options.add_argument("--headless")
    chrome_options.add_argument("log-level=3")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument('window-size=1500,2500')
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])

    # read sequences from file
    name_directory = {}
    queue = []
    with open(f"{PATH_TO_HERE}\\RNAComposer\\GlnA sequences.txt", "r") as f:
        sequences = f.readlines()
        for i in range(0, len(sequences), 2):
            name = sha256(sequences[i].strip().encode('utf-8')).hexdigest()
            name_directory[i] = name
            sequence = sequences[i + 1].strip()
            sequence = sequence.replace("T", "U")
            queue.append((sequence, name))
            print(sequence)

    # save name_directory
    with open(f"{PATH_TO_HERE}\\RNAComposer\\name_directory.csv", "w") as f:
        for key, value in name_directory.items():
            f.write(f"{key},{value}\n")

    # download files in parallel
    with tqdm(total=len(queue)) as bar:
        with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
            futures = [pool.submit(download_pdb) for _ in range(MAX_WORKERS)]

    seconds = time.time() - start
    minutes = seconds // 60
    seconds = seconds - minutes * 60
    hours = minutes // 60
    minutes = minutes - hours * 60
    print(f"Total time: {int(hours)}:{int(minutes)}:{seconds}")
