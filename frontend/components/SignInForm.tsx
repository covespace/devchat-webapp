import React from 'react';

interface SignInFormProps {
  accessKey: string;
  errorMessage: string;
  onAccessKeyChange: (value: string) => void;
  onSubmit: (e: React.FormEvent) => void;
}

const SignInForm: React.FC<SignInFormProps> = ({
  accessKey,
  errorMessage,
  onAccessKeyChange,
  onSubmit,
}) => {
  return (
    <form onSubmit={onSubmit}>
      <div className="mb-4">
        <label
          className="block text-gray-700 text-sm font-bold mb-2"
          htmlFor="access-key"
        >
          Access Key
        </label>
        <input
          className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
          id="access-key"
          type="text"
          placeholder="Enter your access key"
          value={accessKey}
          onChange={(e) => onAccessKeyChange(e.target.value)}
        />
      </div>
      {errorMessage && (
        <p className="text-red-500 text-xs italic mb-4">{errorMessage}</p>
      )}
      <button
        className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
        type="submit"
      >
        Sign In
      </button>
    </form>
  );
};

export default SignInForm;
