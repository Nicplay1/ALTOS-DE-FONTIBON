
// =============================================
// CARRUSEL PRINCIPAL
// =============================================
(function() {
    function initCarousel() {
        const slides = document.querySelectorAll('.carousel-slide');
        const carouselSlides = document.querySelector('.carousel-slides');
        const controls = document.querySelectorAll('.carousel-control');
        
        if (!slides.length || !carouselSlides) return;

        let currentSlide = 0;
        const totalSlides = slides.length;
        
        carouselSlides.style.transform = `translateX(0)`;

        function goToSlide(index) {
            if (index < 0) index = totalSlides - 1;
            if (index >= totalSlides) index = 0;
            
            currentSlide = index;
            carouselSlides.style.transform = `translateX(-${currentSlide * 25}%)`;
            
            controls.forEach((control, i) => {
                control.classList.toggle('active', i === currentSlide);
            });
        }

        controls.forEach(control => {
            control.addEventListener('click', () => {
                const index = parseInt(control.getAttribute('data-index'));
                goToSlide(index);
            });
        });

        document.addEventListener('click', function(e) {
            if (e.target.closest('.carousel-arrow.prev')) {
                goToSlide(currentSlide - 1);
            }
            if (e.target.closest('.carousel-arrow.next')) {
                goToSlide(currentSlide + 1);
            }
        });

        let slideInterval = setInterval(() => {
            goToSlide(currentSlide + 1);
        }, 5000);

        const carousel = document.querySelector('.carousel');
        carousel.addEventListener('mouseenter', () => {
            clearInterval(slideInterval);
        });

        carousel.addEventListener('mouseleave', () => {
            slideInterval = setInterval(() => {
                goToSlide(currentSlide + 1);
            }, 5000);
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initCarousel);
    } else {
        initCarousel();
    }
})();


// =============================================
// NAVBAR SCROLL EFFECT
// =============================================
(function() {
    function initNavbarScroll() {
        const navbar = document.querySelector('.navbar');
        if (!navbar) return;

        window.addEventListener('scroll', () => {
            const scrollY = window.scrollY;
            const start = 50;
            const end = 400;

            if (scrollY < start) {
                navbar.style.background = `
                    radial-gradient(circle at 20% 30%, rgba(45, 106, 79, 0.05), transparent 60%),
                    radial-gradient(circle at 80% 20%, rgba(26, 74, 58, 0.04), transparent 70%),
                    radial-gradient(circle at 50% 80%, rgba(15, 32, 39, 0.05), transparent 65%),
                    rgba(0, 0, 0, 0.02)
                `;
                navbar.style.backdropFilter = "blur(0px)";
                navbar.style.boxShadow = "none";
                navbar.classList.remove('scrolled', 'solid');
            } 
            else if (scrollY >= start && scrollY <= end) {
                const progress = (scrollY - start) / (end - start);
                const blur = 8 * progress;
                const opacity = 0.1 + (0.5 * progress);

                navbar.style.background = `
                    radial-gradient(circle at 20% 30%, rgba(45, 106, 79, ${opacity + 0.15}), transparent 60%),
                    radial-gradient(circle at 80% 20%, rgba(26, 74, 58, ${opacity + 0.1}), transparent 70%),
                    radial-gradient(circle at 50% 80%, rgba(15, 32, 39, ${opacity}), transparent 65%),
                    linear-gradient(90deg, rgba(15, 32, 39, ${opacity}), rgba(26, 74, 58, ${opacity + 0.1}), rgba(45, 106, 79, ${opacity + 0.15}))
                `;
                navbar.style.backdropFilter = `blur(${blur}px)`;
                navbar.style.boxShadow = `0 2px 10px rgba(0, 0, 0, ${0.1 + 0.05 * progress})`;

                navbar.classList.add('scrolled');
                navbar.classList.remove('solid');
            } 
            else {
                navbar.style.background = `
                    radial-gradient(circle at 75% 30%, rgba(15, 32, 39, 0.35), transparent 60%),
                    radial-gradient(circle at 20% 20%, rgba(26, 74, 58, 0.25), transparent 70%),
                    radial-gradient(circle at 50% 80%, rgba(45, 106, 79, 0.3), transparent 65%),
                    linear-gradient(270deg, #0f2027 0%, #1a4a3a 50%, #2d6a4f 100%)
                `;
                navbar.style.backdropFilter = "blur(0px)";
                navbar.style.boxShadow = "0 2px 15px rgba(0, 0, 0, 0.15)";
                navbar.classList.add('solid');
                navbar.classList.remove('scrolled');
            }
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initNavbarScroll);
    } else {
        initNavbarScroll();
    }
})();

// menu desplegable //
// =============================================
        // MENÚ HAMBURGUESA (NUEVO)
        // =============================================
        const hamburger = document.getElementById('hamburger');
        const sidebarMenu = document.getElementById('sidebarMenu');
        const overlay = document.getElementById('overlay');
        const sidebarLinks = document.querySelectorAll('.sidebar-menu a');

        function toggleMenu() {
            hamburger.classList.toggle('active');
            sidebarMenu.classList.toggle('active');
            overlay.classList.toggle('active');
            document.body.style.overflow = sidebarMenu.classList.contains('active') ? 'hidden' : '';
        }

        hamburger.addEventListener('click', toggleMenu);
        overlay.addEventListener('click', toggleMenu);

        // Cerrar menú al hacer clic en un enlace
        sidebarLinks.forEach(link => {
            link.addEventListener('click', () => {
                toggleMenu();
            });
        });

        // Cerrar menú con tecla ESC
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && sidebarMenu.classList.contains('active')) {
                toggleMenu();
            }
        });

