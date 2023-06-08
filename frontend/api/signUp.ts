import apiClient from '@/api/client';
import { AxiosError } from 'axios';

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
    const axiosError = error as AxiosError<{ detail: string }>;
    if (axiosError.response && axiosError.response.data && axiosError.response.data.detail) {
      throw axiosError.response.data.detail;
    } else {
      throw 'An unknown error occurred.';
    }
  }
}
