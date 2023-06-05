import { useState } from 'react';
import { createOrganization, createUser, addUserToOrganization, issueAccessKey } from '../api/signUp';

const useSignUp = () => {
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

  return {
    signUpErrorMessage,
    signUpSuccessMessage,
    handleSignUp,
  };
};

export default useSignUp;
