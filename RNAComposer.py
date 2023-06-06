"""This script takes a text file with RNA sequences and names and uses RNAComposer to generate pdb files for each sequence."""
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os

WAIT_TIME = 60 # seconds to wait for processing
PATH_TO_HERE = os.path.dirname(os.path.abspath(__file__))
TEXTAREA_XPATH = "/html/body/table/tbody/tr[2]/td[2]/div/table/tbody/tr/td/div/table/tbody/tr/td/div/form/table/tbody/tr[4]/td/textarea"
SUBMIT_XPATH = "/html/body/table/tbody/tr[2]/td[2]/div/table/tbody/tr/td/div/table/tbody/tr/td/div/form/table/tbody/tr[7]/td/table/tbody/tr/td[1]/input"
DOWNLOAD_XPATH = "/html/body/table/tbody/tr[2]/td[2]/div/table/tbody/tr/td/div/table/tbody/tr/td/div/table/tbody/tr[4]/td/div/table/tbody/tr/td[1]/b/a"

# makes directory for pdb files if it doesn't exist
if not os.path.exists(f"{PATH_TO_HERE}\\pdbFiles"):
    os.mkdir(f"{PATH_TO_HERE}\\pdbFiles")
# moves downloaded files to pdbFiles directory
chrome_options = webdriver.ChromeOptions()
prefs = {"download.default_directory" : f"{PATH_TO_HERE}\\pdbFiles"}
chrome_options.add_experimental_option("prefs", prefs)
chrome_options.add_argument("--headless")
# opens browser to RNAComposer
driver = webdriver.Chrome(options=chrome_options)
driver.get("https://rnacomposer.cs.put.poznan.pl/")
print(f"Path to here: {PATH_TO_HERE}\n")

with open("GlnA sequences.txt", "r") as f:
    sequences = f.readlines()
    for i in range(0, len(sequences), 2):
        name = sequences[i].strip().split()[0].split("_")[0]
        sequence = sequences[i + 1].strip()
        sequence = sequence.replace("T", "U")
        driver.find_element("xpath", TEXTAREA_XPATH).clear()
        driver.find_element("xpath", TEXTAREA_XPATH).send_keys(f"#sequence number {i//2 + 1}\n" + name + "\n" + sequence)
        driver.find_element("xpath", SUBMIT_XPATH).click()
        try:
            WebDriverWait(driver, WAIT_TIME).until(EC.presence_of_element_located(("xpath", DOWNLOAD_XPATH)))
            driver.find_element("xpath", DOWNLOAD_XPATH).click()
            print(f"Downloaded {name}.pdb for sequence #{i//2 + 1}")
        except TimeoutException:
            print(f"Timed out for sequence #{i//2 + 1}")
        except:
            print(f"Error for sequence #{i//2 + 1}")
        driver.back()
