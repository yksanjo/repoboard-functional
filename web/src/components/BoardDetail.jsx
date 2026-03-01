import React from 'react'
import { useQuery } from '@tanstack/react-query'
import { useParams, Link } from 'react-router-dom'
import { getBoard } from '../api'

function BoardDetail() {
  const { boardId } = useParams()
  
  const { data: boardData, isLoading, error } = useQuery({
    queryKey: ['board', boardId],
    queryFn: () => getBoard(boardId),
  })

  if (isLoading) {
    return <div className="loading">Loading board...</div>
  }

  if (error) {
    return <div className="error">Error loading board: {error.message}</div>
  }

  if (!boardData) {
    return <div className="error">Board not found</div>
  }

  const { board, repos } = boardData

  return (
    <div>
      <Link to="/">← Back to Boards</Link>
      
      <div className="card" style={{ marginTop: '2rem' }}>
        <h1>{board.name}</h1>
        <p>{board.description}</p>
        <div className="stats" style={{ marginTop: '1rem' }}>
          <div className="stat">
            <span className="stat-label">Repositories:</span>
            <span className="stat-value">{board.repo_count}</span>
          </div>
          {board.category && (
            <div className="stat">
              <span className="stat-label">Category:</span>
              <span className="stat-value">{board.category}</span>
            </div>
          )}
        </div>
      </div>

      <h2 style={{ marginTop: '2rem', marginBottom: '1rem' }}>Repositories</h2>
      
      {repos && repos.length > 0 ? (
        <div>
          {repos.map((item) => {
            const repo = item.repo
            const summary = item.summary
            
            return (
              <Link key={repo.id} to={`/repos/${repo.id}`} className="card">
                <h3>{repo.full_name}</h3>
                {repo.description && <p>{repo.description}</p>}
                
                {summary && (
                  <>
                    <p style={{ marginTop: '0.5rem' }}>{summary.summary}</p>
                    {summary.tags && summary.tags.length > 0 && (
                      <div className="tags">
                        {summary.tags.map((tag, idx) => (
                          <span key={idx} className="tag">{tag}</span>
                        ))}
                      </div>
                    )}
                  </>
                )}
                
                <div className="stats" style={{ marginTop: '1rem' }}>
                  <div className="stat">
                    <span className="stat-label">⭐ Stars:</span>
                    <span className="stat-value">{repo.stars}</span>
                  </div>
                  {summary && (
                    <>
                      <div className="stat">
                        <span className="stat-label">Category:</span>
                        <span className="stat-value">{summary.category}</span>
                      </div>
                      <div className="stat">
                        <span className="stat-label">Skill:</span>
                        <span className="stat-value">{summary.skill_level}</span>
                      </div>
                    </>
                  )}
                </div>
              </Link>
            )
          })}
        </div>
      ) : (
        <div className="loading">No repositories in this board yet.</div>
      )}
    </div>
  )
}

export default BoardDetail