// =============================================
// CONTADORES ANIMADOS
// =============================================
(function() {
    function animarContadores() {
        const contadores = document.querySelectorAll('.numero');
        if (!contadores.length) return;

        const velocidad = 2000;

        contadores.forEach(contador => {
            const target = parseInt(contador.getAttribute('data-target'));
            const incremento = target / (velocidad / 16);
            let current = 0;

            const actualizarContador = () => {
                current += incremento;
                if (current < target) {
                    contador.textContent = Math.ceil(current).toLocaleString();
                    setTimeout(actualizarContador, 16);
                } else {
                    contador.textContent = target.toLocaleString();
                }
            };

            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        actualizarContador();
                        observer.unobserve(entry.target);
                    }
                });
            });

            observer.observe(contador);
        });
    }

    function crearParticulas() {
        const contenedor = document.getElementById('particulas');
        if (!contenedor) return;

        const cantidad = 15;

        for (let i = 0; i < cantidad; i++) {
            const particula = document.createElement('div');
            particula.className = 'particula';
            
            const size = Math.random() * 8 + 2;
            const left = Math.random() * 100;
            const delay = Math.random() * 5;
            const duration = Math.random() * 3 + 3;
            
            particula.style.width = `${size}px`;
            particula.style.height = `${size}px`;
            particula.style.left = `${left}%`;
            particula.style.animationDelay = `${delay}s`;
            particula.style.animationDuration = `${duration}s`;
            
            contenedor.appendChild(particula);
        }
    }

    function initContadores() {
        animarContadores();
        crearParticulas();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initContadores);
    } else {
        initContadores();
    }
})();

// =============================================
// TESTIMONIOS SLIDER
// =============================================
(function() {
    class TestimoniosSlider {
        constructor() {
            this.wrapper = document.getElementById('testimoniosWrapper');
            this.tarjetas = document.querySelectorAll('.testimonio-tarjeta');
            this.indicadores = document.querySelectorAll('.indicador');
            this.prevBtn = document.querySelector('.prev-btn');
            this.nextBtn = document.querySelector('.next-btn');
            
            if (!this.wrapper || !this.tarjetas.length) return;

            this.currentIndex = 0;
            this.totalTarjetas = this.tarjetas.length;
            this.autoScrollInterval = null;
            this.isAutoScrolling = true;
            
            this.init();
        }
        
        init() {
            if (this.prevBtn) {
                this.prevBtn.addEventListener('click', () => this.prev());
            }
            if (this.nextBtn) {
                this.nextBtn.addEventListener('click', () => this.next());
            }
            
            this.indicadores.forEach(indicador => {
                indicador.addEventListener('click', (e) => {
                    const index = parseInt(e.target.getAttribute('data-index'));
                    this.goToSlide(index);
                });
            });
            
            this.wrapper.addEventListener('mouseenter', () => this.pauseAutoScroll());
            this.wrapper.addEventListener('mouseleave', () => this.resumeAutoScroll());
            
            this.startAutoScroll();
            this.updateDisplay();
        }
        
        updateDisplay() {
            const tarjetaWidth = this.tarjetas[0].offsetWidth + 30;
            const desplazamiento = -this.currentIndex * tarjetaWidth;
            this.wrapper.style.transform = `translateX(${desplazamiento}px)`;
            
            this.tarjetas.forEach((tarjeta, index) => {
                tarjeta.classList.toggle('active', index === this.currentIndex);
            });
            
            this.indicadores.forEach((indicador, index) => {
                indicador.classList.toggle('active', index === this.currentIndex);
            });
        }
        
        next() {
            this.currentIndex = (this.currentIndex + 1) % this.totalTarjetas;
            this.updateDisplay();
            this.resetAutoScroll();
        }
        
        prev() {
            this.currentIndex = (this.currentIndex - 1 + this.totalTarjetas) % this.totalTarjetas;
            this.updateDisplay();
            this.resetAutoScroll();
        }
        
        goToSlide(index) {
            this.currentIndex = index;
            this.updateDisplay();
            this.resetAutoScroll();
        }
        
        startAutoScroll() {
            this.autoScrollInterval = setInterval(() => {
                if (this.isAutoScrolling) {
                    this.next();
                }
            }, 5000);
        }
        
        pauseAutoScroll() {
            this.isAutoScrolling = false;
        }
        
        resumeAutoScroll() {
            this.isAutoScrolling = true;
        }
        
        resetAutoScroll() {
            clearInterval(this.autoScrollInterval);
            this.startAutoScroll();
        }
    }
    
    function initTestimonios() {
        new TestimoniosSlider();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initTestimonios);
    } else {
        initTestimonios();
    }
})();

