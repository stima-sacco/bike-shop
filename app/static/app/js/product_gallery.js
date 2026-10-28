document.addEventListener("DOMContentLoaded", () => {
  const gallery = document.querySelector("[data-gallery]");
  if (!gallery) {
    return;
  }

  const mainImage = gallery.querySelector("[data-gallery-main]");
  const thumbs = Array.from(gallery.querySelectorAll("[data-gallery-thumb]"));
  const lightbox = gallery.querySelector("[data-gallery-lightbox]");
  const lightboxImage = gallery.querySelector("[data-gallery-lightbox-image]");
  const images = thumbs.length
    ? thumbs.map((thumb) => ({ src: thumb.dataset.src, alt: thumb.dataset.alt }))
    : [{ src: mainImage.getAttribute("src"), alt: mainImage.alt }];
  let current = 0;

  function show(index) {
    current = (index + images.length) % images.length;
    const image = images[current];
    mainImage.src = image.src;
    mainImage.alt = image.alt;
    lightboxImage.src = image.src;
    lightboxImage.alt = image.alt;
    thumbs.forEach((thumb, i) => thumb.classList.toggle("is-active", i === current));
    gallery.querySelectorAll("[data-gallery-counter]").forEach((counter) => {
      counter.textContent = `${current + 1} / ${images.length}`;
    });
  }

  thumbs.forEach((thumb, index) => thumb.addEventListener("click", () => show(index)));
  gallery.querySelectorAll("[data-gallery-prev]").forEach((button) => {
    button.addEventListener("click", () => show(current - 1));
  });
  gallery.querySelectorAll("[data-gallery-next]").forEach((button) => {
    button.addEventListener("click", () => show(current + 1));
  });

  gallery.querySelector("[data-gallery-open]").addEventListener("click", () => {
    if (!images[0].src) {
      return;
    }
    show(current);
    lightbox.showModal();
  });

  gallery.querySelector("[data-gallery-close]").addEventListener("click", () => lightbox.close());

  // Clicking the dark backdrop (the dialog itself, not its contents) closes it.
  lightbox.addEventListener("click", (event) => {
    if (event.target === lightbox) {
      lightbox.close();
    }
  });

  document.addEventListener("keydown", (event) => {
    if (images.length < 2) {
      return;
    }
    if (event.key === "ArrowLeft") {
      show(current - 1);
    } else if (event.key === "ArrowRight") {
      show(current + 1);
    }
  });

  // Swipe between images on touch screens.
  let touchStartX = null;
  [mainImage, lightboxImage].forEach((element) => {
    element.addEventListener("touchstart", (event) => {
      touchStartX = event.touches[0].clientX;
    }, { passive: true });
    element.addEventListener("touchend", (event) => {
      if (touchStartX === null || images.length < 2) {
        return;
      }
      const distance = event.changedTouches[0].clientX - touchStartX;
      if (Math.abs(distance) > 40) {
        show(current + (distance < 0 ? 1 : -1));
      }
      touchStartX = null;
    });
  });
});
