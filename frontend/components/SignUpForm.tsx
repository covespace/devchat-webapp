import React from 'react';
import HCaptcha from '@hcaptcha/react-hcaptcha';
import Link from 'next/link';

interface SignUpFormProps {
  onSubmit: (event: React.FormEvent<HTMLFormElement>) => void;
  signUpErrorMessage: string;
  signUpSuccessMessage: string;
  onCaptchaVerify: (token: string) => void;
}

const SignUpForm: React.FC<SignUpFormProps> = ({
  onSubmit,
  signUpErrorMessage,
  signUpSuccessMessage,
  onCaptchaVerify,
}) => {
  return (
    <form onSubmit={onSubmit} className="form-bg-dark">
      <div className="mb-4">
        <label className="form-label" htmlFor="username">
          Username
        </label>
        <input
          className="form-input"
          id="username"
          type="text"
          placeholder="3 to 39 alphanumeric chars or '-'"
        />
      </div>
      <div className="mb-4">
        <label className="form-label" htmlFor="email">
          Email
        </label>
        <input
          className="form-input"
          id="email"
          type="email"
          placeholder="Enter your email"
        />
      </div>
      <div className="mb-4">
        <HCaptcha
          sitekey={process.env.NEXT_PUBLIC_HCAPTCHA_SITEKEY || ''}
          onVerify={onCaptchaVerify}
        />
      </div>
      {signUpErrorMessage && (
        <p className="text-red-500 text-xs italic mt-2 mb-2">{signUpErrorMessage}</p>
      )}
      {signUpSuccessMessage && (
        <p className="text-green-500 text-xs italic mt-2 mb-2">{signUpSuccessMessage}</p>
      )}
      <p className="text-xs mb-2">
        By clicking Sign Up, you agree to our{' '}
        <Link href="/terms">
          <span className="text-blue-500">Terms</span>
        </Link>{' '}
        and{' '}
        <Link href="https://meri.co/privacy">
          <span className="text-blue-500">Privacy Policy</span>
        </Link>.
      </p>
      <button className="form-button" type="submit">
        Sign Up
      </button>
    </form>
  );
};

export default SignUpForm;
