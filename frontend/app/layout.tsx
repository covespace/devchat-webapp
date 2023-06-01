// frontend/app/layout.tsx
import React, { ReactNode } from 'react'

interface LayoutProps {
  children: ReactNode
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  return (
    <div>
      {/* Add your common layout components here */}
      {children}
    </div>
  )
}

export default Layout
