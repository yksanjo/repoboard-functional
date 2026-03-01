import React, { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { searchRepos } from '../api'

function Search() {
  const [query, setQuery] = useState('')
  const [searchTerm, setSearchTerm] = useState('')

  const { data: results, isLoading, error } = useQuery({
    queryKey: ['search', searchTerm],
    queryFn: () => searchRepos(searchTerm),
    enabled: searchTerm.length > 0,
  })

  const handleSubmit = (e) => {
    e.preventDefault()
    setSearchTerm(query)
  }

  return (
    <div>
      <h1>Search Repositories</h1>
      
      <form onSubmit={handleSubmit} style={{ marginBottom: '2rem' }}>
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search by name, description, or tags..."
          style={{
            width: '100%',
            maxWidth: '500px',
            padding: '0.75rem',
            fontSize: '1rem',
            border: '1px solid #e1e4e8',
            borderRadius: '6px',
          }}
        />
        <button
          type="submit"
          style={{
            marginLeft: '0.5rem',
            padding: '0.75rem 1.5rem',
            fontSize: '1rem',
            backgroundColor: '#0366d6',
            color: 'white',
            border: 'none',
            borderRadius: '6px',
            cursor: 'pointer',
          }}
        >
          Search
        </button>
      </form>

      {isLoading && <div className="loading">Searching...</div>}
      
      {error && <div className="error">Error searching: {error.message}</div>}

      {results && (
        <>
          <p style={{ marginBottom: '1rem', color: '#586069' }}>
            Found {results.length} repositories
          </p>
          
          {results.length > 0 ? (
            <div>
              {results.map((item) => {
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
                        <div className="stat">
                          <span className="stat-label">Category:</span>
                          <span className="stat-value">{summary.category}</span>
                        </div>
                      )}
                    </div>
                  </Link>
                )
              })}
            </div>
          ) : (
            <div className="loading">No repositories found. Try a different search term.</div>
          )}
        </>
      )}
    </div>
  )
}

export default Search

