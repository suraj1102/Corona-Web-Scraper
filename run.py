import requests
from bs4 import BeautifulSoup
import smtplib

class WebScraper():
    def __init__(self):
        """GETS THE CORONA PAGE AND CREATES A SOUP"""
        headers = {
            'User-Agent': "user-agent"
        }

        self.page = requests.get("https://www.worldometers.info/coronavirus/", headers=headers)
        self.soup = BeautifulSoup(self.page.content, 'html.parser')

    def get_main_data(self):
        """GETS TOTAL CASES, DEATHS, RECOVERED"""
        self.main_data = []

        for i in self.soup.find_all('div', id='maincounter-wrap'):
            data = f"{i.h1.text} {i.span.text}"
            self.main_data.append(data)

        return self.main_data

    def get_headings(self):
        """GETS THE HEADINGS IN THE TABLE TO BE USED LATER WITH TABLE DATA
        REMOVES UNWANTED/ UNIMPORTAND DATA"""
        self.headings = []

        for row in self.soup.find_all('table', id='main_table_countries_today'):
            for headings in row.find_all('th'):
                heading = headings.text
                self.headings.append(heading)       
                
        self.headings = [i.replace('\n', '') for i in self.headings]
        self.headings = [i.replace('\xa0', ' ') for i in self.headings]

        self.headings = self.headings[1:15]

    def get_country_data(self, place):
        """GET ALL STATS OF THE GIVEN COUNTRY 
        AND REMOVE UNWANTED DATA"""
        self.country_data = []

        for row in self.soup.find_all('table', id='main_table_countries_today'):
            for country in row.find_all('tr'):
                for td in country.find_all('td', text=place):
                    data = country.text
                    self.country_data.append(data)
    
        self.country_data = self.country_data[0].split('\n')
        self.country_data = self.country_data[2:16]
        self.country_data = ['-' if len(i) == 0 else i for i in self.country_data]

        return self.country_data

    def format_data(self, headings_list, con_data_list):
        """USING THE HEADINGS AND COUNTRY DATA LISTS TO CREATE A COMBINED GROUPED LIST"""
        self.formatted_data = []

        for heading, data in zip(headings_list, con_data_list):
            combination = f"{heading}: {data}\n"
            self.formatted_data.append(combination)
        
        return self.formatted_data

    def list_to_string(self, list_):
        """CONVERTS LIST INTO STRING SO THAT IT CAN BE USED IN AN EMAIL"""
        string = ''
        list_ = [i for i in list_]
        return string.join(list_)

    def create_message(self):
        """CREATES THE FINAL MESSAGE TO BE USED IN THE EMAIL"""
        main_data = self.get_main_data()
        main_data = [i+'\n' for i in main_data]
        main_data = self.list_to_string(main_data)

        usa_data = self.get_country_data('USA')
        usa_data = self.format_data(self.headings, usa_data)
        usa_data = self.list_to_string(usa_data)
        
        india_data = self.get_country_data('India')
        india_data = self.format_data(self.headings, india_data)
        india_data = self.list_to_string(india_data)

        UAE_data = self.get_country_data('UAE')
        UAE_data = self.format_data(self.headings, UAE_data)
        UAE_data = self.list_to_string(UAE_data)

        subject = 'COVID REPORT'
        body = f"{main_data}\n\n{usa_data}\n\n{india_data}\n\n{UAE_data}"

        self.msg = f"Subject: {subject}\n\n{body}".encode('utf-8')
    
    def emial(self, reciever, reciever_name):
        self.server = smtplib.SMTP('smtp.gmail.com', 587)
        self.server.ehlo()
        self.server.starttls()
        self.server.ehlo()

        self.server.login('your_email', 'password')

        self.server.sendmail(
            'your_email',
            reciever,
            self.msg
        )
        print(f'EMAIL SENT TO {reciever_name.upper()}')

        self.server.quit()

    def run(self):
        self.get_main_data()
        self.get_headings()
        self.create_message()
        self.emial('recievers_email', 'recievers_name')

WebScraper = WebScraper()
WebScraper.run()
