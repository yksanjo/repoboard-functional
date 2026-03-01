import React from 'react'
import { useQuery } from '@tanstack/react-query'
import { useParams } from 'react-router-dom'
import { getRepo } from '../api'

function RepoDetail() {
  const { repoId } = useParams()
  
  const { data: repoData, isLoading, error } = useQuery({
    queryKey: ['repo', repoId],
    queryFn: () => getRepo(repoId),
  })

  if (isLoading) {
    return <div className="loading">Loading repository...</div>
  }

  if (error) {
    return <div className="error">Error loading repository: {error.message}</div>
  }

  if (!repoData) {
    return <div className="error">Repository not found</div>
  }

  const { repo, summary } = repoData

  return (
    <div>
      <div className="card">
        <h1>{repo.full_name}</h1>
        <p>
          <a href={repo.url} target="_blank" rel="noopener noreferrer">
            View on GitHub →
          </a>
        </p>
        
        {repo.description && <p style={{ marginTop: '1rem', fontSize: '1.1rem' }}>{repo.description}</p>}
        
        {summary && (
          <>
            <h2 style={{ marginTop: '2rem' }}>Summary</h2>
            <p>{summary.summary}</p>
            
            <h3 style={{ marginTop: '1.5rem' }}>Details</h3>
            <div className="stats">
              <div className="stat">
                <span className="stat-label">Category:</span>
                <span className="stat-value">{summary.category}</span>
              </div>
              <div className="stat">
                <span className="stat-label">Skill Level:</span>
                <span className="stat-value">{summary.skill_level} ({summary.skill_level_numeric}/10)</span>
              </div>
              <div className="stat">
                <span className="stat-label">Project Health:</span>
                <span className="stat-value">{summary.project_health}</span>
              </div>
            </div>
            
            {summary.tags && summary.tags.length > 0 && (
              <>
                <h3 style={{ marginTop: '1.5rem' }}>Tags</h3>
                <div className="tags">
                  {summary.tags.map((tag, idx) => (
                    <span key={idx} className="tag">{tag}</span>
                  ))}
                </div>
              </>
            )}
            
            {summary.use_cases && summary.use_cases.length > 0 && (
              <>
                <h3 style={{ marginTop: '1.5rem' }}>Use Cases</h3>
                <ul style={{ marginLeft: '1.5rem', lineHeight: '1.8' }}>
                  {summary.use_cases.map((useCase, idx) => (
                    <li key={idx}>{useCase}</li>
                  ))}
                </ul>
              </>
            )}
          </>
        )}
        
        <h3 style={{ marginTop: '1.5rem' }}>Statistics</h3>
        <div className="stats">
          <div className="stat">
            <span className="stat-label">⭐ Stars:</span>
            <span className="stat-value">{repo.stars}</span>
          </div>
          <div className="stat">
            <span className="stat-label">🍴 Forks:</span>
            <span className="stat-value">{repo.forks}</span>
          </div>
          <div className="stat">
            <span className="stat-label">👀 Watchers:</span>
            <span className="stat-value">{repo.watchers}</span>
          </div>
          <div className="stat">
            <span className="stat-label">📝 Issues:</span>
            <span className="stat-value">{repo.open_issues}</span>
          </div>
        </div>
        
        {repo.languages && Object.keys(repo.languages).length > 0 && (
          <>
            <h3 style={{ marginTop: '1.5rem' }}>Languages</h3>
            <div className="tags">
              {Object.entries(repo.languages)
                .sort((a, b) => b[1] - a[1])
                .slice(0, 10)
                .map(([lang, percent]) => (
                  <span key={lang} className="tag">
                    {lang} ({Math.round(percent * 100)}%)
                  </span>
                ))}
            </div>
          </>
        )}
      </div>
    </div>
  )
}

export default RepoDetail

