// Mobile nav, hero equalizer, scroll reveals, and the booking form.

document.documentElement.classList.add("js");

(() => {
  const toggle = document.querySelector(".nav-toggle");
  const nav = document.getElementById("site-nav");
  if (toggle && nav) {
    toggle.addEventListener("click", () => {
      const open = nav.classList.toggle("open");
      toggle.setAttribute("aria-expanded", String(open));
    });
    nav.addEventListener("click", (ev) => {
      if (ev.target.closest("a")) {
        nav.classList.remove("open");
        toggle.setAttribute("aria-expanded", "false");
      }
    });
  }

  // ------------------------------------------------------- hero equalizer
  const eq = document.querySelector(".eq");
  if (eq) {
    const count = window.innerWidth < 600 ? 32 : 64;
    for (let i = 0; i < count; i++) {
      const bar = document.createElement("span");
      bar.style.setProperty("--d", (0.45 + Math.random() * 0.9).toFixed(2) + "s");
      bar.style.setProperty("--delay", (-Math.random() * 1.5).toFixed(2) + "s");
      bar.style.setProperty("--min", (0.05 + Math.random() * 0.15).toFixed(2));
      bar.style.setProperty("--max", (0.35 + Math.random() * 0.65).toFixed(2));
      eq.appendChild(bar);
    }
  }

  // ------------------------------------------------------- scroll reveals
  const revealEls = document.querySelectorAll(".reveal");
  if ("IntersectionObserver" in window) {
    const io = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("in");
          io.unobserve(entry.target);
        }
      });
    }, { threshold: 0.1, rootMargin: "0px 0px -40px 0px" });
    revealEls.forEach((el) => io.observe(el));
  } else {
    revealEls.forEach((el) => el.classList.add("in"));
  }

  // --------------------------------------------------------- booking form
  const form = document.querySelector(".booking-form");
  if (!form) return;

  const status = form.querySelector(".form-status");
  const button = form.querySelector("button[type=submit]");
  const dateInput = form.querySelector("[name=event_date]");
  if (dateInput) dateInput.min = new Date().toISOString().slice(0, 10);

  // Prefill from links like book/?package=Gold or book/?booth=1
  const params = new URLSearchParams(window.location.search);
  const pkg = params.get("package");
  const pkgSelect = form.querySelector("[name=package]");
  if (pkg && pkgSelect && [...pkgSelect.options].some((o) => o.value === pkg)) pkgSelect.value = pkg;
  if (params.get("booth")) form.querySelector("[name=photo_booth]").checked = true;

  const setStatus = (text, kind) => {
    status.textContent = text;
    status.className = "form-status" + (kind ? " " + kind : "");
  };

  const validate = () => {
    let firstBad = null;
    form.querySelectorAll("[required]").forEach((el) => {
      const bad = !el.checkValidity();
      el.setAttribute("aria-invalid", String(bad));
      if (bad && !firstBad) firstBad = el;
    });
    if (firstBad) firstBad.focus();
    return !firstBad;
  };

  const summary = (data) => {
    const labels = {
      name: "Name", email: "Email", phone: "Phone", event_date: "Event date", event_type: "Event type",
      package: "Package", venue: "Venue / city", guests: "Expected guests", hours: "Time",
      photo_booth: "Interested in a photo booth", message: "Details",
    };
    return Object.entries(labels)
      .filter(([key]) => data.get(key))
      .map(([key, label]) => `${label}: ${data.get(key)}`)
      .join("\n");
  };

  form.addEventListener("submit", async (ev) => {
    ev.preventDefault();
    if (!validate()) {
      setStatus("Fill in the highlighted fields.", "err");
      return;
    }
    const data = new FormData(form);
    if (data.get("company")) return; // honeypot: bots fill hidden fields

    const subject = `DJ Play booking request: ${data.get("event_type")} on ${data.get("event_date")}`;
    const endpoint = form.dataset.endpoint;

    if (!endpoint) {
      const href = `mailto:${form.dataset.email}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(summary(data))}`;
      window.location.href = href;
      setStatus("Your email app should open with the request filled in. Hit send there.", "ok");
      return;
    }

    button.disabled = true;
    setStatus("Sending...");
    data.delete("company");
    data.append("_subject", subject);
    try {
      const res = await fetch(endpoint, { method: "POST", body: data, headers: { Accept: "application/json" } });
      if (!res.ok) {
        // Formspree returns { errors: [{ field, message }] } when it rejects a submission.
        const body = await res.json().catch(() => ({}));
        const errors = Array.isArray(body.errors) ? body.errors : [];
        errors.forEach((err) => {
          const el = err.field && form.querySelector(`[name="${err.field}"]`);
          if (el) el.setAttribute("aria-invalid", "true");
        });
        const msg = errors.map((err) => err.message).filter(Boolean).join(" ");
        throw Object.assign(new Error(msg), { fromFormspree: true });
      }
      form.reset();
      setStatus("Request sent. You'll hear back within 24 hours.", "ok");
    } catch (err) {
      const detail = err && err.fromFormspree && err.message ? `${err.message} ` : "";
      setStatus(`${detail}That didn't go through. Call or email us directly.`, "err");
    } finally {
      button.disabled = false;
    }
  });

  form.addEventListener("input", (ev) => {
    if (ev.target.getAttribute("aria-invalid") === "true" && ev.target.checkValidity()) {
      ev.target.setAttribute("aria-invalid", "false");
    }
  });
})();
