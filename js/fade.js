document.addEventListener("DOMContentLoaded", function() {
    const links = document.querySelectorAll(".nav-custom a");
  
    links.forEach(link => {
      link.addEventListener("click", function(event) {
        event.preventDefault();
        const href = this.getAttribute("href");
  
        document.getElementById("content-container").classList.remove("fade-in");
        document.getElementById("content-container").classList.add("fade-out");
  
        setTimeout(function() {
          window.location.href = href;
        }, 500);
      });
    });
  });
  