import os
import random
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager


from dotenv import load_dotenv
#from bs4 import BeautifulSoup

load_dotenv()

username = os.getenv("INSTAGRAM_USERNAME")
password = os.getenv("INSTAGRAM_PASSWORD")

if not username or not password:
    raise ValueError("As variáveis de ambiente INSTAGRAM_USERNAME e INSTAGRAM_PASSWORD não estão definidas.")

def is_element_present(driver, xpath):
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, xpath))
        )
        return True
    except:
        return False
    
def type_like_a_human(element, text):
    for char in text:
        element.send_keys(char)
        time.sleep(random.uniform(0.01, 0.5)) 

def check_login_errors(driver):
    if is_element_present(driver, "//p[contains(text(), 'senha incorreta')]"):
        print("Erro de login: Senha incorreta.")
        return False
    elif is_element_present(driver, "//p[contains(text(), 'não corresponde a uma conta')]"):
        print("Erro de login: Nome de usuário inválido.")
        return False
    
    if is_element_present(driver, "//*[contains(@href, '/explore/')]"):
        return True
    
    print("Erro desconhecido durante o login.")
    return False

def click_not_now(driver):
    try:
        not_now_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//*[text()='Agora não']"))
        )
        not_now_button.click()
    except Exception as e:
        print(f"'Agora não' não foi encontrado: {e}")
        time.sleep(2)
        

def login(driver, username, password):
    driver.get("https://www.instagram.com/accounts/login/")
    
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.NAME, "username"))
    )
    username_input = driver.find_element(By.NAME, "username")
    password_input = driver.find_element(By.NAME, "password")
    
    type_like_a_human(username_input, username)
    type_like_a_human(password_input, password)
    
    password_input.send_keys("\n")

    if not check_login_errors(driver):
        print("Erro durante o login, verifique as credenciais.")
        return False
    else:
        click_not_now(driver)
        return True
    
def click_search_icon(driver):
        path = "body > div > div > div > div:nth-child(2) > div > div > div:first-child > div:first-child > div:nth-child(2) > div > div > div > div > div > div:nth-child(2)"
        search_container = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, path))
        )
        print(search_container)
        
        if search_container: 
            search_container.click()
            time.sleep(2)


def type_in_search_field(driver, search_text):
        search_field = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Pesquisar']"))
        )
        
        type_like_a_human(search_field, search_text)
        time.sleep(2)       
        

def click_first_search_result(driver):
    try:
        first_result = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, '/napucminas/')]"))
        )
        first_result.click()
        
    except Exception as e:
        print(f"Erro ao tentar clicar no primeiro resultado: {e}")

def get_post_details(driver):
    try:
        wait = WebDriverWait(driver, 10)
        
        container = driver.find_element(By.CSS_SELECTOR, "article[role=presentation]")
        
        user_element = container.find_element(By.CSS_SELECTOR, "header a")
        username = user_element.text
        
        post_body = container.find_element(By.CSS_SELECTOR, "& > div > div:nth-child(2) > div > div> div:nth-child(2)")

        comments_body = post_body.find_element(By.CSS_SELECTOR, "& ul")
        
        description_element = comments_body.find_element(By.CSS_SELECTOR, "h1")
        
        description = description_element.get_attribute("innerText")

        date_element = wait.until(EC.presence_of_element_located((By.XPATH, "//time")))
        datetime_str = date_element.get_attribute("datetime")
        
        post_datetime = datetime.fromisoformat(datetime_str.replace("Z", "+00:00"))

        is_video = False
        try:
            video_element = driver.find_element(By.CSS_SELECTOR, "video")
            is_video = True
        except:
            pass

        post_type = "Vídeo" if is_video else "Foto"

        print(f"Nome de usuário que realizou postagem: {username}")
        print(f"Descrição do post: {description}")
        print(f"Data e Hora da postagem: {post_datetime.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Tipo de postagem: {post_type}\n")

    except Exception as e:
        print("Erro ao coletar dados do post:", e)
        
def get_likes(driver):
    try:        
        likes_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//section//span[contains(text(), 'curtidas') or contains(text(), 'likes')]/span"))
        )
        likes_text = likes_element.text.replace(',', '').replace('.', '')
        
        if 'K' in likes_text:
            likes = int(float(likes_text.replace('K', '')) * 1000)
        elif 'M' in likes_text:
            likes = int(float(likes_text.replace('M', '')) * 1000000)
        else:
            likes = int(likes_text)
            
        print(f"Número total de curtidas: {likes}")
        return likes
    except Exception as e:
        print(f"Erro ao coletar curtidas: {e}\n")
        return 0

