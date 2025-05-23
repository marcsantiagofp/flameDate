const profileCard = document.querySelector('.profile-card');

let currentProfileIndex = 0;
let currentImageIndex = 0;

const profiles = [
  {
    name: "MARC",
    age: 20,
    distance: "a 1 km de distancia...",
    description: "✨ LO QUE SURJA",
    images: [
      "img/perfil.svg",
      "img/perfil2.png",
      "img/perfil3.png"
    ]
  },
  {
    name: "RAQUEL",
    age: 22,
    distance: "a 3 km de distancia...",
    description: "😍 RELACIÓN ESTABLE",
    images: [
      "img/perfil.svg",
      "img/perfil2.png",
      "img/perfil3.png"
    ]
  },
  {
    name: "CARLA",
    age: 24,
    distance: "a 5 km de distancia...",
    description: "😅 ROLLOS CORTOS",
    images: [
      "img/perfil.svg",
      "img/perfil2.png",
      "img/perfil3.png"
    ]
  }
];

function loadProfile(profile) {
  const carousel = document.querySelector('.image-carousel');
  const indicatorsContainer = document.querySelector('.image-indicators');
  const nameAge = document.querySelector('.name-age');
  const distance = document.querySelector('.distance');
  const description = document.querySelector('.description');

  // Limpiar contenido anterior
  carousel.innerHTML = `
    <div class="click-zone left-zone"></div>
    <div class="click-zone right-zone"></div>
    <div class="image-indicators"></div>
  `;

  const indicators = carousel.querySelector('.image-indicators');

  profile.images.forEach((src, i) => {
    const img = document.createElement('img');
    img.src = src;
    img.className = 'card-img' + (i === 0 ? ' active' : '');
    img.alt = `Foto ${i + 1}`;
    carousel.insertBefore(img, carousel.querySelector('.click-zone'));

    const dot = document.createElement('div');
    dot.className = 'indicator' + (i === 0 ? ' active' : '');
    indicators.appendChild(dot);
  });

  currentImageIndex = 0;
  nameAge.innerHTML = `${profile.name} <span class="age">${profile.age}</span>`;
  distance.textContent = profile.distance;
  description.textContent = profile.description;

  setupImageClickEvents();
  setupButtonEvents(); // 👈 Añadir eventos a los botones actuales
}

function setupButtonEvents() {
  const likeBtn = document.querySelector('[aria-label="Like"]');
  const nopeBtn = document.querySelector('[aria-label="Nope"]');

  likeBtn?.addEventListener('click', () => swipeCard('right'));
  nopeBtn?.addEventListener('click', () => swipeCard('left'));
}

function setupImageClickEvents() {
  const imgs = document.querySelectorAll('.card-img');
  const indicators = document.querySelectorAll('.indicator');
  const leftZone = document.querySelector('.left-zone');
  const rightZone = document.querySelector('.right-zone');

  imgs.forEach((img, i) => {
    img.addEventListener('click', (e) => {
      const rect = img.getBoundingClientRect();
      const clickX = e.clientX - rect.left;

      if (clickX < rect.width / 2) {
        prevImage(imgs, indicators);
      } else {
        nextImage(imgs, indicators);
      }
    });
  });

  leftZone?.addEventListener('click', () => prevImage(imgs, indicators));
  rightZone?.addEventListener('click', () => nextImage(imgs, indicators));
}

function swipeCard(direction) {
  const animClass = direction === 'left' ? 'swipe-left' : 'swipe-right';
  profileCard.classList.add(animClass);

  setTimeout(() => {
    profileCard.classList.remove(animClass);

    currentProfileIndex++;
    if (currentProfileIndex < profiles.length) {
      loadProfile(profiles[currentProfileIndex]);
    } else {
      showNoMoreMessage();
    }
  }, 500);
}

function showNoMoreMessage() {
  const carousel = document.querySelector('.image-carousel');
  const cardInfo = document.querySelector('.card-info');

  carousel?.remove();
  cardInfo?.remove();

  const noMoreDiv = document.createElement('div');
  noMoreDiv.className = 'no-more-card text-center p-5';
  noMoreDiv.innerHTML = `
    <h2 class="text-white"> ¡No hay más personas cerca!</h2>
    <p class="text-white-50">Actualiza el rango de distancia para descubrir nuevos perfiles.</p>
  `;

  profileCard?.appendChild(noMoreDiv);
}

function nextImage(imgs, indicators) {
  if (currentImageIndex < imgs.length - 1) {
    imgs[currentImageIndex].classList.remove('active');
    indicators[currentImageIndex].classList.remove('active');
    currentImageIndex++;
    imgs[currentImageIndex].classList.add('active');
    indicators[currentImageIndex].classList.add('active');
  }
}

function prevImage(imgs, indicators) {
  if (currentImageIndex > 0) {
    imgs[currentImageIndex].classList.remove('active');
    indicators[currentImageIndex].classList.remove('active');
    currentImageIndex--;
    imgs[currentImageIndex].classList.add('active');
    indicators[currentImageIndex].classList.add('active');
  }
}

// Inicializar al cargar la página
window.addEventListener('DOMContentLoaded', () => {
  loadProfile(profiles[currentProfileIndex]);
});