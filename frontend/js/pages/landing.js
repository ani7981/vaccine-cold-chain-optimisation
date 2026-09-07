import { startSimulation } from '../api.js';

export function init() {
  const exploreBtn = document.querySelector('button[onclick="scrollToSimulator()"]');
  if (exploreBtn) {
    exploreBtn.removeAttribute('onclick');
    exploreBtn.innerText = "Start Live Demo";
    exploreBtn.addEventListener('click', async (e) => {
      e.preventDefault();
      try {
        await startSimulation();
      } catch (err) {}
      history.pushState(null, '', '/overview');
      window.dispatchEvent(new Event('popstate'));
    });
  }
}
