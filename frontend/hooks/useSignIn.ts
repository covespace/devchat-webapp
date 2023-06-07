import { useState } from 'react';
import { useRouter } from 'next/router';
import { isAxiosError } from 'axios';
import apiClient from '@/api/client';

const useSignIn = () => {
  const [accessKey, setAccessKey] = useState('');
  const [errorMessage, setErrorMessage] = useState('');
  const [captchaToken, setCaptchaToken] = useState<string | null>(null);
  const router = useRouter();

  const handleSignIn = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const response = await apiClient.post('/api/v1/login', {
        key: accessKey,
        token: captchaToken,
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

  const handleCaptchaVerify = (token: string) => {
    setCaptchaToken(token);
  };

  return { accessKey, setAccessKey, errorMessage, handleSignIn, handleCaptchaVerify };
};

export default useSignIn;
