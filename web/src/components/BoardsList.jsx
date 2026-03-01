import React from 'react'
import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { getBoards, getStats } from '../api'

function BoardsList() {
  const { data: boards, isLoading: boardsLoading, error: boardsError } = useQuery({
    queryKey: ['boards'],
    queryFn: () => getBoards(),
  })

  const { data: stats } = useQuery({
    queryKey: ['stats'],
    queryFn: () => getStats(),
  })

  if (boardsLoading) {
    return <div className="loading">Loading boards...</div>
  }

  if (boardsError) {
    return <div className="error">Error loading boards: {boardsError.message}</div>
  }

  return (
    <div>
      <h1>Curated Boards</h1>
      
      {stats && (
        <div className="stats">
          <div className="stat">
            <span className="stat-label">Total Repos:</span>
            <span className="stat-value">{stats.total_repos}</span>
          </div>
          <div className="stat">
            <span className="stat-label">Total Boards:</span>
            <span className="stat-value">{stats.total_boards}</span>
          </div>
          <div className="stat">
            <span className="stat-label">Categories:</span>
            <span className="stat-value">{stats.total_categories}</span>
          </div>
        </div>
      )}

      <div className="grid">
        {boards && boards.map((board) => (
          <Link key={board.id} to={`/boards/${board.id}`} className="card">
            <h2>{board.name}</h2>
            <p>{board.description}</p>
            <div className="stats">
              <div className="stat">
                <span className="stat-label">Repos:</span>
                <span className="stat-value">{board.repo_count}</span>
              </div>
              {board.category && (
                <div className="stat">
                  <span className="stat-label">Category:</span>
                  <span className="stat-value">{board.category}</span>
                </div>
              )}
            </div>
          </Link>
        ))}
      </div>

      {(!boards || boards.length === 0) && (
        <div className="loading">No boards found. Run the board generation job to create boards.</div>
      )}
    </div>
  )
}

export default BoardsList

