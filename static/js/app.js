/* Interações progressivas: a aplicação funciona sem JavaScript;
   os scripts apenas melhoram a experiência (menu, galeria, cópia, compartilhamento). */
(function () {
  "use strict";

  // Menu móvel acessível
  const toggle = document.querySelector("[data-menu-toggle]");
  const nav = document.getElementById("menu-principal");
  if (toggle && nav) {
    const fechar = () => {
      toggle.setAttribute("aria-expanded", "false");
      nav.classList.remove("is-aberto");
    };
    toggle.addEventListener("click", () => {
      const aberto = toggle.getAttribute("aria-expanded") === "true";
      toggle.setAttribute("aria-expanded", String(!aberto));
      nav.classList.toggle("is-aberto", !aberto);
    });
    document.addEventListener("keydown", (e) => { if (e.key === "Escape") fechar(); });
  }

  // Fechar mensagens
  document.querySelectorAll("[data-fechar]").forEach((btn) =>
    btn.addEventListener("click", () => btn.closest("[data-mensagem]").remove())
  );

  // Galeria de fotos
  const principal = document.querySelector("[data-galeria-principal]");
  document.querySelectorAll("[data-galeria-mini]").forEach((mini) => {
    mini.addEventListener("click", () => {
      if (!principal) return;
      principal.style.opacity = "0";
      setTimeout(() => {
        principal.src = mini.dataset.galeriaMini;
        principal.style.opacity = "1";
      }, 150);
      document.querySelectorAll("[data-galeria-mini]").forEach((m) => m.classList.remove("is-ativa"));
      mini.classList.add("is-ativa");
    });
  });

  // Copiar chave PIX
  document.querySelectorAll("[data-copiar]").forEach((btn) => {
    btn.addEventListener("click", async () => {
      const alvo = document.querySelector(btn.dataset.copiar);
      const feedback = document.querySelector("[data-copiar-feedback]");
      try {
        await navigator.clipboard.writeText(alvo.textContent.trim());
        if (feedback) feedback.textContent = "Chave copiada! Obrigado pelo apoio 💛";
      } catch {
        if (feedback) feedback.textContent = "Selecione e copie a chave manualmente.";
      }
    });
  });

  // Compartilhar perfil (Web Share API com alternativa de copiar link)
  document.querySelectorAll("[data-compartilhar]").forEach((btn) => {
    btn.addEventListener("click", async () => {
      const dados = { title: btn.dataset.titulo, url: btn.dataset.url };
      const feedback = document.querySelector("[data-compartilhar-feedback]");
      if (navigator.share) {
        try { await navigator.share(dados); } catch { /* cancelado */ }
        return;
      }
      try {
        await navigator.clipboard.writeText(dados.url);
        if (feedback) feedback.textContent = "Link copiado! Cole no WhatsApp ou Instagram.";
      } catch {
        if (feedback) feedback.textContent = dados.url;
      }
    });
  });

  // Pré-visualização da foto principal no formulário
  document.querySelectorAll("[data-preview-de]").forEach((img) => {
    const input = document.getElementById(img.dataset.previewDe);
    if (!input) return;
    input.addEventListener("change", () => {
      const arquivo = input.files && input.files[0];
      if (!arquivo) return;
      img.src = URL.createObjectURL(arquivo);
      img.hidden = false;
    });
  });

  // Animação de entrada dos cards
  const reduzir = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (!reduzir && "IntersectionObserver" in window) {
    const itens = document.querySelectorAll(".card-cao, .passo, .adotado, .indicador");
    const obs = new IntersectionObserver((entradas) => {
      entradas.forEach((ent) => {
        if (ent.isIntersecting) {
          ent.target.classList.add("is-visivel");
          obs.unobserve(ent.target);
        }
      });
    }, { threshold: 0.12 });
    itens.forEach((el, i) => {
      el.classList.add("revelar");
      el.style.transitionDelay = `${(i % 6) * 60}ms`;
      obs.observe(el);
    });
  }
})();
