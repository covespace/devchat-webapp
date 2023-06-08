// frontend/pages/profile.tsx
import Head from 'next/head';
import { useRouter } from 'next/router';
import { useEffect, useState } from 'react';
import apiClient from '@/api/client';

const Profile: React.FC = () => {
  const router = useRouter();
  const [userId, setUserId] = useState<string | null>(null);
  const [userName, setUserName] = useState<string | null>(null);
  const [userEmail, setUserEmail] = useState<string | null>(null);

  useEffect(() => {
    if (typeof window !== 'undefined') {
      const storedUserId = localStorage.getItem('user_id');
      if (storedUserId) {
        setUserId(storedUserId);
        apiClient.get(`/api/v1/users/${storedUserId}/profile`)
          .then((response) => {
            setUserName(response.data.username);
            setUserEmail(response.data.email);
          });
      } else {
        setTimeout(() => {
          router.push('/');
        }, 1500);
      }
    }
  }, [router]);

  const handleSignOut = () => {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('user_id');
    }
    router.push('/');
  };

  if (userId === null) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">
          <span className="block sm:inline"> You don&apos;t have access to this page.</span>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100 py-6 flex flex-col justify-center sm:py-12">
      <Head>
        <title>Profile</title>
      </Head>

      <main className="relative w-full h-full sm:max-w-xl sm:mx-auto">
        <div className="relative px-8 py-16 bg-white shadow-lg sm:rounded-3xl sm:p-20 h-full">
          <div className="flex justify-between items-start">
            <div>
              <h1 className="text-2xl font-semibold mb-1 profile-text-dark">Welcome, {userName}!</h1>
              <p className="text-sm mb-4 profile-text-dark">{userEmail}</p>
            </div>
            <button onClick={handleSignOut} className="form-button min-w-max">
              Sign Out
            </button>
          </div>
          <p className="mt-4 profile-text-dark">
            Your access key works! Please visit{' '}
            <a href="https://marketplace.visualstudio.com/items?itemName=merico.devchat" target="_blank" rel="noopener noreferrer" className="text-blue-500 underline">
              this link
            </a>{' '}
            to install the VS Code extension or follow the steps below:
          </p>
          <ul className="list-disc list-inside mt-2 profile-text-dark">
            <li className='mb-2'>Open the Extensions view (⇧⌘X) in Visual Studio Code, search for DevChat, and install the extension.</li>
            <li className='mb-2'>Since DevChat requires a Git or SVN repository folder to store metadata, be sure to open a Git or SVN project.</li>
            <li className='mb-2'>Press ⇧⌘P / Ctrl+Shift+P or F1 in Visual Studio Code to open the Command Palette. Type &ldquo;devchat access key&rdquo; and execute the command to enter your access key.</li>
            <li className='mb-2'>We recommend dragging the DevChat logo from the left sidebar to the right sidebar to avoid overlapping with the Explorer.</li>
          </ul>
        </div>
      </main>
    </div>
  );
};

export default Profile;
