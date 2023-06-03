import argparse
import os
import logging
import re
from typing import List
import openpyxl
import requests


API_BASE_URL = os.environ.get('API_BASE_URL', 'http://localhost:8000')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def sanitize_name(name: str) -> str:
    return re.sub(r'[^a-zA-Z0-9]+', '-', name).strip('-')


def create_organization(org_name: str) -> int:
    response = requests.post(
        f"{API_BASE_URL}/api/v1/organizations",
        json={"name": org_name, "country_code": "CN"},
        timeout=20
    )
    if response.status_code != 201:
        logger.error("Failed to create organization %s: %s", org_name, response.json())
        return None
    logger.info("Successfully created organization %s", org_name)
    return response.json()["org_id"]


def create_user(email: str) -> int:
    username = sanitize_name(email)
    response = requests.post(
        f"{API_BASE_URL}/api/v1/users",
        json={"username": username, "email": email},
        timeout=20
    )
    if response.status_code != 201:
        logger.error("Failed to create user %s: %s", email, response.json())
        return None
    logger.info("Successfully created user %s", email)
    return response.json()["user_id"]


def add_user_to_organization(org_id: int, user_id: int, role: str) -> bool:
    response = requests.post(
        f"{API_BASE_URL}/api/v1/organizations/{org_id}/users",
        json={"user_id": user_id, "role": role},
        timeout=20
    )
    if response.status_code != 200:
        logger.error("Failed to add user %d to organization %d with role '%s': %s",
                     user_id, org_id, role, response.json())
        return False
    logger.info("Successfully added user %d to organization %d with role '%s'",
                user_id, org_id, role)
    return True


def issue_access_key(org_id: int, user_id: int) -> bool:
    response = requests.post(
        f"{API_BASE_URL}/api/v1/organizations/{org_id}/user/{user_id}/access_key",
        timeout=20
    )
    if response.status_code != 200:
        logger.error("Failed to issue access key for user %d in organization %d: %s",
                     user_id, org_id, response.json())
        return False
    logger.info("Successfully issued access key for user %d in organization %d", user_id, org_id)
    return True


def check_existence(org_name: str, email: str) -> bool:
    response = requests.get(
        f"{API_BASE_URL}/api/v1/organizations/{org_name}/id",
        timeout=20
    )
    if response.status_code != 200:
        return False

    org_id = response.json()["org_id"]

    response = requests.get(
        f"{API_BASE_URL}/api/v1/organizations/{org_id}/users",
        timeout=20
    )
    if response.status_code != 200:
        logger.error("Failed to fetch users for organization %d: %s", org_id, response.json())
        return False

    users: List[dict] = response.json()
    for user in users:
        if user["email"] == email:
            return True

    return False


def process_excel_file(file_path: str):
    workbook = openpyxl.load_workbook(file_path)
    sheet = workbook.active

    for row in sheet.iter_rows(min_row=2):
        org_name = sanitize_name(row[6].value)
        owner_email = row[7].value
        if check_existence(org_name, owner_email):
            logger.info("Skipped row %d and older rows", row[0].row)
            break

        logger.info("Processing row %d", row[0].row)

        org_id = create_organization(org_name)
        if org_id is None:
            logger.warning("Check row %d for failed org creation", row[0].row)
            continue

        owner_id = create_user(owner_email)
        if owner_id is None:
            logger.warning("Check row %d for failed user creation", row[0].row)
            continue

        if not add_user_to_organization(org_id, owner_id, "owner"):
            logger.warning("Check row %d for failed user addition to org", row[0].row)
            continue

        if not issue_access_key(org_id, owner_id):
            logger.warning("Check row %d, column %d for failed access key issue",
                           row[7].row, row[7].column)

        for col in range(8, 12):
            member_email = row[col].value
            if member_email:
                member_id = create_user(member_email)
                if member_id is None:
                    logger.warning("Check row %d, column %d for failed user creation",
                                   row[col].row, row[col].column)
                    continue
                if not add_user_to_organization(org_id, member_id, "member"):
                    logger.warning("Check row %d, column %d for failed user addition to org",
                                   row[col].row, row[col].column)
                    continue
                if not issue_access_key(org_id, member_id):
                    logger.warning("Check row %d, column %d for failed access key issue",
                                   row[col].row, row[col].column)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Process an Excel file to create organizations and users.")
    parser.add_argument("file", help="Path to the Excel file.")
    args = parser.parse_args()

    process_excel_file(args.file)
