// index.js

document.addEventListener('DOMContentLoaded', function() {
    // Hero Carrusel
    const heroCarouselInner = document.getElementById('heroCarouselInner');
    const heroPrevBtn = document.getElementById('heroCarouselPrev');
    const heroNextBtn = document.getElementById('heroCarouselNext');
    const heroDots = [
        document.getElementById('heroDot0'),
        document.getElementById('heroDot1'),
        document.getElementById('heroDot2')
    ];
    let heroCurrent = 0;
    const heroTotal = 3;

    function updateHeroCarousel() {
        heroCarouselInner.style.transform = `translateX(-${heroCurrent * 100}%)`;
        heroDots.forEach((dot, i) => {
            dot.classList.toggle('bg-red-500', i === heroCurrent);
            dot.classList.toggle('bg-gray-300', i !== heroCurrent);
        });
    }
    if(heroPrevBtn && heroNextBtn && heroCarouselInner) {
        heroPrevBtn.addEventListener('click', () => {
            heroCurrent = (heroCurrent - 1 + heroTotal) % heroTotal;
            updateHeroCarousel();
        });
        heroNextBtn.addEventListener('click', () => {
            heroCurrent = (heroCurrent + 1) % heroTotal;
            updateHeroCarousel();
        });
        heroDots.forEach((dot, i) => {
            dot.addEventListener('click', () => {
                heroCurrent = i;
                updateHeroCarousel();
            });
        });
        setInterval(() => {
            heroCurrent = (heroCurrent + 1) % heroTotal;
            updateHeroCarousel();
        }, 7000);
    }

    // Swiper para productos destacados
    if(document.querySelector('.productosSwiper')) {
        new Swiper('.productosSwiper', {
            slidesPerView: 4,
            spaceBetween: 20,
            loop: true,
            slidesPerGroup: 4,
            autoplay: {
                delay: 4000,
                disableOnInteraction: false
            },
            navigation: {
                nextEl: '.swiper-button-next',
                prevEl: '.swiper-button-prev',
            },
            pagination: {
                el: '.swiper-pagination',
                clickable: true,
            }
        });
    }
}); 