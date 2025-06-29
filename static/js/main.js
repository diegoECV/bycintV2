// main.js para bycint Cosméticos
console.log('JS cargado correctamente.');
// Animaciones generales y utilidades globales aquí
// Para lógica de tienda, catálogo o blog, ver tienda.js, catalogo_categoria.js y blog.js
// Aquí puedes agregar interactividad personalizada para tu tienda 

if (document.querySelector('.productosSwiper')) {
  const swiper = new Swiper('.productosSwiper', {
    slidesPerView: 4,
    slidesPerGroup: 4,
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
      delay: 7000, // 7 segundos
      disableOnInteraction: false,
    }
  });
  // Detener autoplay al pasar el mouse
  const carrusel = document.querySelector('.productosSwiper');
  carrusel.addEventListener('mouseenter', () => swiper.autoplay.stop());
  carrusel.addEventListener('mouseleave', () => swiper.autoplay.start());
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