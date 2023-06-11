"""This script takes a text file with RNA sequences and names and uses RNAComposer to generate pdb files for each sequence."""
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import concurrent.futures
import threading
import time
import pickle

WAIT_TIME = 600 # seconds to wait for processing
MAX_WORKERS = 2 # number of threads to use
PATH_TO_HERE = "\\".join(os.path.dirname(os.path.abspath(__file__)).split("\\")[:-1])
TEXTAREA_XPATH = "/html/body/table/tbody/tr[2]/td[2]/div/table/tbody/tr/td/div/table/tbody/tr/td/div/form/table/tbody/tr[4]/td/textarea"
SUBMIT_XPATH = "/html/body/table/tbody/tr[2]/td[2]/div/table/tbody/tr/td/div/table/tbody/tr/td/div/form/table/tbody/tr[7]/td/table/tbody/tr/td[1]/input"
DOWNLOAD_XPATH = "/html/body/table/tbody/tr[2]/td[2]/div/table/tbody/tr/td/div/table/tbody/tr/td/div/table/tbody/tr[4]/td/div/table/tbody/tr/td[1]/b/a"

def error_handler(i, message, driver):
    """Takes a screenshot of the error and saves it to the errorFiles directory."""
    if not os.path.exists(f"{PATH_TO_HERE}\\RNAComposer\\errorFiles"):
        os.mkdir(f"{PATH_TO_HERE}\\RNAComposer\\errorFiles")
    driver.save_screenshot(f"errorFiles\\{i}_{message}.png")

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
        driver.back()
    print(f"Thread {thread_name} finished")
    driver.quit()


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
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("log-level=3")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument('window-size=1500,2500')

    # read sequences from file
    name_directory = {}
    queue = []
    with open("GlnA sequences.txt", "r") as f:
        sequences = f.readlines()
        for i in range(0, len(sequences), 2):
            name = sequences[i].strip().split()[0].split("_")[0]
            name_directory[i] = name[1:]
            sequence = sequences[i + 1].strip()
            sequence = sequence.replace("T", "U")
            queue.append((sequence, i))
            if i >= 2:
                break
    # save name_directory
    with open("name_directory.pkl", "wb") as f:
        pickle.dump(name_directory, f)

    # download files in parallel
    pool = concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS)
    for i in range(MAX_WORKERS):
        pool.submit(download_pdb)
    pool.shutdown(wait=True)

    # rename files
    with open("name_directory.pkl", "rb") as f:
        name_directory = pickle.load(f)
    for file in os.listdir(f"{PATH_TO_HERE}\\pdbFiles"):
        if file.endswith(".pdb"):
            if (id := file.split(".")[0]).isdigit():
                file_name = name_directory.get(int(id))
            else:
                continue
            if file_name == None:
                print(f"Could not find name for {file}")
            else:
                try:
                    os.rename(f"{PATH_TO_HERE}\\pdbFiles\\{file}", f"{PATH_TO_HERE}\\pdbFiles\\{file_name}.pdb")
                except FileExistsError:
                    print(f"File {file_name}.pdb already exists")
                except Exception as e:
                    print(f"Error renaming {file}: {e}")

    seconds = time.time() - start
    minutes = seconds // 60
    seconds = seconds - minutes * 60
    hours = minutes // 60
    minutes = minutes - hours * 60
    print(f"Total time: {int(hours)}:{int(minutes)}:{seconds}")
