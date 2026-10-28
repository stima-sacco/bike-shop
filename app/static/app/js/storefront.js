document.addEventListener("DOMContentLoaded", () => {
  const menuToggle = document.querySelector(".menu-toggle");
  const navigation = document.querySelector("#site-nav");
  const filters = document.querySelectorAll(".filter-button");
  const products = document.querySelectorAll("#bikes .product-card");
  const emptyState = document.querySelector(".empty-state");
  const cartCount = document.querySelector(".cart-count");
  const cartLink = document.querySelector(".cart-link");
  const toast = document.querySelector(".toast");
  const newsletterForm = document.querySelector(".newsletter-form");
  let itemCount = 0;
  let toastTimeout;

  menuToggle.addEventListener("click", () => {
    const isOpen = menuToggle.getAttribute("aria-expanded") === "true";
    menuToggle.setAttribute("aria-expanded", String(!isOpen));
    menuToggle.setAttribute("aria-label", isOpen ? "Open navigation" : "Close navigation");
    navigation.classList.toggle("is-open", !isOpen);
  });

  navigation.querySelectorAll("a").forEach((link) => {
    link.addEventListener("click", () => {
      menuToggle.setAttribute("aria-expanded", "false");
      menuToggle.setAttribute("aria-label", "Open navigation");
      navigation.classList.remove("is-open");
    });
  });

  filters.forEach((filter) => {
    filter.addEventListener("click", () => {
      const category = filter.dataset.filter;
      let visibleCount = 0;

      filters.forEach((button) => {
        const isActive = button === filter;
        button.classList.toggle("is-active", isActive);
        button.setAttribute("aria-pressed", String(isActive));
      });

      products.forEach((product) => {
        const isVisible = category === "all" || product.dataset.category === category;
        product.hidden = !isVisible;
        visibleCount += Number(isVisible);
      });

      emptyState.hidden = visibleCount !== 0;
    });
  });

  document.querySelectorAll(".add-button").forEach((button) => {
    button.addEventListener("click", () => {
      itemCount += 1;
      cartCount.textContent = String(itemCount);
      cartLink.setAttribute("aria-label", `Shopping bag, ${itemCount} ${itemCount === 1 ? "item" : "items"}`);
      button.classList.add("is-added");
      showToast(`${button.dataset.product} added to your bag`);
    });
  });

  if (newsletterForm) {
    newsletterForm.addEventListener("submit", (event) => {
      event.preventDefault();
      document.querySelector(".form-message").textContent = "Thanks for stopping by — newsletter sign-up is coming soon.";
      newsletterForm.reset();
    });
  }

  function showToast(message) {
    toast.textContent = message;
    toast.classList.add("is-visible");
    window.clearTimeout(toastTimeout);
    toastTimeout = window.setTimeout(() => toast.classList.remove("is-visible"), 2600);
  }
});
