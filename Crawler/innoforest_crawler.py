import os
import json
import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

class InnoForestCrawler:
    def __init__(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.dataset_dir = os.path.join(base_dir, 'Dataset')
        os.makedirs(self.dataset_dir, exist_ok=True)

        self.output_file = os.path.join(self.dataset_dir, 'inno_company.json')
        self.error_log_file = os.path.join(self.dataset_dir, 'error_log.json')
        self.result = []
        self.error_list = []
        if os.path.exists(self.output_file):
            with open(self.output_file, 'r', encoding='utf-8') as f:
                content = f.read()
                self.existing_urls = set([comp["url"] for comp in json.loads(content)]) if content.strip() else set()
        else:
            self.existing_urls = set()

        chrome_driver_path = r"C:\Users\kimhy\chromedriver-win64\chromedriver.exe"
        service = Service(executable_path=chrome_driver_path)

        options = Options()
        options.add_argument(r"user-data-dir=C:\Users\kimhy\AppData\Local\Google\Chrome\User Data")
        options.add_argument("profile-directory=Profile 3")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)

        self.driver = webdriver.Chrome(service=service, options=options)
        print("🚀 크롬 세션 로딩 완료 (로그인 유지)")

    def random_sleep(self, a=0.5, b=1.5):
        time.sleep(random.uniform(a, b))

    def get_dd(self, label):
        self.random_sleep()
        try:
            dt_elem = self.driver.find_element(By.XPATH, f"//dt[contains(text(), '{label}')]")
            dd_elem = dt_elem.find_element(By.XPATH, "following-sibling::dd[1]")
            text = dd_elem.text.strip()
            return text if text != "-" and text else None
        except:
            return None

    def parse_major_info(self):
        self.random_sleep()
        info = {}
        try:
            keys_to_get = ["자본금", "고용인원", "누적투자유치금액", "투자유치건수", "연매출", "기술등급"]
            blocks = self.driver.find_elements(By.CSS_SELECTOR, "div.css-1s5aaxq > dl > div")
            for block in blocks:
                key = block.find_element(By.CSS_SELECTOR, "dt").text.strip()
                if key in keys_to_get:
                    val = block.find_element(By.CSS_SELECTOR, "dd").text.strip()
                    info[key] = val if val != "-" and val else None
        except:
            pass
        return info

    def parse_table(self, label):
        self.random_sleep()
        data = {}
        try:
            bars = self.driver.find_elements(By.CSS_SELECTOR, f"div#{label}Chart g[aria-label]")
            for bar in bars:
                aria = bar.get_attribute("aria-label")
                parts = aria.split()
                if len(parts) >= 3:
                    item, year, value = parts[0], parts[1], parts[2]
                    data.setdefault(item, {})[year] = value
        except:
            pass
        return data

    def parse_news(self):
        self.random_sleep()
        news = []
        try:
            news_list = self.driver.find_elements(By.CSS_SELECTOR, "ul.css-1nx5s0 li")
            for n in news_list:
                try:
                    link = n.find_element(By.TAG_NAME, "a").get_attribute("href")
                    title = n.find_element(By.TAG_NAME, "dt").text.strip()
                    date = n.find_element(By.TAG_NAME, "dd").text.strip()
                    news.append({"링크": link, "제목": title, "날짜": date})
                except:
                    continue
        except:
            pass
        return news

    def parse_patents(self):
        self.random_sleep()
        patents = []
        try:
            items = self.driver.find_elements(By.CSS_SELECTOR, "ul.css-tgpw9p > li")
            for item in items:
                try:
                    title = item.find_element(By.TAG_NAME, "dt").text.split("{")[0].strip()
                    patents.append(title)
                except:
                    continue
        except:
            pass
        return patents
    
    def parse_investment(self):
        invest_info = {
        "최종투자단계": None,
        "누적투자유치금액": None,
        "투자유치건수": None,
        "투자유치이력": []
    }
        try:
            invest_info["최종투자단계"] = self.get_dd("최종투자단계")
            invest_info["누적투자유치금액"] = self.get_dd("누적투자유치금액")
            invest_info["투자유치건수"] = self.get_dd("투자유치건수")
            rows = self.driver.find_elements(By.CSS_SELECTOR, "div.css-1ipakji table tr")[1:]
            for row in rows:
                cells = row.find_elements(By.TAG_NAME, "td")
                if len(cells) >= 3:
                    date = cells[0].text.strip()
                    stage = cells[1].text.strip()
                    amount = cells[2].text.strip()
                    invest_info["투자유치이력"].append({"날짜": date, "단계": stage, "금액": amount})
        except:
            pass
        return invest_info


    def parse_categories(self):
        self.random_sleep()
        categories = []
        try:
            cats = self.driver.find_elements(By.CSS_SELECTOR, "div.css-k0zb2y > span")
            for cat in cats[:4]:
                text = cat.text.split('\n')[0].strip()
                categories.append(text)
        except:
            pass
        return categories

    def crawl(self, url):
        try:
            # URL 중복 검사
            if url in self.existing_urls:
                print(f"⏩ 이미 수집된 기업, 스킵")
                return

            print(f"🔗 {url} 크롤링 시작")
            self.driver.get(url)
            time.sleep(random.uniform(3,4))  # 로딩 대기

            company_name = self.driver.find_element(By.CSS_SELECTOR, "div.css-gmlt1i h1 span").text.strip()
            company_intro = self.get_dd("기업소개")
            listed = self.get_dd("상장여부")
            established = self.get_dd("설립일자")

            homepage = None
            try:
                homepage_elem = self.driver.find_element(By.XPATH, "//dt[contains(text(),'홈페이지')]/following-sibling::dd[1]//a")
                homepage = homepage_elem.get_attribute("href")
            except:
                pass

            address_full = self.get_dd("주소")
            address = " ".join(address_full.split()[:2]) if address_full else None

            major_info = self.parse_major_info()
            profit_data = self.parse_table("profit")
            finance_data = self.parse_table("finance")
            news = self.parse_news()
            patents = self.parse_patents()
            categories = self.parse_categories()
            invest_data = self.parse_investment()

            data = {
                "url": url,
                "기업명": company_name,
                "기업소개": company_intro,
                "상장여부": listed,
                "설립일": established,
                "홈페이지": homepage,
                "주소": address,
                "카테고리": categories,
                "주요정보": major_info,
                "투자유치정보": invest_data,
                "손익": profit_data,
                "재무": finance_data,
                "보도자료": news,
                "특허명칭리스트": ", ".join(patents) if patents else None
            }

            self.result.append(data)
            self.existing_urls.add(url)   # ⭐️ 여기 중요
            self.save()
            self.result.clear()
            print(f"✅ {company_name} 수집 완료")

        except Exception as e:
            print(f"⚠ {url} 오류 발생 → {e}")
            self.error_list.append({"url": url, "error": str(e)})

    def save(self):
        if os.path.exists(self.output_file):
            with open(self.output_file, 'r', encoding='utf-8') as f:
                content = f.read()
                existing = json.loads(content) if content.strip() else []
                self.existing_urls = set([comp["url"] for comp in existing])
        else:
            existing = []

        existing.extend(self.result)

        with open(self.output_file, 'w', encoding='utf-8') as f:
            json.dump(existing, f, ensure_ascii=False, indent=4)
        print(f"💾 저장 완료: {self.output_file}")

        if self.error_list:
            with open(self.error_log_file, 'w', encoding='utf-8') as f:
                json.dump(self.error_list, f, ensure_ascii=False, indent=4)
            print(f"⚠ 에러 로그 기록됨: {self.error_log_file}")

    def close(self):
        self.driver.quit()

if __name__ == "__main__":
    crawler = InnoForestCrawler()

    with open("listing.txt", "r", encoding="utf-8") as f:
        urls = [line.strip() for line in f if line.strip()]

    for idx, url in enumerate(urls, 1):
        print(f"🚩 {idx} / {len(urls)} 번째 URL 진행 중")
        crawler.crawl(url)
        if idx % 50 == 0:
            crawler.driver.quit()
            time.sleep(1)
            crawler.__init__()

    crawler.save()
    crawler.close()










