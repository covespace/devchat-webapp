import React from 'react';
import ReactMarkdown from 'react-markdown';
import fs from 'fs';
import path from 'path';
import Footer from '@/components/Footer';
import 'github-markdown-css/github-markdown.css';

interface TermsProps {
  content: string;
}

const Terms: React.FC<TermsProps> = ({ content }) => {
  return (
    <div className="main">
      <div className="container markdown-body">
        <div className="markdown-content-container">
          <ReactMarkdown>{content}</ReactMarkdown>
        </div>
      </div>
      <footer className="footer">
        <Footer />
      </footer>
    </div>
  );
};

export async function getStaticProps() {
  const filePath = path.join(__dirname, 'terms.md');
  const content = fs.readFileSync(filePath, 'utf8');

  return {
    props: {
      content,
    },
  };
}

export default Terms;
