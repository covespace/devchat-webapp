import React from 'react';
import { FaGithub } from 'react-icons/fa';
import Link from 'next/link';

const Footer: React.FC = () => {
  return (
    <footer className="footer">
      <div className="container">
        <div className="footer-items">
          <p>&copy; {new Date().getFullYear()} DevChat</p>
          <a href="https://github.com/devchat" target="_blank" rel="noopener noreferrer">
            <FaGithub size={24} className="github-icon" />
          </a>
          <Link href="/terms">
            <span className="footer-link cursor-pointer">Terms</span>
          </Link>
          <Link href="/privacy">
            <span className="footer-link cursor-pointer">Privacy</span>
          </Link>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
