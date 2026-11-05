document.addEventListener('DOMContentLoaded',()=>{for(const link of document.querySelectorAll('nav a')){if(link.pathname===location.pathname)link.setAttribute('aria-current','page');}});
