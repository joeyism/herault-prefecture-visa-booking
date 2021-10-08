import os
import time
import datetime
import argparse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import AutoChromedriver
import random

URL = "https://www.herault.gouv.fr/booking/create/27396/2"
ERROR_MSGS = ("502 Bad Gateway", "503 Service Unavailable", "504 Gateway Time-out")
WAIT_SECONDS = 3
BAD_GATEWAY_TIMEOUT = 30

if not os.path.exists("./chromedriver"):
    AutoChromedriver.download_chromedriver(version="79.0.3945.36") 

def is_element_exist_by_id(driver, id):
    try:
        WebDriverWait(driver, WAIT_SECONDS).until(EC.presence_of_element_located((By.ID, id)))
        return True
    except:
        return False

def check_bad_gateway(driver):
    url = driver.current_url
    same_page = True
    while any(err_msg in driver.page_source for err_msg in ERROR_MSGS):
        shortened_url = "/".join(driver.current_url.split("/")[-2:])
        print(f"\n\tRetrying {shortened_url} at {datetime.datetime.now()}\t", end="")
        time.sleep(BAD_GATEWAY_TIMEOUT)
        driver.refresh()
        if driver.current_url != url:
            same_page = False
    return driver, same_page

def check_availability(driver=None):
    print(f"Trying at {datetime.datetime.now()}\t", end="")
    availability =_check_availability(driver)
    print_availability(availability)

def _check_availability(driver=None):
    if driver is None:
        driver = _create_chrome_driver(headless=True)

    driver.get(URL)
    time.sleep(WAIT_SECONDS)

    driver, same_page = check_bad_gateway(driver)
    if not same_page:
        return False
    if is_element_exist_by_id(driver, "cookies-banner") and driver.find_element_by_id("cookies-banner").is_displayed():
        driver.execute_script("window.scrollTo(0, Math.ceil(document.body.scrollHeight*3/4));")
        driver.find_element_by_id("cookies-banner").find_element_by_class_name("boutons").find_elements_by_tag_name("a")[1].click()
        time.sleep(WAIT_SECONDS)

    driver, same_page = check_bad_gateway(driver)
    if not is_element_exist_by_id(driver, "condition_Booking"):
        print(driver.page_source)
        time.sleep(WAIT_SECONDS)
    driver.find_element_by_id("condition_Booking").find_element_by_tag_name("input").click()
    driver.find_element_by_id("submit_Booking").find_element_by_name("nextButton").click()
    time.sleep(WAIT_SECONDS)

    driver, same_page = check_bad_gateway(driver)
    if not same_page:
        return False
    if is_element_exist_by_id(driver, "fchoix_Booking"):
        url = driver.current_url
        i = 0
        while url == driver.current_url:
            driver, same_page = check_bad_gateway(driver)
            buttons = driver.find_element_by_id("fchoix_Booking").find_elements_by_tag_name("input")
            randint = random.randint(0, len(buttons)-1)
            button = buttons[randint]
            button.click()
            if not button.is_selected():
                driver.execute_script("arguments[0].checked = true;", button)
                print("*")
            submit_btn = driver.find_element_by_id("submit_Booking").find_element_by_name("nextButton")
            submit_btn.click()
            i += 1
            if i > 20:
                return False

    driver, same_page  = check_bad_gateway(driver)
    if not same_page:
        return False
    try:
        availability_text = driver.find_element_by_name("create").text
    except:
        import ipdb; ipdb.set_trace()
    availability =  "Il n'existe plus de plage horaire libre pour votre demande" not in availability_text and driver.current_url[-1] not in ('0', '1')
    return availability

def print_availability(availability):
    if availability:
        print("\n===================================================")
        print(f"\n>>> AVAILABILITY : {datetime.datetime.now()} <<<")
        print("===================================================")
        play_sound()
        import ipdb; ipdb.set_trace()
    else:
        print("FAILED")
    return availability

def play_sound():
    from pydub import AudioSegment
    from pydub.playback import play

    song = AudioSegment.from_wav("file_example_WAV_1MG.wav")
    play(song)

def _create_chrome_driver(headless=True):
    chrome_options = Options()
    if headless:
        chrome_options.add_argument("--headless")
    return webdriver.Chrome("./chromedriver", options=chrome_options)

def main(headless=True):
    parser = argparse.ArgumentParser(description="Upload HERE data")
    parser.add_argument('--show-chrome', help="Whether to show Chrome instead of being headless", action='store_true')
    args = parser.parse_args()

    while True:
        print("===== NEW START =====")
        headless = not args.show_chrome
        CHROME_DRIVER = _create_chrome_driver(headless=headless)
        try:
            while not check_availability(driver=CHROME_DRIVER):
                time.sleep(WAIT_SECONDS)

            while True:
                play_sound()
        except Exception as e:
            CHROME_DRIVER.close()
            print(e)
        finally:
            CHROME_DRIVER.close()



if __name__ == "__main__":
    main()
