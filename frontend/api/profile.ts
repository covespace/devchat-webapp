import { AxiosError } from 'axios';
import apiClient from '@/api/client';
import { NetworkError, ServerError, ClientError } from '@/api/errors';

interface Key {
  id: number;
  thumbnail: string;
  create_time: string;
}

interface OrganizationResponse {
  org_id: number;
  org_name: string;
  keys: Key[];
}

export async function getUserOrganizations(user_id: number): Promise<OrganizationResponse[] | Error> {
  try {
    const response = await apiClient.get<OrganizationResponse[]>(`/api/v1/users/${user_id}/organizations`);

    if (response.status >= 500) {
      const message = `Server internal issue: ${response.status} ${response.statusText}`;
      return new ServerError(message);
    } else if (response.status >= 400) {
      const message = `Client-side issue: ${response.status} ${response.statusText}`;
      return new ClientError(message);
    }

    return response.data;
  } catch (error) {
    const axiosError = error as AxiosError;

    if (!axiosError.response) {
      return new NetworkError('Network issue');
    }

    const message = `Unknown error occurred: ${axiosError.response.status} ${axiosError.response.statusText}`;
    console.error('Failed to get user organizations:', axiosError);
    return new Error(message);
  }
}
