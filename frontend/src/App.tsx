import { useState } from 'react'
import { Dashboard, type PageId } from './pages/Dashboard'
import './index.css'

function App() {
  const [activePage, setActivePage] = useState<PageId>('dashboard')
  return <Dashboard activePage={activePage} onNavigate={setActivePage} />
}

export default App
