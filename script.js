function toggle(header) {
  const card = header.closest(".endpoint");
  card.classList.toggle("open");
}

function switchTab(tab, panelId) {
  const tabs = tab.parentElement.querySelectorAll(".code-tab");
  tabs.forEach((t) => t.classList.remove("active"));
  tab.classList.add("active");

  // Find all sibling panels
  const container = tab.closest(".endpoint-inner");
  const panels = container.querySelectorAll(".code-panel");
  panels.forEach((p) => p.classList.remove("active"));

  const target = document.getElementById(panelId);
  if (target) target.classList.add("active");
}

function copyPre(btn) {
  const pre = btn.parentElement;
  const text = pre.innerText.replace("copy\n", "").trim();
  navigator.clipboard.writeText(text).then(() => {
    btn.textContent = "copied!";
    btn.style.color = "var(--accent)";
    setTimeout(() => {
      btn.textContent = "copy";
      btn.style.color = "";
    }, 1500);
  });
}

function scrollTo(id) {
  const el = document.getElementById(id);
  if (el) el.scrollIntoView({ behavior: "smooth", block: "start" });
  // Close sidebar on mobile
  if (window.innerWidth < 768) {
    document.getElementById("sidebar").classList.remove("open");
  }
  // Update active
  document
    .querySelectorAll(".sidebar-link")
    .forEach((l) => l.classList.remove("active"));
  event.currentTarget.classList.add("active");
}

function toggleSidebar() {
  document.getElementById("sidebar").classList.toggle("open");
}

// Highlight active sidebar link on scroll
const sections = document.querySelectorAll("[id]");
const links = document.querySelectorAll(".sidebar-link");
window.addEventListener("scroll", () => {
  let current = "";
  sections.forEach((s) => {
    if (window.scrollY >= s.offsetTop - 120) current = s.id;
  });
  links.forEach((l) => {
    l.classList.remove("active");
    if (
      l.getAttribute("onclick") &&
      l.getAttribute("onclick").includes("'" + current + "'")
    ) {
      l.classList.add("active");
    }
  });
});

function scrollSection(id) {
  const element = document.getElementById(id);

  if (element) {
    element.scrollIntoView({
      behavior: "smooth",
      block: "start",
    });
  }
}
