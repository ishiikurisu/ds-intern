import urllib.request
from bs4 import BeautifulSoup
from multiprocessing import Process
import document

class Researcher:
    def __init__(self, limit):
        """Starts the main variables that will be used in this process"""
        self.limit = limit
        self.debug = False
        self.pages = []
        self.visited = set()

    def study_from(self, start_point):
        """Starts the main study loop from a starting wikipedia page"""
        self.docs = []
        self.how_many = 1
        self.study(start_point)
        processes = []

        # downloading and extracting information
        while len(self.pages) > 0:
            page = self.pages[0]
            del self.pages[0]
            process = Process(target=self.study, args=(page,))
            process.start()
            processes.append(process)
        for process in processes:
            process.join()

        # generating final files
        # TODO Generate a list of all words in their weights in all visited documents

        if self.debug:
            print('how many: %d' % (self.how_many))
            print('...')

    def study(self, page):
        """Study a page by parsing its HTML, adding the next pages to be followed
        and analyzing the current page text."""
        html = urllib.request.urlopen(page).read()
        soup = BeautifulSoup(html, 'html.parser')
        div = soup.find('div', {'id': 'mw-content-text'})
        self.visited.add(page)

        links = div.find_all('a')
        for link in links:
            try:
                next_page = self.get_link(link)
                if next_page is not None:
                    self.try_to_add(next_page)
            except UnicodeEncodeError:
                pass

        all_p = div.find_all('p')
        content = ''
        for p in all_p:
            text = self.get_text(p)
            content += '\n' + text
        self.analyze(content)

        if self.debug:
            try:
                print('---')
                print('page: %s' % (page))
                print('content:')
                print(content)
            except UnicodeEncodeError:
                pass

    def try_to_add(self, page):
        """Tries to add another page to the study process."""
        if (self.how_many < self.limit) and (page not in self.visited):
            self.pages.append(page)
            self.how_many += 1
            self.visited.add(page)

    def get_link(self, a):
        """Gets a link from a Beautiful Soup anchor element."""
        outlet = None
        try:
            href = a['href']
            if href.startswith('/wiki'):
                outlet = 'https://wikipedia.org%s' % href
        except KeyError:
            pass
        return outlet

    def get_text(self, p):
        """Gets the text from a beautiful soup paragraph element."""
        return ' '.join(text.strip() for text in p.find_all(text=True, recursive=True))

    def analyze(self, text):
        """Studies the content of the text as proposed in this study."""
        # IDEA Create an analyzer class that will count words per document and give an opinion.
        doc = document.Document(text)
        self.docs.append(doc)
