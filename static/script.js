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


function toggleTheme() {
  const currentTheme = document.documentElement.getAttribute("data-theme");
  if (currentTheme === "light") {
    document.documentElement.removeAttribute("data-theme");
    console.log("Switched to dark theme");
  } else {
    document.documentElement.setAttribute("data-theme", "light");
    console.log("Switched to light theme");
  }
}


function toggleTheme() {
  const root = document.documentElement;
  const icon = document.getElementById("theme-icon");
  const isLight = root.getAttribute("data-theme") === "light";

  if (isLight) {
    root.removeAttribute("data-theme");
    icon.classList.replace("fa-sun", "fa-moon");
    console.log("Switched to dark theme");
  } else {
    root.setAttribute("data-theme", "light");
    icon.classList.replace("fa-moon", "fa-sun");
    console.log("Switched to light theme");
  }
}


function toggleTheme() {
  const html = document.documentElement;
  const icon = document.querySelector(".theme-toggle i");
  const isLight = html.getAttribute("data-theme") === "light";
  html.setAttribute("data-theme", isLight ? "dark" : "light");
  icon.className = isLight ? "fa-solid fa-moon" : "fa-solid fa-sun";
}
