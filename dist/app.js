(() => {
  "use strict";

  const root = document.documentElement;
  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const header = document.querySelector("[data-header]");
  const progressBar = document.querySelector(".scroll-progress span");
  const heroImage = document.querySelector("[data-parallax]");
  let ticking = false;

  const updateScrollUI = () => {
    const scrollTop = window.scrollY;
    const scrollable = Math.max(document.documentElement.scrollHeight - window.innerHeight, 1);
    const progress = Math.min(scrollTop / scrollable, 1);

    if (header) header.classList.toggle("is-scrolled", scrollTop > 28);
    if (progressBar) progressBar.style.transform = `scaleX(${progress})`;

    if (heroImage && !reducedMotion && scrollTop < window.innerHeight * 1.25) {
      heroImage.style.transform = `translate3d(0, ${scrollTop * 0.045}px, 0) scale(1.03)`;
    }

    ticking = false;
  };

  window.addEventListener(
    "scroll",
    () => {
      if (!ticking) {
        window.requestAnimationFrame(updateScrollUI);
        ticking = true;
      }
    },
    { passive: true }
  );
  updateScrollUI();

  const revealElements = [...document.querySelectorAll("[data-reveal]")];
  if ("IntersectionObserver" in window && !reducedMotion) {
    const revealObserver = new IntersectionObserver(
      (entries, observer) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add("is-visible");
            observer.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.12, rootMargin: "0px 0px -8% 0px" }
    );
    revealElements.forEach((element) => revealObserver.observe(element));
  } else {
    revealElements.forEach((element) => element.classList.add("is-visible"));
  }

  const navLinks = [...document.querySelectorAll(".main-nav a")];
  const navSections = navLinks
    .map((link) => {
      const href = link.getAttribute("href");
      return href && href.startsWith("#") ? document.querySelector(href) : null;
    })
    .filter(Boolean);

  if ("IntersectionObserver" in window && navSections.length) {
    const navObserver = new IntersectionObserver(
      (entries) => {
        const visible = entries
          .filter((entry) => entry.isIntersecting)
          .sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0];
        if (!visible) return;

        navLinks.forEach((link) => {
          const active = link.getAttribute("href") === `#${visible.target.id}`;
          link.classList.toggle("is-active", active);
          if (active) link.setAttribute("aria-current", "location");
          else link.removeAttribute("aria-current");
        });
      },
      { threshold: [0.1, 0.35, 0.6], rootMargin: "-22% 0px -55% 0px" }
    );
    navSections.forEach((section) => navObserver.observe(section));
  }

  const dayCards = [...document.querySelectorAll(".day-card")];
  const sceneImages = [...document.querySelectorAll("[data-scene]")];
  const visualDay = document.querySelector("[data-visual-day]");
  const visualPlace = document.querySelector("[data-visual-place]");
  const visualCoordinate = document.querySelector("[data-visual-coordinate]");

  const setScene = (card) => {
    if (!card) return;
    const scene = card.dataset.sceneTarget;
    const index = dayCards.indexOf(card);

    dayCards.forEach((item) => item.classList.toggle("is-current", item === card));
    sceneImages.forEach((image) => image.classList.toggle("is-active", image.dataset.scene === scene));

    if (visualDay) visualDay.textContent = `Day ${String(index + 1).padStart(2, "0")}`;
    if (visualPlace) visualPlace.textContent = card.dataset.place || "";
    if (visualCoordinate) visualCoordinate.textContent = card.dataset.coordinate || "";
  };

  if ("IntersectionObserver" in window && dayCards.length) {
    const dayObserver = new IntersectionObserver(
      (entries) => {
        const candidate = entries
          .filter((entry) => entry.isIntersecting)
          .sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0];
        if (candidate) setScene(candidate.target);
      },
      { threshold: [0.2, 0.45, 0.7], rootMargin: "-25% 0px -35% 0px" }
    );
    dayCards.forEach((card) => dayObserver.observe(card));
  }

  const currency = new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 0,
  });
  const vehicleInputs = [...document.querySelectorAll('input[name="vehicle"]')];
  const totalElement = document.querySelector("[data-total]");
  const perPersonElement = document.querySelector("[data-per-person]");
  const vehicleCostElement = document.querySelector("[data-vehicle-cost]");
  const meter = document.querySelector("[data-meter]");
  const status = document.querySelector("[data-status]");
  const ring = document.querySelector("[data-ring]");
  const ringValue = document.querySelector("[data-ring-value]");
  const baseCost = 35000;
  const cap = 45000;
  const people = 7;

  const updateBudget = (vehicleCost) => {
    const total = baseCost + vehicleCost;
    const totalPercent = Math.min((total / cap) * 100, 100);
    const capRangePercent = Math.max(0, Math.min(((total - baseCost) / (cap - baseCost)) * 100, 100));
    const remaining = cap - total;

    if (totalElement) {
      totalElement.textContent = currency.format(total);
      totalElement.classList.remove("is-changing");
      void totalElement.offsetWidth;
      totalElement.classList.add("is-changing");
    }
    if (perPersonElement) perPersonElement.textContent = currency.format(Math.round(total / people));
    if (vehicleCostElement) vehicleCostElement.textContent = currency.format(vehicleCost);
    if (meter) meter.style.width = `${capRangePercent}%`;
    if (ring) ring.style.setProperty("--budget-angle", `${totalPercent * 3.6}deg`);
    if (ringValue) ringValue.textContent = `${Math.round(totalPercent)}%`;

    if (status) {
      if (remaining === 0) status.textContent = "Right on the ₹45k ceiling";
      else if (remaining > 0) status.textContent = `${currency.format(remaining)} breathing room`;
      else status.textContent = `${currency.format(Math.abs(remaining))} over budget`;
    }
  };

  vehicleInputs.forEach((input) => {
    input.addEventListener("change", () => {
      if (input.checked) updateBudget(Number(input.value));
    });
  });
  const selectedVehicle = vehicleInputs.find((input) => input.checked);
  updateBudget(selectedVehicle ? Number(selectedVehicle.value) : 10000);

  const checklistKey = "cliffs-to-clouds-checklist-v1";
  const checklistInputs = [...document.querySelectorAll("[data-check]")];
  const checkCount = document.querySelector("[data-check-count]");
  const checkProgress = document.querySelector("[data-check-progress]");
  const resetButton = document.querySelector("[data-reset]");

  const readChecklist = () => {
    try {
      const stored = JSON.parse(window.localStorage.getItem(checklistKey) || "[]");
      return Array.isArray(stored) ? stored : [];
    } catch {
      return [];
    }
  };

  const updateChecklist = () => {
    const completed = checklistInputs.filter((input) => input.checked).map((input) => input.dataset.check);
    if (checkCount) checkCount.textContent = String(completed.length);
    if (checkProgress) {
      const percentage = checklistInputs.length ? (completed.length / checklistInputs.length) * 100 : 0;
      checkProgress.style.width = `${percentage}%`;
    }
    try {
      window.localStorage.setItem(checklistKey, JSON.stringify(completed));
    } catch {
      // The checklist still works for this page visit when storage is unavailable.
    }
  };

  const savedChecks = readChecklist();
  checklistInputs.forEach((input) => {
    input.checked = savedChecks.includes(input.dataset.check);
    input.addEventListener("change", updateChecklist);
  });
  updateChecklist();

  if (resetButton) {
    resetButton.addEventListener("click", () => {
      checklistInputs.forEach((input) => {
        input.checked = false;
      });
      updateChecklist();
    });
  }

  const toast = document.querySelector("[data-toast]");
  let toastTimer;
  const showToast = (message) => {
    if (!toast) return;
    toast.textContent = message;
    toast.classList.add("is-visible");
    window.clearTimeout(toastTimer);
    toastTimer = window.setTimeout(() => toast.classList.remove("is-visible"), 2400);
  };

  const copyLink = async () => {
    try {
      await navigator.clipboard.writeText(window.location.href);
      showToast("Trip link copied");
    } catch {
      const textArea = document.createElement("textarea");
      textArea.value = window.location.href;
      textArea.setAttribute("readonly", "");
      textArea.style.position = "fixed";
      textArea.style.opacity = "0";
      document.body.appendChild(textArea);
      textArea.select();
      document.execCommand("copy");
      textArea.remove();
      showToast("Trip link copied");
    }
  };

  document.querySelectorAll("[data-share]").forEach((button) => {
    button.addEventListener("click", async () => {
      const shareData = {
        title: "Cliffs to Clouds — Kerala Road Trip",
        text: "Our Tirupati → Varkala → Ponmudi → Munroe Island road-trip plan for 5–9 September.",
        url: window.location.href,
      };

      if (navigator.share) {
        try {
          await navigator.share(shareData);
        } catch (error) {
          if (error && error.name !== "AbortError") await copyLink();
        }
      } else {
        await copyLink();
      }
    });
  });

  document.querySelectorAll("[data-print]").forEach((button) => {
    button.addEventListener("click", () => window.print());
  });
})();
