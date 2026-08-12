(() => {
  const grid = document.querySelector('.photo-grid');
  if (!grid) return;

  const photos = [...grid.querySelectorAll('.photo-slot')].reverse();
  grid.replaceChildren(...photos);
  photos.forEach((photo, index) => {
    photo.hidden = index > 4;
    photo.classList.remove('photo-slot--large');
    photo.tabIndex = 0;
    photo.setAttribute('role', 'link');
    photo.setAttribute('aria-label', '写真アーカイブを開く');
    const openArchive = () => { window.location.href = '/gallery.html'; };
    photo.addEventListener('click', openArchive);
    photo.addEventListener('keydown', (event) => {
      if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); openArchive(); }
    });
  });
  photos[0]?.classList.add('photo-slot--large');
})();
