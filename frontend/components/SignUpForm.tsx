import React from 'react';

interface SignUpFormProps {
  onSubmit: (event: React.FormEvent<HTMLFormElement>) => void;
  signUpErrorMessage: string;
  signUpSuccessMessage: string;
}

const SignUpForm: React.FC<SignUpFormProps> = ({
  onSubmit,
  signUpErrorMessage,
  signUpSuccessMessage,
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
        <label className="form-label" htmlFor="org-name">
          Create Organization (Optional)
        </label>
        <input
          className="form-input"
          id="org-name"
          type="text"
          placeholder="Enter your organization name"
        />
      </div>
      {signUpErrorMessage && (
        <p className="text-red-500 text-xs italic mt-2">{signUpErrorMessage}</p>
      )}
      {signUpSuccessMessage && (
        <p className="text-green-500 text-xs italic mt-2">{signUpSuccessMessage}</p>
      )}
      <button className="form-button" type="submit">
        Sign Up
      </button>
    </form>
  );
};

export default SignUpForm;
