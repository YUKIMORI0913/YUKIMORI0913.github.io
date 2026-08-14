(() => {
  const grid = document.querySelector('.photo-grid');
  if (!grid) return;
  const makeFigure = (photo, index) => {
    const figure = document.createElement('figure');
    figure.className = `photo-slot${index === 0 ? ' photo-slot--large' : ''}`;
    figure.tabIndex = 0; figure.setAttribute('role', 'link'); figure.setAttribute('aria-label', '写真アーカイブを開く');
    const image = new Image(); image.src = photo.thumbnail_url; image.alt = photo.alt_text || photo.title || '鰻谷饅頭 Photo Archive'; image.width = photo.width; image.height = photo.height; image.loading = index ? 'lazy' : 'eager'; image.decoding = 'async';
    const caption = document.createElement('figcaption'); caption.textContent = photo.title || `ARCHIVE ${String(photo.sort_order).padStart(2, '0')}`;
    figure.append(image, caption);
    const open = () => { window.location.href = '/gallery.html'; }; figure.addEventListener('click', open); figure.addEventListener('keydown', event => { if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); open(); } });
    return figure;
  };
  fetch('/assets/data/photos.json', { cache: 'no-store' }).then(response => {
    if (!response.ok) throw new Error('archive metadata unavailable');
    return response.json();
  }).then(data => {
    const photos = data.photos.filter(photo => photo.is_published !== false).sort((a, b) => b.sort_order - a.sort_order).slice(0, 5);
    grid.replaceChildren(...photos.map(makeFigure));
  }).catch(() => { grid.innerHTML = '<p class="notice">写真アーカイブを読み込めませんでした。</p>'; });
})();
