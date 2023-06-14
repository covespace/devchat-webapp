import { useState } from 'react';
import Head from 'next/head';
import Image from 'next/image';
import Footer from '@/components/Footer';
import SignInForm from '@/components/SignInForm';
import SignUpForm from '@/components/SignUpForm';
import useSignIn from '@/hooks/useSignIn';
import useSignUp from '@/hooks/useSignUp';

const Home: React.FC = () => {
  const [activeTab, setActiveTab] = useState('signin');
  const { accessKey, setAccessKey, signInErrorMessage, handleSignIn } = useSignIn();
  const { signUpErrorMessage, signUpSuccessMessage, handleSignUp, handleSignUpCaptcha } = useSignUp();

  return (
    <div>
      <Head>
        <title>DevChat Sign In & Sign Up</title>
        <link rel="icon" href="/favicon.ico" />
      </Head>
      <main className="container main">
        <Image src="/devchat.png" alt="Logo" width={120} height={120} style={{ marginBottom: '2rem' }} />
        <h1 className="text-4xl font-bold mb-8">Welcome to DevChat!</h1>

        <div className="card w-[400px]">
          <div className="flex mb-4">
            <button
              className={`text-2xl font-semibold mr-4 ${activeTab === 'signin' ? 'text-blue-500' : 'text-gray-400'
                }`}
              onClick={() => setActiveTab('signin')}
            >
              Sign In
            </button>
            <button
              className={`text-2xl font-semibold ${activeTab === 'signup' ? 'text-blue-500' : 'text-gray-400'
                }`}
              onClick={() => setActiveTab('signup')}
            >
              Sign Up
            </button>
          </div>

          {activeTab === 'signin' && (
            <SignInForm
              accessKey={accessKey}
              errorMessage={signInErrorMessage}
              onAccessKeyChange={setAccessKey}
              onSubmit={handleSignIn}
            />
          )}

          {activeTab === 'signup' && (
            <SignUpForm
              onSubmit={handleSignUp}
              signUpErrorMessage={signUpErrorMessage}
              signUpSuccessMessage={signUpSuccessMessage}
              onCaptchaVerify={handleSignUpCaptcha}
            />
          )}
        </div>
      </main>
      <footer className="footer">
        <Footer />
      </footer>
    </div>
  );
};

export default Home;
