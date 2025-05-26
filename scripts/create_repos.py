import argparse
import json
import requests
import base64

def create_repo(org, project_name, project_id, pat, repo_name):
    # Check if the repository already exists
    check_url = f'{org}/{project_name}/_apis/git/repositories/{repo_name}?api-version=6.0'
    pat_encoded = base64.b64encode(f":{pat}".encode()).decode()
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Basic {pat_encoded}'
    }
    check_response = requests.get(check_url, headers=headers)
    if check_response.status_code == 200:
        print(f'Repositório {repo_name} já existe. Nenhuma ação necessária.')
        return None  # Return None if the repository already exists

    # Proceed to create the repository if it doesn't exist
    url = f'{org}/{project_name}/_apis/git/repositories?api-version=6.0'
    data = {
        'name': repo_name,
        'project': {'id': project_id}  # Use the project ID here
    }
    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 201:
        print(f'Repositório {repo_name} criado com sucesso! Agora vai criar a Main Branch')
        repo_id = response.json()['id']
        create_main_branch(org, project_name, pat, repo_id)
        print(f'Branch main criada com sucesso! Agora vai criar a Develop Branch')
        return repo_id  # Return the repo_id if the repository was successfully created
    else:
        print(f'Erro ao criar o repositório {repo_name}: {response.status_code} - {response.text}')
        return None  # Return None if the repository creation failed
  
def create_main_branch(org, project_name, pat, repo_id):
    # Create the main branch with an initial commit
    url = f'{org}/{project_name}/_apis/git/repositories/{repo_id}/pushes?api-version=6.0'
    pat_encoded = base64.b64encode(f":{pat}".encode()).decode()
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Basic {pat_encoded}'
    }
    data = {
        "refUpdates": [
            {"name": "refs/heads/main", "oldObjectId": "0000000000000000000000000000000000000000"}
        ],
        "commits": [
            {
                "comment": "Initial commit for main branch",
                "changes": [
                    {
                        "changeType": "add",
                        "item": {"path": "/README.md"},
                        "newContent": {
                            "content": "# Initial Commit\n\nThis is the initial commit for the repository.",
                            "contentType": "rawtext"
                        }
                    }
                ]
            }
        ]
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 201:
        print(f'Branch main criada com sucesso no repositório {repo_id}!')
        return True
    else:
        print(f'Erro ao criar a branch main no repositório {repo_id}: {response.status_code} - {response.text}')
        return False

def create_repos(org, project_name, project_id, pat, repos_file):
    with open(repos_file, 'r') as f:
        repos = json.load(f)
    for repo in repos:
        create_repo(org, project_name, project_id, pat, repo['name'])

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--org', required=True, help="URL da organização")
    parser.add_argument('--project_name', required=True, help="Nome do projeto (para a URL)")
    parser.add_argument('--project_id', required=True, help="ID do projeto (para o corpo da requisição)")
    parser.add_argument('--pat', required=True, help="Token de acesso pessoal")
    parser.add_argument('--input', required=True, help="Arquivo de entrada JSON com os repositórios")
    args = parser.parse_args()
    create_repos(args.org, args.project_name, args.project_id, args.pat, args.input)
