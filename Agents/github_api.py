import requests
import os

from Service.TextInjectorService import TextInjectorService


class GitHubAPI:
    def __init__(self, token):
        self.token = token
        self.api_url = "https://api.github.com/user/repos"
        self.user_url = "https://api.github.com/user"  # URL to get user info
        self.issue_url = "https://api.github.com/repos/{owner}/{repo}/issues"  # URL for creating issues
        self.headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json"
        }
        self.owner = self.get_authenticated_user()  # Get the authenticated user's username

    def get_authenticated_user(self):
        response = requests.get(self.user_url, headers=self.headers)
        if response.status_code == 200:
            user_info = response.json()
            print("ID Github : " + user_info['login'])
            return user_info['login']  # Return the username (owner)
        else:
            print("Failed to get authenticated user information.")
            return None

    def create_repo(self, repo_name, private=False, description=""):
        data = {
            "name": repo_name,
            "private": private,
            "description": description
        }

        response = requests.post(self.api_url, headers=self.headers, json=data)

        if response.status_code == 201:
            print(f"Successfully created GitHub repository: {repo_name}")
            return True
        else:
            print(f"Failed to create repository: {response.json().get('message')}")
            return False

    def create_issue(self, repo_name, title, body, labels=None):
        # Construct the URL for the specific repository using the owner
        url = self.issue_url.format(owner=self.owner, repo=repo_name)  # Use the dynamic owner
        print(url)
        data = {
            "title": title,
            "body": body,
            "labels": labels or []
        }
        
        response = requests.post(url, headers=self.headers, json=data)
        
        if response.status_code == 201:
            print(f"Successfully created issue: {title}")
            TextInjectorService.write(f"Successfully created issue: {title}")
            return True
        else:
            print(f"Failed to create issue: {response.json().get('message')}")
            TextInjectorService.write(f"Failed to create issue: {response.json().get('message')}")
            return False
