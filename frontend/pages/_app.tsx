// frontend/pages/_app.tsx
import '@/styles/globals.css'
import '@/styles/formStyles.css';
import '@/styles/pageStyles.css';

import Layout from '../components/Layout'
import type { AppProps } from 'next/app'

function DevChat({ Component, pageProps }: AppProps) {
  return (
    <Layout>
      <Component {...pageProps} />
    </Layout>
  )
}

export default DevChat
