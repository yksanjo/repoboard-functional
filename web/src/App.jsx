import React from 'react'
import { Routes, Route, Link } from 'react-router-dom'
import BoardsList from './components/BoardsList'
import BoardDetail from './components/BoardDetail'
import RepoDetail from './components/RepoDetail'
import Search from './components/Search'
import './App.css'

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <div className="container">
          <Link to="/" className="logo">
            <h1>RepoBoard</h1>
          </Link>
          <nav>
            <Link to="/">Boards</Link>
            <Link to="/search">Search</Link>
          </nav>
        </div>
      </header>

      <main className="container">
        <Routes>
          <Route path="/" element={<BoardsList />} />
          <Route path="/boards/:boardId" element={<BoardDetail />} />
          <Route path="/repos/:repoId" element={<RepoDetail />} />
          <Route path="/search" element={<Search />} />
        </Routes>
      </main>

      <footer>
        <div className="container">
          <p>RepoBoard - GitHub Repository Curation AI</p>
        </div>
      </footer>
    </div>
  )
}

export default App

