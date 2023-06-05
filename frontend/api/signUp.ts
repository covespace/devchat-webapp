import apiClient from './apiClient';

interface CreateOrganizationResponse {
  org_id: number;
}

interface CreateUserResponse {
  user_id: number;
}

export async function createOrganization(org_name: string): Promise<number | null> {
  try {
    const response = await apiClient.post<CreateOrganizationResponse>('/api/v1/organizations', {
      name: org_name,
    });

    return response.data.org_id;
  } catch (error) {
    console.error('Failed to create organization:', error);
    return null;
  }
}

export async function createUser(username: string, email: string): Promise<number | null> {
  try {
    const response = await apiClient.post<CreateUserResponse>('/api/v1/users', {
      username: username,
      email: email,
    });

    return response.data.user_id;
  } catch (error) {
    console.error('Failed to create user:', error);
    return null;
  }
}

export async function addUserToOrganization(org_id: number, user_id: number, role: string): Promise<boolean> {
  try {
    await apiClient.post(`/api/v1/organizations/${org_id}/users`, {
      user_id: user_id,
      role: role,
    });

    return true;
  } catch (error) {
    console.error('Failed to add user to organization:', error);
    return false;
  }
}

export async function issueAccessKey(org_id: number, user_id: number): Promise<boolean> {
  try {
    await apiClient.post(`/api/v1/organizations/${org_id}/user/${user_id}/access_key`);

    return true;
  } catch (error) {
    console.error('Failed to issue access key:', error);
    return false;
  }
}
