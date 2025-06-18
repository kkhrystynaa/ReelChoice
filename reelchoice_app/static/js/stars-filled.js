document.addEventListener("DOMContentLoaded", () => {
  const starsContainer = document.getElementById("stars");
  const stars = starsContainer.querySelectorAll("svg");
  const scoreInput = document.getElementById("score-input");

  function setStars(rating) {
    stars.forEach((star) => {
      const starValue = parseInt(star.getAttribute("data-value"));
      if (starValue <= rating) {
        star.classList.add("text-[#BA4040]");
        star.classList.remove("text-[#424242]");
      } else {
        star.classList.add("text-[#424242]");
        star.classList.remove("text-[#BA4040]");
      }
    });
  }

  // Фіксуємо зірки, якщо є збережений рейтинг
  if (scoreInput.value) {
    setStars(parseInt(scoreInput.value));
  }

  stars.forEach((star) => {
    star.addEventListener("mouseenter", () => {
      const hoverValue = parseInt(star.getAttribute("data-value"));
      setStars(hoverValue);
    });

    star.addEventListener("mouseleave", () => {
      if (scoreInput.value) {
        setStars(parseInt(scoreInput.value));
      } else {
        setStars(0);
      }
    });

    star.addEventListener("click", () => {
      const selectedValue = parseInt(star.getAttribute("data-value"));
      scoreInput.value = selectedValue;
      setStars(selectedValue);

      star.classList.add("shadow-lg", "scale-95", "transition-all");

      setTimeout(() => {
        star.classList.remove("shadow-lg", "scale-95");
      }, 150);
    });
  });
});

