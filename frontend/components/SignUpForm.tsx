import React from 'react';

interface SignUpFormProps {
  onSubmit: (event: React.FormEvent<HTMLFormElement>) => void;
  signUpErrorMessage: string;
  signUpSuccessMessage: string;
}

const SignUpForm: React.FC<SignUpFormProps> = ({ onSubmit, signUpErrorMessage, signUpSuccessMessage }) => {
  return (
    <form onSubmit={onSubmit}>
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
  );
};

export default SignUpForm;
