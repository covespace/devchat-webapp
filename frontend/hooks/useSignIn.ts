import { useState } from 'react';
import { useRouter } from 'next/router';
import { isAxiosError } from 'axios';
import apiClient from '@/api/client';

const useSignIn = () => {
  const [accessKey, setAccessKey] = useState('');
  const [signInErrorMessage, setErrorMessage] = useState('');
  const router = useRouter();

  const handleSignIn = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const response = await apiClient.post('/api/v1/login', {
        key: accessKey
      });
      const { user_id } = response.data;
      localStorage.setItem('user_id', user_id.toString());
      router.push('/profile');
    } catch (error: unknown) {
      console.error('Error signing in:', error);
      if (isAxiosError(error) && error.response && error.response.status === 401) {
        setErrorMessage('Failed to sign in. Please check your access key.');
      } else {
        setErrorMessage('Network error. Please check your connection and try again.');
      }
    }
  };

  return { accessKey, setAccessKey, signInErrorMessage, handleSignIn };
};

export default useSignIn;
