import React from 'react';
import ReactMarkdown from 'react-markdown';
import fs from 'fs';
import path from 'path';
import Footer from '@/components/Footer';

interface TermsProps {
  content: string;
}

const Terms: React.FC<TermsProps> = ({ content }) => {
  return (
    <div className="container">
      <ReactMarkdown>{content}</ReactMarkdown>
      <Footer />
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
