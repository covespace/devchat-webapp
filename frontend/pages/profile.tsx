// frontend/pages/profile.tsx
import Head from 'next/head';
import { useRouter } from 'next/router';
import { useEffect, useState } from 'react';

const Profile: React.FC = () => {
  const router = useRouter();
  const [userId, setUserId] = useState<string | null>(null);

  useEffect(() => {
    if (typeof window !== 'undefined') {
      const storedUserId = localStorage.getItem('user_id');
      if (storedUserId) {
        setUserId(storedUserId);
      } else {
        setTimeout(() => {
          router.push('/');
        }, 2000);
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
    <div>
      <Head>
        <title>Profile</title>
      </Head>

      <main>
        <h1>Welcome, User ID: {userId}</h1>
        <button onClick={handleSignOut} className="absolute top-4 right-4">
          Sign Out
        </button>
      </main>
    </div>
  );
};

export default Profile;
