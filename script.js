const hamburger = document.getElementById("hamburger");
const navLinks = document.querySelector(".nav-links");
const ctabutton = document.querySelector(".cta-button");

hamburger.addEventListener("click", () => {
    navLinks.classList.toggle("show");
    ctabutton.classList.toggle("show")
});