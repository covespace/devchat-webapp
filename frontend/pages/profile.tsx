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
            <h1 className="text-2xl font-semibold mb-4">Welcome, {userName} ({userEmail})!</h1>
            <button onClick={handleSignOut} className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded">
              Sign Out
            </button>
          </div>
        </div>
      </main>
    </div>
  );
};

export default Profile;