def open_likers_list(driver):
    try:
        likers_button = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, "//section//span[contains(text(), 'curtidas') or contains(text(), 'likes')]/span"))
        )
        driver.execute_script("arguments[0].click();", likers_button)

        WebDriverWait(driver, 40).until(
            EC.visibility_of_element_located((By.XPATH, "//div[@role='heading'][contains(text(), 'Curtidas') or contains(text(), 'Likes')]"))
        )
    except Exception as e:
        print(f"Erro ao abrir a lista de curtidores: {e}")

        
def collect_likers(driver, max_scrolls=10):
    open_likers_list(driver)
    
    scroll_top = 0
    like_list = set()
    error_count = 0
    
    for scroll_count in range(max_scrolls):
        # Acha titulo com "Curtidas"
        if error_count > 5:
            print("Erro ao coletar curtidores.")
            break
        
        try:
            likes_div = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.XPATH, "//div[@role='heading'][contains(text(), 'Curtidas') or contains(text(), 'Likes')]"))
            )
            # Acha o container do dialog
            likes_container = likes_div.find_element(By.XPATH, "../../../../..")
            likes_list_element = likes_container.find_element(By.CSS_SELECTOR, "& > div:nth-child(2) > div")
            list_item_heigth = likes_list_element.find_element(By.CSS_SELECTOR, "& > div > div").size['height']
        except TimeoutException:
            print("Erro: 'Curtidas' não encontrado.")
            open_likers_list(driver)
            scroll_count = 0
            like_list.clear()
            scroll_top = 0
            error_count += 1
            time.sleep(1)
            continue
            
        try:
            current_likes_list = likes_list_element.find_elements(By.CSS_SELECTOR, "& > div > div span>div>a span")
            if len(current_likes_list) != 0:
                for liker in current_likes_list:
                    like_list.add(liker.text.strip())
                
                scroll_top += list_item_heigth * len(current_likes_list)
                driver.execute_script("arguments[0].scrollTop = arguments[1];", likes_list_element, scroll_top)
            
            time.sleep(1)
        except Exception as e:
            print(e)
            break
        
    return like_list

def collect_comments(driver):
    try:
        comments_container = driver.find_element(By.CSS_SELECTOR, "article[role=presentation] > div > div:nth-child(2) > div > div> div:nth-child(2) > div > ul > div:last-child > div > div")
        
        comments = []

        comment_elements = comments_container.find_elements(By.CSS_SELECTOR, "& > div > ul > div h3 a[role=link]")

        for comment_element in comment_elements:
            try:
                user_name = comment_element.text.strip()
                if user_name:
                    comments.append(user_name)
            except Exception as e:
                print(f"Erro ao processar comentário: {e}")
        
        comments = list(set(comments))
        
        print(f"\nUsuários que comentaram coletados: {comments}")
        return comments
    except Exception as e:
        print(f"Erro ao coletar comentários: {e}")
    return []

def scroll_like_human_page(driver, scroll_pause_time=2, max_scrolls=10):
    last_height = driver.execute_script("return document.body.scrollHeight")
    
    for _ in range(max_scrolls):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        
        time.sleep(scroll_pause_time + random.uniform(0, 2))
        
        new_height = driver.execute_script("return document.body.scrollHeight")
        
        if new_height == last_height:
            break
        
        last_height = new_height
        
def exit(driver):
    try:
        actions = ActionChains(driver)
        actions.send_keys(Keys.ESCAPE).perform()
        time.sleep(1)
    except Exception as e:
        print(f"Erro ao sair do post: {e}")

 
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

if login(driver, username, password):
    print("Login realizado com sucesso!")

click_search_icon(driver)

search_text = "napucminas"
type_in_search_field(driver, search_text)
    
click_first_search_result(driver)
time.sleep(1)


elements = WebDriverWait(driver, 10).until(
    EC.presence_of_all_elements_located((By.CSS_SELECTOR, "main > div > div:nth-child(3) a"))
) 

print(elements)

for index in range(len(elements)):
    time.sleep(1)
    print(f"Clicando no post {index + 1} de {len(elements)}")
    elements[index].click()
    time.sleep(2)
    
    print(f"Coletando dados do post {index + 1}...")
    get_post_details(driver)
    time.sleep(2)
            
    get_likes(driver)
    time.sleep(1)

    open_likers_list(driver)
    time.sleep(2)
    likers = collect_likers(driver, max_scrolls=5)
    print(f"\nUsuários que curtiram coletados: {likers}")
    time.sleep(1)

    collect_comments(driver)
    time.sleep(2)
            
    driver.back()
    time.sleep(2)