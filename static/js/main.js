// main.js para bycint Cosméticos
console.log('JS cargado correctamente.');
// Animaciones generales y utilidades globales aquí
// Para lógica de tienda, catálogo o blog, ver tienda.js, catalogo_categoria.js y blog.js
// Aquí puedes agregar interactividad personalizada para tu tienda 

if (document.querySelector('.productosSwiper')) {
  new Swiper('.productosSwiper', {
    slidesPerView: 1,
    spaceBetween: 20,
    loop: true,
    navigation: {
      nextEl: '.swiper-button-next',
      prevEl: '.swiper-button-prev',
    },
    pagination: {
      el: '.swiper-pagination',
      clickable: true,
      dynamicBullets: false
    },
    autoplay: {
      delay: 10000, // 10 segundos
      disableOnInteraction: false,
    },
    breakpoints: {
      640: { slidesPerView: 2, slidesPerGroup: 2 },
      1024: { slidesPerView: 5, slidesPerGroup: 5 },
    },
    slidesPerGroup: 1,
  });
}

// Funcionalidad para botón de favorito en productos destacados
if (document.querySelectorAll('.btn-fav').length) {
  document.querySelectorAll('.btn-fav').forEach(btn => {
    btn.addEventListener('click', function(e) {
      e.preventDefault();
      const icon = this.querySelector('i');
      if (icon.classList.contains('fa-regular')) {
        icon.classList.remove('fa-regular', 'text-gray-300');
        icon.classList.add('fa-solid', 'text-red-500');
      } else {
        icon.classList.remove('fa-solid', 'text-red-500');
        icon.classList.add('fa-regular', 'text-gray-300');
      }
    });
  });
} 