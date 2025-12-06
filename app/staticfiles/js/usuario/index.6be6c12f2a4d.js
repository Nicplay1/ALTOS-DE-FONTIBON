// JavaScript personalizado para el efecto del navbar
const navbar = document.getElementById('mainNavbar');
const navbarCollapse = document.getElementById('navbarNav');
const navbarToggler = document.querySelector('.navbar-toggler');

// Estado para rastrear si el menú está abierto
let isMenuOpen = false;

// Efecto de scroll para el navbar
window.addEventListener('scroll', function() {
    if (isMenuOpen) return; // No cambiar el color si el menú está abierto
    
    if (window.scrollY > 100) {
        navbar.classList.remove('navbar-transparent');
        navbar.classList.add('navbar-solid');
    } else {
        navbar.classList.remove('navbar-solid');
        navbar.classList.add('navbar-transparent');
    }
});

// Controlar el color del navbar cuando se despliega el menú hamburguesa
navbarToggler.addEventListener('click', function() {
    if (!navbarCollapse.classList.contains('show')) {
        // Si el menú se va a abrir, aplicar el color sólido
        navbar.classList.remove('navbar-transparent');
        navbar.classList.add('navbar-expanded');
        isMenuOpen = true;
    } else {
        // Si el menú se va a cerrar, verificar la posición de scroll
        if (window.scrollY <= 100) {
            navbar.classList.remove('navbar-expanded');
            navbar.classList.add('navbar-transparent');
        } else {
            navbar.classList.remove('navbar-expanded');
            navbar.classList.add('navbar-solid');
        }
        isMenuOpen = false;
    }
});

// Cerrar el menú al hacer clic en un enlace (en dispositivos móviles)
const navLinks = document.querySelectorAll('.nav-link, .btn-login');
navLinks.forEach(link => {
    link.addEventListener('click', () => {
        if (window.innerWidth < 992) {
            const bsCollapse = new bootstrap.Collapse(navbarCollapse, {
                toggle: false
            });
            bsCollapse.hide();
            
            // Restaurar el estado del navbar después de cerrar el menú
            setTimeout(() => {
                if (window.scrollY <= 100) {
                    navbar.classList.remove('navbar-expanded');
                    navbar.classList.add('navbar-transparent');
                } else {
                    navbar.classList.remove('navbar-expanded');
                    navbar.classList.add('navbar-solid');
                }
                isMenuOpen = false;
            }, 350);
        }
    });
});

// Manejar el evento de Bootstrap para cuando el menú se cierra
navbarCollapse.addEventListener('hidden.bs.collapse', function() {
    if (window.scrollY <= 100) {
        navbar.classList.remove('navbar-expanded');
        navbar.classList.add('navbar-transparent');
    } else {
        navbar.classList.remove('navbar-expanded');
        navbar.classList.add('navbar-solid');
    }
    isMenuOpen = false;
});

// Manejar el evento de Bootstrap para cuando el menú se abre
navbarCollapse.addEventListener('shown.bs.collapse', function() {
    navbar.classList.remove('navbar-transparent');
    navbar.classList.add('navbar-expanded');
    isMenuOpen = true;
});

// Contador animado
function animateCounter(element, target) {
    let current = 0;
    const increment = target / 100;
    const timer = setInterval(() => {
        current += increment;
        if (current >= target) {
            element.textContent = target.toLocaleString();
            clearInterval(timer);
        } else {
            element.textContent = Math.floor(current).toLocaleString();
        }
    }, 20);
}

// Observador para activar contadores cuando sean visibles
const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            const counters = entry.target.querySelectorAll('.contador-numero');
            counters.forEach(counter => {
                const target = parseInt(counter.getAttribute('data-target'));
                animateCounter(counter, target);
            });
            observer.unobserve(entry.target);
        }
    });
}, { threshold: 0.5 });

// Observar la sección de contadores
const contadoresSection = document.getElementById('contadores');
observer.observe(contadoresSection);

// JavaScript para el carrusel de reseñas
document.addEventListener('DOMContentLoaded', function() {
    const reseñasTrack = document.getElementById('reseñasTrack');
    const reseñasCards = document.querySelectorAll('.reseña-card');
    const prevBtn = document.getElementById('prevReseña');
    const nextBtn = document.getElementById('nextReseña');
    const indicatorsContainer = document.getElementById('reseñasIndicators');
    
    let currentIndex = 0;
    
    // Crear indicadores
    reseñasCards.forEach((_, index) => {
        const indicator = document.createElement('div');
        indicator.classList.add('reseñas-indicator');
        if (index === 0) indicator.classList.add('active');
        indicator.addEventListener('click', () => {
            goToSlide(index);
        });
        indicatorsContainer.appendChild(indicator);
    });
    
    // Función para ir a un slide específico
    function goToSlide(index) {
        currentIndex = index;
        updateCarousel();
    }
    
    // Función para actualizar el carrusel
    function updateCarousel() {
        // Calcular el ancho de la tarjeta incluyendo márgenes
        const cardStyle = getComputedStyle(reseñasCards[0]);
        const cardMarginLeft = parseFloat(cardStyle.marginLeft);
        const cardMarginRight = parseFloat(cardStyle.marginRight);
        const cardWidth = reseñasCards[0].offsetWidth + cardMarginLeft + cardMarginRight;
        
        // Calcular el desplazamiento para centrar la card activa
        const containerWidth = reseñasTrack.parentElement.offsetWidth;
        const offset = (containerWidth / 2) - (cardWidth / 2) - (currentIndex * cardWidth);
        reseñasTrack.style.transform = `translateX(${offset}px)`;
        
        // Actualizar clases activas
        reseñasCards.forEach((card, index) => {
            if (index === currentIndex) {
                card.classList.add('active');
            } else {
                card.classList.remove('active');
            }
        });
        
        // Actualizar indicadores
        const indicators = document.querySelectorAll('.reseñas-indicator');
        indicators.forEach((indicator, index) => {
            if (index === currentIndex) {
                indicator.classList.add('active');
            } else {
                indicator.classList.remove('active');
            }
        });
    }
    
    // Event listeners para los botones
    prevBtn.addEventListener('click', () => {
        if (currentIndex > 0) {
            currentIndex--;
        } else {
            currentIndex = reseñasCards.length - 1;
        }
        updateCarousel();
    });
    
    nextBtn.addEventListener('click', () => {
        if (currentIndex < reseñasCards.length - 1) {
            currentIndex++;
        } else {
            currentIndex = 0;
        }
        updateCarousel();
    });
    
    // Inicializar el carrusel
    updateCarousel();
    
    // Cambio automático cada 5 segundos
    setInterval(() => {
        if (currentIndex < reseñasCards.length - 1) {
            currentIndex++;
        } else {
            currentIndex = 0;
        }
        updateCarousel();
    }, 5000);
    
    // Ajustar el carrusel al redimensionar la ventana
    window.addEventListener('resize', updateCarousel);
});

// Smooth scrolling para los enlaces internos
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        
        const targetId = this.getAttribute('href');
        if(targetId === '#') return;
        
        const targetElement = document.querySelector(targetId);
        if(targetElement) {
            window.scrollTo({
                top: targetElement.offsetTop - 70,
                behavior: 'smooth'
            });
        }
    });
});