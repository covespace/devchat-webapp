import argparse
import os
import re
import openpyxl
import requests

API_BASE_URL = os.environ.get('API_BASE_URL', 'http://localhost:8000')


def sanitize_name(name: str) -> str:
    return re.sub(r'[^a-zA-Z0-9]+', '-', name).strip('-')


def create_organization(org_name: str) -> int:
    response = requests.post(
        f"{API_BASE_URL}/api/v1/organizations",
        json={"name": org_name, "country_code": "CN"},
        timeout=10
    )
    if response.status_code != 201:
        return None
    return response.json()["org_id"]


def create_user(email: str) -> int:
    username = sanitize_name(email)
    response = requests.post(
        f"{API_BASE_URL}/api/v1/users",
        json={"username": username, "email": email},
        timeout=10
    )
    if response.status_code != 201:
        return None
    return response.json()["user_id"]


def add_user_to_organization(org_id: int, user_id: int, role: str):
    response = requests.post(
        f"{API_BASE_URL}/api/v1/organizations/{org_id}/users",
        json={"user_id": user_id, "role": role},
        timeout=10
    )
    return response.status_code == 200


def issue_access_key(org_id: int, user_id: int):
    response = requests.post(
        f"{API_BASE_URL}/ap1/vi/organizations/{org_id}/user/{user_id}/access_key",
        timeout=10
    )
    return response.status_code == 200


def process_excel_file(file_path: str):
    workbook = openpyxl.load_workbook(file_path)
    sheet = workbook.active

    for row in reversed(list(sheet.iter_rows(min_row=2))):
        org_name = sanitize_name(row[6].value)
        org_id = create_organization(org_name)
        if org_id is None:
            print(f"Failed to create organization: {org_name}")
            break

        owner_email = row[7].value
        owner_id = create_user(owner_email)
        if owner_id is None:
            print(f"Failed to create user: {owner_email}")
            continue

        if not add_user_to_organization(org_id, owner_id, "owner"):
            print(f"Failed to add owner {owner_email} to organization {org_name}")
            continue

        if not issue_access_key(org_id, owner_id):
            print(f"Failed to issue access key for owner {owner_email} in organization {org_name}")

        for col in range(8, 12):
            member_email = row[col].value
            if member_email:
                member_id = create_user(member_email)
                if member_id is None:
                    print(f"Failed to create user: {member_email}")
                    continue

                if not add_user_to_organization(org_id, member_id, "member"):
                    print(f"Failed to add member {member_email} to organization {org_name}")
                    continue

                if not issue_access_key(org_id, member_id):
                    print(f"Failed to issue access key for {member_email} in {org_name}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Process an Excel file to create organizations and users.")
    parser.add_argument("file", help="Path to the Excel file.")
    args = parser.parse_args()

    process_excel_file(args.file)
