/* Єдина шапка: тінь при прокрутці + мобільне меню (така сама логіка, як на головній) */
(function () {
  var header = document.getElementById('site-header');
  var burger = document.getElementById('burger');
  var mobileMenu = document.getElementById('mobile-menu');
  if (!header) return;
  window.addEventListener('scroll', function () {
    header.classList.toggle('scrolled', window.scrollY > 10);
  }, { passive: true });
  if (!burger || !mobileMenu) return;
  burger.addEventListener('click', function () {
    var isOpen = mobileMenu.classList.toggle('open');
    burger.setAttribute('aria-expanded', isOpen);
  });
  mobileMenu.querySelectorAll('a').forEach(function (link) {
    link.addEventListener('click', function () {
      mobileMenu.classList.remove('open');
      burger.setAttribute('aria-expanded', 'false');
    });
  });
})();
