import { useState } from 'react';
import Head from 'next/head';
import Image from 'next/image';
import SignInForm from '../components/SignInForm';
import useSignIn from '../hooks/useSignIn';
import { createOrganization, createUser, addUserToOrganization, issueAccessKey } from '../api/signUp';

const Home: React.FC = () => {
  const [activeTab, setActiveTab] = useState('signin');
  const { accessKey, setAccessKey, errorMessage, handleSignIn } = useSignIn();
  const [signUpErrorMessage, setSignUpErrorMessage] = useState('');
  const [signUpSuccessMessage, setSignUpSuccessMessage] = useState('');

  const handleSignUp = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const username = event.currentTarget.username.value;
    const email = event.currentTarget.email.value;
    const orgName = event.currentTarget['org-name'].value || username;
    const role = 'owner';

    const org_id = await createOrganization(orgName);
    if (org_id === null) {
      setSignUpErrorMessage('Failed to create account. Please check the user or organization name.');
      return;
    }

    const user_id = await createUser(username, email);
    if (user_id === null) {
      setSignUpErrorMessage('Failed to create user. Please check the email address.');
      return;
    }

    const addUserSuccess = await addUserToOrganization(org_id, user_id, role);
    if (!addUserSuccess) {
      setSignUpErrorMessage('Failed to add account. Please contact hello@devchat.ai.');
      return;
    }

    const accessKeySuccess = await issueAccessKey(org_id, user_id);
    if (!accessKeySuccess) {
      setSignUpErrorMessage('Failed to issue access key. Please contact hello@devchat.ai.');
      return;
    }

    setSignUpErrorMessage('');
    setSignUpSuccessMessage('Sign up successful! Check your email for the access key and sign in.');
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
            <SignInForm
              accessKey={accessKey}
              errorMessage={errorMessage}
              onAccessKeyChange={setAccessKey}
              onSubmit={handleSignIn}
            />
          )}

          {activeTab === 'signup' && (
            <form onSubmit={handleSignUp}>
              <div className="mb-4">
                <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="username">
                  Username
                </label>
                <input
                  className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                  id="username"
                  type="text"
                  placeholder="3 to 39 alphanumeric chars or '-'"
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
                  Create Organization (Optional)
                </label>
                <input
                  className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                  id="org-name"
                  type="text"
                  placeholder="Enter your organization name"
                />
              </div>
              {signUpErrorMessage && (
                <p className="text-red-500 text-xs italic mt-2">{signUpErrorMessage}</p>
              )}
              {signUpSuccessMessage && ( // Add this block
                <p className="text-green-500 text-xs italic mt-2">{signUpSuccessMessage}</p>
              )}
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
