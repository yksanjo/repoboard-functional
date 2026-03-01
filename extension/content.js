// Content script to add RepoBoard features to GitHub pages

const API_URL_KEY = 'repoboard_api_url';

async function getApiUrl() {
  const result = await chrome.storage.sync.get(API_URL_KEY);
  return result[API_URL_KEY] || 'http://localhost:8000';
}

// Add "Similar Repos" section to GitHub repo pages
async function addSimilarRepos() {
  if (!window.location.pathname.match(/^\/[\w-]+\/[\w-]+$/)) {
    return; // Not a repo page
  }
  
  const apiUrl = await getApiUrl();
  const repoName = window.location.pathname.slice(1);
  
  // Check if already added
  if (document.getElementById('repoboard-similar')) {
    return;
  }
  
  try {
    // Search for similar repos
    const response = await fetch(`${apiUrl}/search?q=${repoName}&limit=5`);
    const repos = await response.json();
    
    if (repos.length === 0) return;
    
    // Find sidebar
    const sidebar = document.querySelector('.Layout-sidebar');
    if (!sidebar) return;
    
    // Create similar repos section
    const similarDiv = document.createElement('div');
    similarDiv.id = 'repoboard-similar';
    similarDiv.className = 'BorderGrid-row';
    similarDiv.innerHTML = `
      <div class="BorderGrid-cell">
        <h2 class="h4 mb-3">🔍 Similar Repositories</h2>
        <div class="repoboard-repos">
          ${repos.slice(0, 5).map(repo => `
            <div class="repoboard-repo-item">
              <a href="${repo.repo.url}" target="_blank" class="text-bold">
                ${repo.repo.full_name}
              </a>
              ${repo.summary ? `<p class="text-small color-fg-muted">${repo.summary.summary.substring(0, 100)}...</p>` : ''}
            </div>
          `).join('')}
        </div>
        <a href="${apiUrl.replace('/api', '')}" target="_blank" class="btn btn-sm mt-2">
          View on RepoBoard →
        </a>
      </div>
    `;
    
    // Add styles
    if (!document.getElementById('repoboard-styles')) {
      const style = document.createElement('style');
      style.id = 'repoboard-styles';
      style.textContent = `
        .repoboard-repo-item {
          padding: 8px 0;
          border-bottom: 1px solid #e1e4e8;
        }
        .repoboard-repo-item:last-child {
          border-bottom: none;
        }
        .repoboard-repo-item a {
          text-decoration: none;
        }
        .repoboard-repo-item a:hover {
          text-decoration: underline;
        }
      `;
      document.head.appendChild(style);
    }
    
    // Insert before "About" section or at end
    const aboutSection = sidebar.querySelector('.BorderGrid-row');
    if (aboutSection) {
      sidebar.insertBefore(similarDiv, aboutSection);
    } else {
      sidebar.appendChild(similarDiv);
    }
  } catch (error) {
    console.error('RepoBoard error:', error);
  }
}

// Run when page loads
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', addSimilarRepos);
} else {
  addSimilarRepos();
}

// Re-run on navigation (GitHub uses SPA)
let lastUrl = location.href;
new MutationObserver(() => {
  const url = location.href;
  if (url !== lastUrl) {
    lastUrl = url;
    setTimeout(addSimilarRepos, 1000);
  }
}).observe(document, { subtree: true, childList: true });

