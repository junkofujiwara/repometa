''' GitHubUtil class '''
import re
import requests
from bs4 import BeautifulSoup

class GitHubUtil:
    ''' GitHubUtil class '''

    def __init__(self, token, owner, repo):
        '''init'''
        self.token = token
        self.owner = owner
        self.repo = repo
        self.headers = {"Authorization" : f"token {self.token}"}

    def get_repo_details(self):
        '''get_repo_details'''
        try:
            url = f"https://api.github.com/repos/{self.owner}/{self.repo}"
            response = requests.get(url, headers=self.headers)
            data = response.json()
            return {
                "star_count": data["stargazers_count"],
                "fork_count": data["forks_count"],
                "watch_count": data["subscribers_count"],
            }
        except requests.exceptions.RequestException:
            return None

    def get_contributors_count(self):
        '''get_contributors_count'''
        try:
            url = f"https://api.github.com/repos/{self.owner}/{self.repo}/contributors?anon=true"
            response = requests.get(url, headers=self.headers)
            first_page_data = response.json()
            first_page_length = len(first_page_data)

            if 'link' in response.headers:
                links = response.headers['link'].split(', ')
                last_link = [link for link in links if 'rel="last"' in link][0]
                last_page_url = re.search('<(.*)>', last_link).group(1)
                last_response = requests.get(last_page_url, headers=self.headers)
                last_page_data = last_response.json()
                last_page_length = len(last_page_data)
                page_count = int(re.search(r'page=(\d+)', last_page_url).group(1))
                total_contributors = (first_page_length * (page_count - 1)) + last_page_length
            else:
                total_contributors = first_page_length
            return total_contributors
        except requests.exceptions.RequestException:
            return None

    def get_dependencies_count(self):
        '''get_dependencies_count'''
        try:
            url = "https://api.github.com/graphql"
            headers = {"Authorization": f"Bearer {self.token}",
                       "Accept": "application/vnd.github.hawkgirl-preview+json"}
            query = f"""
            {{
            repository(owner: "{self.owner}", name: "{self.repo}") {{
                dependencyGraphManifests(first: 100) {{
                nodes {{
                    dependencies {{
                    totalCount
                    }}
                }}
                }}
            }}
            }}
            """
            response = requests.post(url, headers=headers, json={'query': query})
            data = response.json()
            dependencies_count = sum(node['dependencies']['totalCount'] for node
                                     in data['data']['repository']
                                     ['dependencyGraphManifests']['nodes'])
            return dependencies_count
        except requests.exceptions.RequestException:
            return None

    def get_dependents_count(self):
        '''get_dependents_count'''
        try:
            url = f"https://github.com/{self.owner}/{self.repo}/network/dependents"
            href = f"/{self.owner}/{self.repo}/network/dependents?dependent_type=REPOSITORY"
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            repos_count_element = soup.find('a', {'href': href})
            if repos_count_element:
                repos_count = repos_count_element.text.strip().replace('Repositories', '')
                return int(repos_count.replace(',', ''))
            return None
        except requests.exceptions.RequestException:
            return None
