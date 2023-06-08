import { useState } from 'react';
import { createUser } from '@/api/signUp';

const useSignUp = () => {
  const [signUpErrorMessage, setSignUpErrorMessage] = useState('');
  const [signUpSuccessMessage, setSignUpSuccessMessage] = useState('');
  const [captchaToken, setCaptchaToken] = useState<string | null>(null);

  const handleSignUp = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const username = event.currentTarget.username.value;
    const email = event.currentTarget.email.value;

    try {
      const user_id = await createUser(username, email, captchaToken);
      setSignUpErrorMessage('');
      setSignUpSuccessMessage('Sign up successful! Check your email for the access key and sign in.');
    } catch (errorDetail) {
      if (typeof errorDetail === 'string') {
        setSignUpErrorMessage(errorDetail);
      } else {
        setSignUpErrorMessage('An unknown error occurred.');
      }
    }
  };

  const handleSignUpCaptcha = (token: string) => {
    setCaptchaToken(token);
  };

  return {
    signUpErrorMessage,
    signUpSuccessMessage,
    handleSignUp,
    handleSignUpCaptcha,
  };
};

export default useSignUp;
