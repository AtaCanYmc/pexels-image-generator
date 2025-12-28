import os
from dotenv import load_dotenv

load_dotenv()

project_name = os.getenv('PROJECT_NAME', 'unknown')


def term_to_folder_name(term: str) -> str:
    return term.replace(' ', '_').lower()


def create_folders_if_not_exist(folder_names: list[str]):
    for folder_name in folder_names:
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)


def get_yes_no_input(prompt: str) -> bool:
    while True:
        user_input = input(f"{prompt} (y/n): ").strip().lower()
        if user_input in ['y', 'yes']:
            return True
        elif user_input in ['n', 'no']:
            return False
        else:
            print("Invalid input. Please enter 'y' or 'n'.")


def read_search_terms(file_path: str) -> list[str]:
    with open(file_path, 'r') as file:
        terms = [line.strip() for line in file if line.strip()]
    return terms


def read_html_as_string(file_path: str) -> str:
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()
