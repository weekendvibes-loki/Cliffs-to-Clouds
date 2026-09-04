(() => {
  "use strict";

  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const header = document.querySelector("[data-header]");
  const progressBar = document.querySelector(".scroll-progress span");
  const heroShots = [...document.querySelectorAll(".book-shot")];
  const timelines = [...document.querySelectorAll("[data-timeline]")];
  let ticking = false;

  const updateScroll = () => {
    const top = window.scrollY;
    const max = Math.max(document.documentElement.scrollHeight - window.innerHeight, 1);
    if (header) header.classList.toggle("is-scrolled", top > 28);
    if (progressBar) progressBar.style.transform = `scaleX(${Math.min(top / max, 1)})`;

    if (!reducedMotion && top < window.innerHeight * 1.2) {
      heroShots.forEach((shot, index) => {
        const drift = top * (0.012 + index * 0.006);
        shot.style.setProperty("--book-drift", `${drift}px`);
      });
    }

    timelines.forEach((timeline) => {
      const rect = timeline.getBoundingClientRect();
      const start = window.innerHeight * 0.68;
      const end = window.innerHeight * 0.22;
      const travelled = start - rect.top;
      const range = Math.max(rect.height + start - end, 1);
      const value = Math.max(0, Math.min(travelled / range, 1));
      timeline.style.setProperty("--timeline-progress", `${value * 100}%`);
    });
    ticking = false;
  };

  window.addEventListener(
    "scroll",
    () => {
      if (!ticking) {
        window.requestAnimationFrame(updateScroll);
        ticking = true;
      }
    },
    { passive: true }
  );
  updateScroll();

  const reveals = [...document.querySelectorAll("[data-book-reveal]")];
  if ("IntersectionObserver" in window && !reducedMotion) {
    const observer = new IntersectionObserver(
      (entries, revealObserver) => {
        entries.forEach((entry) => {
          if (!entry.isIntersecting) return;
          entry.target.classList.add("is-visible");
          revealObserver.unobserve(entry.target);
        });
      },
      { threshold: 0.1, rootMargin: "0px 0px -7% 0px" }
    );
    reveals.forEach((element, index) => {
      element.style.transitionDelay = `${Math.min((index % 4) * 45, 135)}ms`;
      observer.observe(element);
    });
  } else {
    reveals.forEach((element) => element.classList.add("is-visible"));
  }

  const dayLinks = [...document.querySelectorAll("[data-day-link]")];
  const days = [...document.querySelectorAll("[data-book-day]")];
  const activateDay = (day) => {
    const number = day?.dataset.bookDay;
    dayLinks.forEach((link) => {
      const active = link.dataset.dayLink === number;
      link.classList.toggle("is-active", active);
      if (active) link.setAttribute("aria-current", "location");
      else link.removeAttribute("aria-current");
    });
  };

  if ("IntersectionObserver" in window && days.length) {
    const dayObserver = new IntersectionObserver(
      (entries) => {
        const visible = entries
          .filter((entry) => entry.isIntersecting)
          .sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0];
        if (visible) activateDay(visible.target);
      },
      { threshold: [0.08, 0.2, 0.4], rootMargin: "-24% 0px -58% 0px" }
    );
    days.forEach((day) => dayObserver.observe(day));
  }

  const sectionLinks = [...document.querySelectorAll('.main-nav a[href^="#"]')];
  const sections = sectionLinks.map((link) => document.querySelector(link.getAttribute("href"))).filter(Boolean);
  if ("IntersectionObserver" in window && sections.length) {
    const sectionObserver = new IntersectionObserver(
      (entries) => {
        const visible = entries
          .filter((entry) => entry.isIntersecting)
          .sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0];
        if (!visible) return;
        sectionLinks.forEach((link) => {
          const active = link.getAttribute("href") === `#${visible.target.id}`;
          link.classList.toggle("is-active", active);
        });
      },
      { threshold: [0.05, 0.25], rootMargin: "-20% 0px -58% 0px" }
    );
    sections.forEach((section) => sectionObserver.observe(section));
  }

  const storageKey = "cliffs-to-clouds-detailed-checklist-v1";
  const checkboxes = [...document.querySelectorAll("[data-book-check]")];
  const count = document.querySelector("[data-book-count]");
  const meter = document.querySelector("[data-book-meter]");
  const reset = document.querySelector("[data-book-reset]");

  const readSaved = () => {
    try {
      const value = JSON.parse(window.localStorage.getItem(storageKey) || "[]");
      return Array.isArray(value) ? value : [];
    } catch {
      return [];
    }
  };

  const updateChecks = () => {
    const selected = checkboxes.filter((item) => item.checked).map((item) => item.dataset.bookCheck);
    if (count) count.textContent = String(selected.length);
    if (meter) meter.style.width = `${checkboxes.length ? (selected.length / checkboxes.length) * 100 : 0}%`;
    try {
      window.localStorage.setItem(storageKey, JSON.stringify(selected));
    } catch {
      // Keep the checklist usable for the current visit when storage is blocked.
    }
  };

  const saved = readSaved();
  checkboxes.forEach((checkbox) => {
    checkbox.checked = saved.includes(checkbox.dataset.bookCheck);
    checkbox.addEventListener("change", updateChecks);
  });
  updateChecks();

  if (reset) {
    reset.addEventListener("click", () => {
      checkboxes.forEach((checkbox) => {
        checkbox.checked = false;
      });
      updateChecks();
    });
  }
})();