// =============================================
// MODALES Y CARDS
// =============================================
(function() {
    function initModales() {
        // Abrir modales al hacer clic en las cards
        document.querySelectorAll('.card').forEach(card => {
            card.addEventListener('click', () => {
                const cardId = card.getAttribute('data-card');
                const modal = document.getElementById(`modal-${cardId}`);
                if (modal) {
                    modal.classList.add('active');
                    document.body.style.overflow = 'hidden';
                }
            });
        });

        // Cerrar modales
        document.querySelectorAll('.modal-close-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                const modal = btn.closest('.modal-overlay');
                if (modal) {
                    modal.classList.remove('active');
                    document.body.style.overflow = 'auto';
                }
            });
        });

        // Cerrar modal al hacer clic fuera del contenido
        document.querySelectorAll('.modal-overlay').forEach(modal => {
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    modal.classList.remove('active');
                    document.body.style.overflow = 'auto';
                }
            });
        });

        // Funcionalidad del carrusel dentro de los modales
        document.querySelectorAll('.modal-carousel').forEach(carousel => {
            const slidesContainer = carousel.querySelector('.modal-carousel-slides');
            const slides = carousel.querySelectorAll('.modal-carousel-slide');
            const controls = carousel.querySelectorAll('.modal-carousel-control');
            const prevArrow = carousel.querySelector('.modal-carousel-arrow.prev');
            const nextArrow = carousel.querySelector('.modal-carousel-arrow.next');

            if (!slidesContainer || !slides.length) return;

            let currentSlide = 0;
            const totalSlides = slides.length;

            slidesContainer.style.width = `${totalSlides * 100}%`;
            slides.forEach(slide => {
                slide.style.width = `${100 / totalSlides}%`;
            });

            function goToSlide(index) {
                if (index < 0) index = totalSlides - 1;
                if (index >= totalSlides) index = 0;
                currentSlide = index;
                slidesContainer.style.transform = `translateX(-${(100 / totalSlides) * currentSlide}%)`;

                controls.forEach((control, i) => {
                    control.classList.toggle('active', i === currentSlide);
                });
            }

            controls.forEach(control => {
                control.addEventListener('click', () => {
                    const index = parseInt(control.getAttribute('data-index'));
                    goToSlide(index);
                });
            });

            if (prevArrow) {
                prevArrow.addEventListener('click', () => {
                    goToSlide(currentSlide - 1);
                });
            }

            if (nextArrow) {
                nextArrow.addEventListener('click', () => {
                    goToSlide(currentSlide + 1);
                });
            }

            goToSlide(0);
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initModales);
    } else {
        initModales();
    }
})();

// =============================================
// MANEJO DE REDIMENSIONAMIENTO
// =============================================
(function() {
    function handleResize() {
        // Testimonios
        const slider = document.querySelector('.testimonios-wrapper');
        const activeCard = document.querySelector('.testimonio-tarjeta.active');
        if (activeCard && slider) {
            const index = Array.from(document.querySelectorAll('.testimonio-tarjeta')).indexOf(activeCard);
            slider.style.transform = `translateX(-${index * (activeCard.offsetWidth + 30)}px)`;
        }

        // Modales
        document.querySelectorAll('.modal-carousel').forEach(carousel => {
            const slidesContainer = carousel.querySelector('.modal-carousel-slides');
            const slides = carousel.querySelectorAll('.modal-carousel-slide');
            const totalSlides = slides.length;
            
            if (slidesContainer && slides.length) {
                slidesContainer.style.width = `${totalSlides * 100}%`;
                slides.forEach(slide => {
                    slide.style.width = `${100 / totalSlides}%`;
                });
            }
        });
    }

    window.addEventListener('resize', handleResize);
})();