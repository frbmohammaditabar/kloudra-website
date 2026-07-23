document.addEventListener('DOMContentLoaded', function () {
  var yearEl = document.getElementById('year');
  if (yearEl) yearEl.textContent = new Date().getFullYear();

  var toggle = document.getElementById('navToggle');
  var links = document.getElementById('navLinks');
  if (toggle && links) {
    toggle.addEventListener('click', function () {
      links.classList.toggle('open');
    });
    links.querySelectorAll('a').forEach(function (a) {
      a.addEventListener('click', function () { links.classList.remove('open'); });
    });
  }

  var revealEls = document.querySelectorAll('.reveal');
  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('in');
          io.unobserve(entry.target);
        }
      });
    }, { threshold: 0.12 });
    revealEls.forEach(function (el) { io.observe(el); });
  } else {
    revealEls.forEach(function (el) { el.classList.add('in'); });
  }

  var form = document.getElementById('contactForm');
  if (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var name = document.getElementById('cf-name').value;
      var company = document.getElementById('cf-company').value;
      var email = document.getElementById('cf-email').value;
      var interest = document.getElementById('cf-interest').value;
      var message = document.getElementById('cf-message').value;
      var subject = encodeURIComponent('New enquiry from ' + (name || 'website visitor'));
      var body = encodeURIComponent(
        'Name: ' + name +
        '\nCompany: ' + company +
        '\nEmail: ' + email +
        '\nInterested in: ' + interest +
        '\n\nMessage:\n' + message
      );
      // NOTE: replace hello@kloudra.net with your real business email before publishing
      window.location.href = 'mailto:hello@kloudra.net?subject=' + subject + '&body=' + body;
    });
  }
});
