// Popup script for RepoBoard extension

const API_URL_KEY = 'repoboard_api_url';

async function loadBoards() {
  const boardsDiv = document.getElementById('boards');
  boardsDiv.innerHTML = '<div class="loading">Loading boards...</div>';
  
  const apiUrl = await getApiUrl();
  if (!apiUrl) {
    boardsDiv.innerHTML = '<div class="error">Please set API URL in options</div>';
    return;
  }
  
  try {
    const response = await fetch(`${apiUrl}/boards?limit=10`);
    const boards = await response.json();
    
    if (boards.length === 0) {
      boardsDiv.innerHTML = '<div class="loading">No boards found. Generate boards first!</div>';
      return;
    }
    
    boardsDiv.innerHTML = boards.map(board => `
      <div class="board-item" data-board-id="${board.id}">
        <div class="board-name">${board.name}</div>
        <div class="board-desc">${board.description}</div>
        <div style="font-size: 11px; color: #586069; margin-top: 4px;">
          ${board.repo_count} repositories
        </div>
      </div>
    `).join('');
    
    // Add click handlers
    document.querySelectorAll('.board-item').forEach(item => {
      item.addEventListener('click', () => {
        const boardId = item.dataset.boardId;
        chrome.tabs.create({
          url: `${apiUrl.replace('/api', '')}/boards/${boardId}`
        });
      });
    });
  } catch (error) {
    boardsDiv.innerHTML = `<div class="error">Error: ${error.message}</div>`;
  }
}

async function getApiUrl() {
  const result = await chrome.storage.sync.get(API_URL_KEY);
  return result[API_URL_KEY] || 'http://localhost:8000';
}

document.getElementById('saveUrl').addEventListener('click', async () => {
  const url = document.getElementById('apiUrl').value;
  await chrome.storage.sync.set({ [API_URL_KEY]: url });
  loadBoards();
});

// Load API URL and boards on startup
(async () => {
  const apiUrl = await getApiUrl();
  document.getElementById('apiUrl').value = apiUrl;
  loadBoards();
})();

