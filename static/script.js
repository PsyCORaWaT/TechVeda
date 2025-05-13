// alert("It's Working")
// if (typeof flashMessages !== 'undefined' && flashMessages.length > 0) {
//     flashMessages.forEach(function(message) {
//         alert(message); // or use your own custom alert logic
//     });
// }



// Flash Message Auto Hide
window.addEventListener("DOMContentLoaded", () => {
  const flash = document.getElementById("flash");
  if (flash) {
    setTimeout(() => {
      flash.style.display = "none";
    }, 4000);
  }
});

// Carousel Drag Scroll
const carousel = document.querySelector(".carousel");
if (carousel) {
  let isDown = false;
  let startX;
  let scrollLeft;

  carousel.addEventListener("mousedown", (e) => {
    isDown = true;
    carousel.classList.add("active");
    startX = e.pageX - carousel.offsetLeft;
    scrollLeft = carousel.scrollLeft;
  });
  carousel.addEventListener("mouseleave", () => {
    isDown = false;
    carousel.classList.remove("active");
  });
  carousel.addEventListener("mouseup", () => {
    isDown = false;
    carousel.classList.remove("active");
  });
  carousel.addEventListener("mousemove", (e) => {
    if (!isDown) return;
    e.preventDefault();
    const x = e.pageX - carousel.offsetLeft;
    const walk = (x - startX) * 2; // scroll speed
    carousel.scrollLeft = scrollLeft - walk;
  });
}

// Theme Toggle
function toggleTheme() {
  const html = document.documentElement;
  const icon = document.querySelector(".theme-toggle i");
  const isLight = html.getAttribute("data-theme") === "light";
  html.setAttribute("data-theme", isLight ? "dark" : "light");
  icon.className = isLight ? "fa-solid fa-moon" : "fa-solid fa-sun";

  // Save theme preference in localStorage
  localStorage.setItem("theme", isLight ? "dark" : "light");
}

// Apply saved theme on page load
window.addEventListener("DOMContentLoaded", () => {
  const savedTheme = localStorage.getItem("theme") || "light";
  document.documentElement.setAttribute("data-theme", savedTheme);
  const icon = document.querySelector(".theme-toggle i");
  icon.className = savedTheme === "light" ? "fa-solid fa-moon" : "fa-solid fa-sun";
});


  // Animate icons with a bounce effect
  document.querySelectorAll('.signup-animate-icon').forEach(function(icon, i) {
    icon.animate([
      { transform: 'scale(1) rotate(0deg)' },
      { transform: 'scale(1.18) rotate(-8deg)' },
      { transform: 'scale(1) rotate(0deg)' }
    ], {
      duration: 1200 + i * 200,
      iterations: Infinity,
      direction: 'alternate',
      easing: 'ease-in-out',
      delay: i * 200
    });
  });

