// frontend/pages/_app.tsx
import '../app/globals.css'
import Layout from '../app/layout'
import type { AppProps } from 'next/app'

function DevChat({ Component, pageProps }: AppProps) {
  return (
    <Layout>
      <Component {...pageProps} />
    </Layout>
  )
}

export default DevChat
