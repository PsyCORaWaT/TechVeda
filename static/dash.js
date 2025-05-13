
document.addEventListener("DOMContentLoaded", () => {
  const storedTheme = localStorage.getItem("theme");
  const html = document.documentElement;
  const icon = document.querySelector(".theme-toggle i");

  if (storedTheme) {
    html.setAttribute("data-theme", storedTheme);
    if (icon) {
      icon.className = storedTheme === "dark" ? "fa-solid fa-sun" : "fa-solid fa-moon";
    }
  }

  window.toggleTheme = function () {
    const current = html.getAttribute("data-theme");
    const newTheme = current === "light" ? "dark" : "light";
    html.setAttribute("data-theme", newTheme);
    localStorage.setItem("theme", newTheme);
    if (icon) {
      icon.className = newTheme === "dark" ? "fa-solid fa-sun" : "fa-solid fa-moon";
    }
  };
});
