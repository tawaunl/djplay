document.documentElement.classList.add("js");

// Mobile menu
const toggle = document.querySelector(".nav-toggle");
const links = document.getElementById("nav-links");

toggle.addEventListener("click", () => {
  const open = toggle.getAttribute("aria-expanded") === "true";
  toggle.setAttribute("aria-expanded", String(!open));
  toggle.setAttribute("aria-label", open ? "Open menu" : "Close menu");
  links.classList.toggle("open", !open);
});

links.addEventListener("click", (e) => {
  if (e.target.closest("a") && links.classList.contains("open")) toggle.click();
});

// Equalizer bars in the hero
const eq = document.querySelector(".eq");
if (eq) {
  const count = window.innerWidth < 600 ? 32 : 64;
  for (let i = 0; i < count; i++) {
    const bar = document.createElement("span");
    bar.style.setProperty("--d", (0.45 + Math.random() * 0.9).toFixed(2) + "s");
    bar.style.setProperty("--delay", (-Math.random() * 1.5).toFixed(2) + "s");
    bar.style.setProperty("--min", (0.05 + Math.random() * 0.15).toFixed(2));
    bar.style.setProperty("--max", (0.35 + Math.random() * 0.65).toFixed(2));
    eq.appendChild(bar);
  }
}

// Reveal sections as they scroll into view
const revealEls = document.querySelectorAll(".reveal");
if ("IntersectionObserver" in window) {
  const io = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add("in");
        io.unobserve(entry.target);
      }
    });
  }, { threshold: 0.12, rootMargin: "0px 0px -40px 0px" });
  revealEls.forEach((el) => io.observe(el));
} else {
  revealEls.forEach((el) => el.classList.add("in"));
}

document.getElementById("year").textContent = new Date().getFullYear();
