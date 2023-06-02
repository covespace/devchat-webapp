// frontend/pages/index.tsx
import apiClient from '../app/apiClient';
import { useState } from 'react';
import Head from 'next/head';
import Image from 'next/image';
import { useRouter } from 'next/router';
import { AxiosError } from 'axios';

const Home: React.FC = () => {
  const [activeTab, setActiveTab] = useState('signin');
  const [accessKey, setAccessKey] = useState('');
  const [errorMessage, setErrorMessage] = useState('');
  const router = useRouter();

  const handleSignIn = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const response = await apiClient.post('/api/v1/login', { key_hash: accessKey });
      const { user_id } = response.data;
      localStorage.setItem('user_id', user_id.toString());
      router.push('/profile');
    }
    catch (error: unknown) {
      console.error('Error signing in:', error);
      if (error instanceof Error && error.message === 'Network Error') {
        setErrorMessage('Network error. Please check your connection and try again.');
      } else {
        setErrorMessage('Failed to sign in. Please check your access key.');
      }
    }
  };

  return (
    <div className="container mx-auto px-4">
      <Head>
        <title>Sign In & Sign Up</title>
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <main className="flex flex-col items-center justify-center min-h-screen py-2">
        <Image src="/devchat.png" alt="Logo" width={120} height={120} style={{ marginBottom: '2rem' }} />
        <h1 className="text-4xl font-bold mb-8">Welcome to DevChat!</h1>

        <div className="bg-white shadow-md rounded px-8 pt-6 pb-8 mb-4 flex flex-col w-[400px]">
          <div className="flex mb-4">
            <button
              className={`text-2xl font-semibold mr-4 ${
                activeTab === 'signin' ? 'text-blue-500' : 'text-gray-500'
              }`}
              onClick={() => setActiveTab('signin')}
            >
              Sign In
            </button>
            <button
              className={`text-2xl font-semibold ${
                activeTab === 'signup' ? 'text-blue-500' : 'text-gray-500'
              }`}
              onClick={() => setActiveTab('signup')}
            >
              Sign Up
            </button>
          </div>

          {activeTab === 'signin' && (
            <form onSubmit={handleSignIn}>
              <div className="mb-4">
                <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="access-key">
                  Access Key
                </label>
                <input
                  className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                  id="access-key"
                  type="text"
                  placeholder="Enter your access key"
                  value={accessKey}
                  onChange={(e) => setAccessKey(e.target.value)}
                />
              </div>
              {errorMessage && <p className="text-red-500 text-xs italic mb-4">{errorMessage}</p>}
              <button
                className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
                type="submit"
              >
                Sign In
              </button>
            </form>
          )}

          {activeTab === 'signup' && (
            <form>
              <div className="mb-4">
                <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="username">
                  Username
                </label>
                <input
                  className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                  id="username"
                  type="text"
                  placeholder="Enter your username"
                />
              </div>
              <div className="mb-4">
                <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="email">
                  Email
                </label>
                <input
                  className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                  id="email"
                  type="email"
                  placeholder="Enter your email"
                />
              </div>
              <div className="mb-4">
                <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="org-name">
                  Organization Name (Optional)
                </label>
                <input
                  className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                  id="org-name"
                  type="text"
                  placeholder="Enter your organization name"
                />
              </div>
              <button
                className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
                type="submit"
              >
                Sign Up
              </button>
            </form>
          )}
        </div>
      </main>
    </div>
  );
};

export default Home;
