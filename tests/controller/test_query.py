"""
test_query.py contains tests for the query.py module.
"""
import datetime
from webapp.controller import create_organization, create_user, add_user_to_organization
from webapp.controller import get_organization_id_by_name, get_users_of_organization
from webapp.controller import create_access_key, revoke_access_key
from webapp.controller import get_valid_keys_of_organization, get_revoked_key_hashes
from webapp.controller import get_user_profile, get_organizations_of_user
from webapp.controller import get_user_keys_in_organizations
from webapp.utils import now


def test_get_organization_id_by_name_success(database):
    org_name = "Test-Organization"
    country_code = "USA"
    organization = create_organization(database, org_name, country_code)

    org_id = get_organization_id_by_name(database, org_name)

    assert organization.id == org_id


def test_get_organization_id_by_name_no_org(database):
    org_id = get_organization_id_by_name(database, "Nonexistent Organization")
    assert org_id is None


def test_get_users_of_organization_success(database):
    org_name = "Test-Organization"
    country_code = "USA"
    organization = create_organization(database, org_name, country_code)

    username1 = "testuser1"
    email1 = "testuser1@example.com"
    user1 = create_user(database, username1, email1)

    username2 = "testuser2"
    email2 = "testuser2@example.com"
    user2 = create_user(database, username2, email2)

    add_user_to_organization(database, user1.id, organization.id)
    add_user_to_organization(database, user2.id, organization.id)

    users = get_users_of_organization(database, organization.id)

    assert len(users) == 2
    assert {"id": user1.id, "username": username1, "email": email1} in users
    assert {"id": user2.id, "username": username2, "email": email2} in users


def test_get_users_of_organization_custom_columns(database):
    org_name = "Test-Organization"
    country_code = "USA"
    organization = create_organization(database, org_name, country_code)

    username = "testuser"
    email = "testuser@example.com"
    company = "Test Company"
    location = "Test City"
    social_profile = "https://example.com/testuser"
    user = create_user(database, username, email, company, location, social_profile)

    add_user_to_organization(database, user.id, organization.id)

    users = get_users_of_organization(database,
                                      organization.id, columns=['id', 'location', 'company'])

    assert len(users) == 1
    assert {'id': user.id, 'location': location, 'company': company} in users


def test_get_users_of_organization_invalid_id(database):
    users = get_users_of_organization(database, 999)
    assert users == []


def test_get_valid_keys_of_organization_success(database):
    org_name = "Test-Organization"
    country_code = "USA"
    organization = create_organization(database, org_name, country_code)

    username = "testuser"
    email = "testuser@example.com"
    user = create_user(database, username, email)

    add_user_to_organization(database, user.id, organization.id)

    key1, _ = create_access_key(database, user.id, organization.id, "key1")
    key2, _ = create_access_key(database, user.id, organization.id, "key2")

    valid_keys = get_valid_keys_of_organization(database, organization.id)
    valid_hashes = [key.key_hash for key in valid_keys]

    assert len(valid_keys) == 2
    assert key1.key_hash in valid_hashes
    assert key2.key_hash in valid_hashes


def test_get_revoked_keys_in_time_range_success(database):
    org_name = "Test-Organization"
    country_code = "USA"
    organization = create_organization(database, org_name, country_code)

    username = "testuser"
    email = "testuser@example.com"
    user = create_user(database, username, email)

    add_user_to_organization(database, user.id, organization.id)

    key1, _ = create_access_key(database, user.id, organization.id, 'key1')
    key2, _ = create_access_key(database, user.id, organization.id, 'key2')

    revoke_access_key(database, key1.id)

    current_time = now(database)
    start_time = current_time - datetime.timedelta(hours=1)
    end_time = current_time + datetime.timedelta(hours=1)

    revoked_hashes = get_revoked_key_hashes(database, start_time, end_time)

    assert len(revoked_hashes) == 1
    assert key1.key_hash in revoked_hashes
    assert key2.key_hash not in revoked_hashes


def test_get_revoked_keys_in_time_range_no_keys(database):
    current_time = now(database)
    start_time = current_time - datetime.timedelta(hours=1)
    end_time = current_time + datetime.timedelta(hours=1)

    revoked_keys = get_revoked_key_hashes(database, start_time, end_time)

    assert revoked_keys == []


def test_get_user_profile_success(database):
    username = "testuser"
    email = "testuser@example.com"
    user = create_user(database, username, email)

    user_profile = get_user_profile(database, user.id)

    assert user_profile == {"username": username, "email": email}


def test_get_user_profile_invalid_id(database):
    user_profile = get_user_profile(database, 999)

    assert user_profile is None


def test_get_organizations_of_user_success(database):
    org_name1 = "Test-Organization1"
    org_name2 = "Test-Organization2"
    country_code = "USA"
    organization1 = create_organization(database, org_name1, country_code)
    organization2 = create_organization(database, org_name2, country_code)

    username = "testuser"
    email = "testuser@example.com"
    user = create_user(database, username, email)

    add_user_to_organization(database, user.id, organization1.id, role="owner")
    add_user_to_organization(database, user.id, organization2.id, role="member")

    organizations = get_organizations_of_user(database, user.id)

    assert len(organizations) == 2
    assert {"id": organization1.id, "name": org_name1, "role": "owner"} in organizations
    assert {"id": organization2.id, "name": org_name2, "role": "member"} in organizations


def test_get_organizations_of_user_custom_columns(database):
    org_name = "Test-Organization"
    country = "USA"
    organization = create_organization(database, org_name, country)

    username = "testuser"
    email = "testuser@example.com"
    user = create_user(database, username, email)

    add_user_to_organization(database, user.id, organization.id, role="owner")

    organizations = get_organizations_of_user(database, user.id,
                                              columns=["id", "name", "country_code"])

    assert len(organizations) == 1
    assert {"id": organization.id, "name": org_name, "country_code": country} in organizations


def test_get_organizations_of_user_invalid_id(database):
    organizations = get_organizations_of_user(database, 999)

    assert organizations == []


def test_get_user_keys_in_organizations(database):
    org_name1 = "Test-Organization1"
    org_name2 = "Test-Organization2"
    country_code = "USA"
    organization1 = create_organization(database, org_name1, country_code)
    organization2 = create_organization(database, org_name2, country_code)

    username = "testuser"
    email = "testuser@example.com"
    user = create_user(database, username, email)

    add_user_to_organization(database, user.id, organization1.id)
    add_user_to_organization(database, user.id, organization2.id)

    key1, _ = create_access_key(database, user.id, organization1.id, "key1")
    key2, _ = create_access_key(database, user.id, organization2.id)

    user_keys = get_user_keys_in_organizations(database, user.id,
                                               [organization1.id, organization2.id])

    assert len(user_keys) == 2
    assert {"id": key1.id, "thumbnail": key1.thumbnail, "create_time": key1.create_time} \
        in user_keys[organization1.id]
    assert {"id": key2.id, "thumbnail": key2.thumbnail, "create_time": key2.create_time} \
        in user_keys[organization2.id]

    # Test with custom columns
    user_keys_custom = get_user_keys_in_organizations(database, user.id,
                                                      [organization1.id, organization2.id],
                                                      columns=["name", "id", "thumbnail"])

    assert len(user_keys_custom) == 2
    assert {"name": "key1", "id": key1.id, "thumbnail": key1.thumbnail} \
        in user_keys_custom[organization1.id]
    assert {"name": None, "id": key2.id, "thumbnail": key2.thumbnail} \
        in user_keys_custom[organization2.id]
