// blog.js - Carrusel y animaciones para la sección de comunidad/blog

document.addEventListener('DOMContentLoaded', function() {
  // Inicializar carrusel de blogs si existe
  if (typeof Swiper !== 'undefined') {
    new Swiper('.blogSwiper', {
      slidesPerView: 1,
      spaceBetween: 32,
      loop: true,
      navigation: {
        nextEl: '.swiper-button-next',
        prevEl: '.swiper-button-prev',
      },
      pagination: {
        el: '.swiper-pagination',
        clickable: true,
      },
      breakpoints: {
        640: { slidesPerView: 1 },
        768: { slidesPerView: 2 },
        1024: { slidesPerView: 4 },
      },
    });
  }
  // Aquí puedes agregar animaciones para las tarjetas de blog
}); 