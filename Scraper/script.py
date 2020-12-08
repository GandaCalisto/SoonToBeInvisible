from selenium import webdriver
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import logging
from datetime import datetime

def main():
    t = time.time()
    default_url = "https://www.worldwildlife.org"
    basic_info = []
    animals = []
    logging.basicConfig(filename=f'log {str(datetime.now()).replace(":",".")}.log', format='%(asctime)s %(levelname)-8s %(message)s', level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S')
    print("Program Started")

    firefox_options = webdriver.FirefoxOptions()
    driver = webdriver.Firefox(options=firefox_options)
    driver.minimize_window()
    
    try:
        for i in range(1, 3, 1):
            print(f"Opening page number {i}")
            driver.get(f"{default_url}/species/directory?page={i}")
            tbody = driver.find_element_by_tag_name("tbody")
            print(f"Found the table")

            tr = tbody.find_elements_by_tag_name("tr")
            print("Created array with all rows")

            print("Starting to scrape basic information")
            for col in tr:
                first = True
                td = []
                for data in col.find_elements_by_tag_name("td"):
                    if first:
                        first = not first
                        td.append(data.find_element_by_tag_name("a").get_attribute('href'))
                    td.append(data.text)
                basic_info.append(td)
            print("Done scrapping basic information")

        print("Starting to scrape complete information about the animals")
        for row in basic_info:
            driver.get(row[0])
            content = driver.find_element_by_id("content")
            ul = content.find_elements_by_tag_name("ul")[1]
            ps = [content.find_elements_by_tag_name("p")[1], content.find_elements_by_tag_name("p")[2]]
            about = ul.find_elements_by_tag_name('li')
            photo_filter = "&filter=photos"

            Populacao, Altura, Peso, Tamanho, Habitats, Sobre, Localizacao, Photos = "","","","",[],"",[],[]

            try:
                Populacao = str(f"{str(about[1].find_elements_by_tag_name('div')[0].text)}")
            except Exception as ex:
                Populacao = "Unknown"
                logging.warning(f"Error getting population at animal -> {row[0]}")
                logging.warning(f"Error was -> {ex} ")

            try:
                Altura = str(f"{str(about[3].find_elements_by_tag_name('div')[0].text)}")
            except Exception as ex:
                Altura = "Unknown"
                logging.warning(f"Error getting height at animal -> {row[0]}")
                logging.warning(f"Error was -> {ex} ")

            try:
                Peso = str(f"{str(about[4].find_elements_by_tag_name('div')[0].text)}")
            except Exception as ex:
                Peso = "Unknown"
                logging.warning(f"Error getting weight at animal -> {row[0]} ")
                logging.warning(f"Error was -> {ex} ")

            try:
                Tamanho = str(f"{str(about[5].find_elements_by_tag_name('div')[0].text)}")
            except Exception as ex:
                Tamanho = "Unknown"
                logging.warning(f"Error getting size at animal -> {row[0]} ")
                logging.warning(f"Error was -> {ex} ")

            try:
                Habitats = str(f"{str(about[6].find_elements_by_tag_name('div')[0].text)}".split(","))
            except Exception as ex:
                Habitats = "Unknown"
                logging.warning(f"Error getting habitats at animal -> {row[0]} ")
                logging.warning(f"Error was -> {ex} ")

            try:
                Sobre = f"{str(ps[0].text)} \n {str(ps[1].text)}"
            except Exception as ex:
                Sobre = "Unknown"
                logging.warning(f"Error getting information about at animal -> {row[0]} ")
                logging.warning(f"Error was -> {ex} ")       

            try:
                Localizacao = f"{content.find_elements_by_class_name('list-data')[1].find_elements_by_class_name('lead')[0].text}".split(",")
            except Exception as ex:
                Localizacao = "Unknown"
                logging.warning(f"Error getting the location at animal -> {row[0]} ")
                logging.warning(f"Error was -> {ex}")   

            obj = {
                "Comum": f"{str(row[1])}",
                "Cientifico": f"{str(row[2])}",
                "Estado": f"{str(row[3])}",
                "Populacao": Populacao,
                "Altura": Altura,
                "Peso": Peso,
                "Tamanho": Tamanho,
                "Habitats": Habitats,
                "Sobre": Sobre,
                "Localizacao": Localizacao,
                "Photos": []
            }

            try:
                driver.get(str(content.find_elements_by_class_name("clearing")[0].find_elements_by_tag_name("a")[0].get_attribute("href")) + photo_filter)
                uls = driver.find_element_by_id("content").find_elements_by_class_name("wrapper")[1].find_elements_by_tag_name("ul")

                for li in uls:
                    for img in li.find_elements_by_tag_name("img"):
                        try:
                            obj["Photos"].append((str(img.get_attribute("src")).replace("featured_story", "story_full_width")))
                        except Exception as ex:
                            logging.warning(f"Error getting the photo at animal -> {row[0]} ")
                            logging.warning(f"Error was -> {ex}")
            except Exception as ex:
                logging.warning(f"Error {ex}")

            animals.append(obj)

            with open("animals.json", "w", encoding="utf-8") as f:
                json.dump(animals, f, indent=4)
                
            print("Added a new animal")

        print(f"Took {str(time.time() - t):0.2f} seconds to scrape all the information")
    except Exception as ex:
        print(f"Error {ex}")

if __name__ == "__main__":
    main()