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
    <form onSubmit={onSubmit} className="form-bg-dark">
      <div className="mb-4">
        <label className="form-label" htmlFor="access-key">
          Access Key
        </label>
        <input
          className="form-input"
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
      <button className="form-button" type="submit">
        Sign In
      </button>
    </form>
  );
};

export default SignInForm;
