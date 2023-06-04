import { useState } from 'react';
import Head from 'next/head';
import Image from 'next/image';
import SignInForm from '../components/SignInForm';
import useSignIn from '../hooks/useSignIn';

const Home: React.FC = () => {
  const [activeTab, setActiveTab] = useState('signin');
  const { accessKey, setAccessKey, errorMessage, handleSignIn } = useSignIn();

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
            <SignInForm
              accessKey={accessKey}
              errorMessage={errorMessage}
              onAccessKeyChange={setAccessKey}
              onSubmit={handleSignIn}
            />
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
