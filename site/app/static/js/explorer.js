/**
 * OpenProblemAtlas Explorer — client-side search and filter
 */

document.addEventListener('DOMContentLoaded', () => {
  const searchInput = document.getElementById('search-input');
  const filterBtns = document.querySelectorAll('.filter-btn');
  const problemCards = document.querySelectorAll('.problem-card');

  let activeFilters = {
    domain: null,
    status: null,
    type: null,
    special: null,
  };

  // Search
  if (searchInput) {
    searchInput.addEventListener('input', (e) => {
      const query = e.target.value.toLowerCase().trim();
      applyFilters(query);
    });
  }

  // Filter buttons
  filterBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      const filterKey = btn.dataset.filterKey;
      const filterVal = btn.dataset.filterValue;

      if (activeFilters[filterKey] === filterVal) {
        activeFilters[filterKey] = null;
        btn.classList.remove('active');
      } else {
        // Deactivate other buttons in same group
        filterBtns.forEach(b => {
          if (b.dataset.filterKey === filterKey) {
            b.classList.remove('active');
          }
        });
        activeFilters[filterKey] = filterVal;
        btn.classList.add('active');
      }

      applyFilters(searchInput ? searchInput.value.toLowerCase().trim() : '');
    });
  });

  function checkSpecialFilter(card, filterValue) {
    if (!filterValue) return true;

    if (filterValue === 'underexplored') {
      var scoreUnderexplored = parseFloat(card.dataset.scoreUnderexplored) || 0;
      var scoreImpact = parseFloat(card.dataset.scoreImpact) || 0;
      return scoreUnderexplored > 0.3 && scoreImpact > 0.5;
    }

    if (filterValue === 'formalizable') {
      var wanted = card.dataset.formalizationWanted === 'True';
      var available = card.dataset.formalizationAvailable === 'True';
      return wanted || available;
    }

    if (filterValue === 'solver-ready') {
      return card.dataset.solverReady === 'True';
    }

    return true;
  }

  function applyFilters(searchQuery) {
    let visibleCount = 0;

    problemCards.forEach(card => {
      const title = (card.dataset.title || '').toLowerCase();
      const domain = card.dataset.domain || '';
      const status = card.dataset.status || '';
      const ptype = card.dataset.type || '';
      const statement = (card.dataset.statement || '').toLowerCase();

      let visible = true;

      // Search
      if (searchQuery && !title.includes(searchQuery) && !statement.includes(searchQuery)) {
        visible = false;
      }

      // Standard filters
      if (activeFilters.domain && domain !== activeFilters.domain) visible = false;
      if (activeFilters.status && status !== activeFilters.status) visible = false;
      if (activeFilters.type && ptype !== activeFilters.type) visible = false;

      // Special filter
      if (visible && activeFilters.special) {
        visible = checkSpecialFilter(card, activeFilters.special);
      }

      card.style.display = visible ? '' : 'none';
      if (visible) visibleCount++;
    });

    // Update count
    const countEl = document.getElementById('result-count');
    if (countEl) {
      countEl.textContent = `${visibleCount} problem${visibleCount !== 1 ? 's' : ''}`;
    }
  }
});
