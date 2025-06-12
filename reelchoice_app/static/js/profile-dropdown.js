document.addEventListener("DOMContentLoaded", function () {
  const btn = document.getElementById("profileBtn");
  const menu = document.getElementById("profileMenu");

  if (!btn || !menu) return;

  btn.addEventListener("click", function () {
    menu.classList.toggle("hidden");
  });

  document.addEventListener("click", function (e) {
    if (!btn.contains(e.target) && !menu.contains(e.target)) {
      menu.classList.add("hidden");
    }
  });
});
