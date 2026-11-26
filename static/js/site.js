document.addEventListener("DOMContentLoaded", () => {
  const toggle = document.querySelector(".mobile-toggle");
  const sidebar = document.querySelector(".sidebar");
  const backdrop = document.querySelector(".sidebar-backdrop");
  const mobile = window.matchMedia("(max-width: 800px)");
  const setNavigation = (open) => {
    if (!sidebar || !toggle || !backdrop) return;
    sidebar.classList.toggle("open", open);
    sidebar.inert = mobile.matches && !open;
    backdrop.hidden = !open;
    toggle.setAttribute("aria-expanded", String(open));
    toggle.setAttribute("aria-label", open ? "Close navigation" : "Open navigation");
    if (open) sidebar.querySelector("a")?.focus();
    else toggle.focus();
  };
  if (toggle && sidebar && backdrop) {
    sidebar.inert = mobile.matches;
    mobile.addEventListener("change", () => {
      sidebar.classList.remove("open");
      sidebar.inert = mobile.matches;
      backdrop.hidden = true;
      toggle.setAttribute("aria-expanded", "false");
    });
    toggle.addEventListener("click", () => setNavigation(!sidebar.classList.contains("open")));
    backdrop.addEventListener("click", () => setNavigation(false));
    document.addEventListener("keydown", (event) => {
      if (event.key === "Escape" && sidebar.classList.contains("open")) setNavigation(false);
    });
  }

  const account = document.querySelector(".account-menu");
  if (account) {
    document.addEventListener("click", (event) => {
      if (!account.contains(event.target)) account.open = false;
    });
    document.addEventListener("keydown", (event) => {
      if (event.key === "Escape" && account.open) {
        account.open = false;
        account.querySelector("summary").focus();
      }
    });
  }

  document.querySelectorAll('.field input[type="password"]').forEach((input) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "password-toggle";
    button.textContent = "Show password";
    button.setAttribute("aria-controls", input.id);
    button.setAttribute("aria-pressed", "false");
    input.insertAdjacentElement("afterend", button);
    button.addEventListener("click", () => {
      const show = input.type === "password";
      input.type = show ? "text" : "password";
      button.textContent = show ? "Hide password" : "Show password";
      button.setAttribute("aria-pressed", String(show));
    });
  });

  document.querySelectorAll(".toast-dismiss").forEach((button) => {
    button.addEventListener("click", () => button.closest(".message").remove());
  });

  const sectionLinks = document.querySelectorAll(".profile-sections a");
  if (sectionLinks.length && "IntersectionObserver" in window) {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        sectionLinks.forEach((link) => {
          if (link.hash === `#${entry.target.id}`) link.setAttribute("aria-current", "true");
          else link.removeAttribute("aria-current");
        });
      });
    }, { rootMargin: "-10% 0px -70% 0px" });
    sectionLinks.forEach((link) => {
      const section = document.getElementById(link.hash.slice(1));
      if (section) observer.observe(section);
    });
  }

  const note = document.querySelector("#id_note");
  if (note) {
    const counter = document.createElement("small");
    counter.setAttribute("aria-live", "polite");
    note.insertAdjacentElement("afterend", counter);
    const updateCounter = () => { counter.textContent = `${note.value.length} / 1500 characters`; };
    note.addEventListener("input", updateCounter);
    updateCounter();
  }

  const dialog = document.getElementById("confirm-dialog");
  let pendingForm = null;
  let pendingSubmitter = null;
  if (dialog && typeof dialog.showModal === "function") {
    document.querySelectorAll('form[method="post"]').forEach((form) => {
      const action = new URL(form.action, window.location.href).pathname;
      const destructive = action.endsWith("/delete/");
      const applying = action.endsWith("/apply/");
      const withdrawing = action.endsWith("/withdraw/");
      const moderation = form.hasAttribute("data-confirm");
      if (!destructive && !applying && !withdrawing && !moderation) return;
      form.addEventListener("submit", (event) => {
        if (form.dataset.confirmed === "true") return;
        event.preventDefault();
        pendingForm = form;
        pendingSubmitter = event.submitter;
        dialog.returnValue = "";
        dialog.querySelector("#confirm-title").textContent = applying ? "Submit your application?" : withdrawing ? "Withdraw your application?" : moderation ? "Confirm this change?" : "Remove this item?";
        dialog.querySelector("#confirm-description").textContent = moderation ? form.dataset.confirm : applying
          ? "Your current profile will be available to the opportunity owner."
          : withdrawing ? "You can reapply while the opportunity remains open."
          : "This action cannot be undone.";
        if (applying) {
          const choice = form.querySelector('input[name="resume_choice"]:checked');
          const labels = { none: "No resume", profile: "Profile resume", upload: "Uploaded PDF" };
          const noteText = form.querySelector('[name="note"]')?.value.trim();
          dialog.querySelector("#confirm-description").textContent = `Resume: ${labels[choice?.value] || "No resume"}. ${noteText ? "Your note will be shared with the opportunity owner." : "No note added."}`;
        }
        dialog.querySelector('[value="confirm"]').textContent = applying ? "Submit application" : withdrawing ? "Withdraw" : moderation ? "Confirm" : "Remove";
        dialog.showModal();
      });
    });
    dialog.addEventListener("close", () => {
      if (dialog.returnValue === "confirm" && pendingForm) {
        pendingForm.dataset.confirmed = "true";
        if (pendingSubmitter) pendingForm.requestSubmit(pendingSubmitter);
        else pendingForm.requestSubmit();
      }
      pendingForm = null;
      pendingSubmitter = null;
    });
  }
  document.querySelectorAll(".apply-form").forEach((form) => {
    form.addEventListener("submit", (event) => {
      if (!event.defaultPrevented && event.submitter) {
        event.submitter.disabled = true;
        event.submitter.textContent = "Submitting?";
      }
    });
  });
});
