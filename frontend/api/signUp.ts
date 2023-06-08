import apiClient from '@/api/client';

interface CreateUserResponse {
  user_id: number;
}

export async function createUser(username: string, email: string, token: string | null): Promise<number | null> {
  try {
    const response = await apiClient.post<CreateUserResponse>('/api/v1/users', {
      username: username,
      email: email,
      token: token,
    });

    return response.data.user_id;
  } catch (error) {
    console.error('Failed to create user:', error);
    throw error.response.data.detail;
  }
}
