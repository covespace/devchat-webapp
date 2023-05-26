"""
test_query.py contains tests for the query.py module.
"""
import datetime
from webapp.controller import create_organization, create_user, add_user_to_organization
from webapp.controller import get_users_of_organization
from webapp.controller import create_access_key, revoke_access_key
from webapp.controller import get_valid_keys_of_organization, get_revoked_key_hashes
from webapp.utils import now


def test_get_users_of_organization_success(database):
    org_name = "Test Organization"
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
    assert [user1.id, username1, email1] in users
    assert [user2.id, username2, email2] in users


def test_get_users_of_organization_custom_columns(database):
    org_name = "Test Organization"
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
    assert [user.id, location, company] in users


def test_get_users_of_organization_invalid_id(database):
    users = get_users_of_organization(database, 999)
    assert users == []


def test_get_valid_keys_of_organization_success(database):
    org_name = "Test Organization"
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
    org_name = "Test Organization"
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
