(function () {
  const menuButton = document.querySelector('.menu-toggle');
  const nav = document.querySelector('.nav-links');
  if (menuButton && nav) {
    menuButton.addEventListener('click', function () {
      const open = menuButton.getAttribute('aria-expanded') === 'true';
      menuButton.setAttribute('aria-expanded', String(!open));
      nav.classList.toggle('open', !open);
    });
  }

  const currentPath = (window.location.pathname.replace(/index\.html$/, '') || '/').replace(/\/{2,}/g, '/');
  document.querySelectorAll('.nav-item[href]').forEach(function (link) {
    const targetPath = new URL(link.href, window.location.href).pathname.replace(/index\.html$/, '');
    const selected = targetPath === '/' ? currentPath === '/' : currentPath.indexOf(targetPath) === 0;
    if (selected) {
      link.classList.add('active');
      link.setAttribute('aria-current', 'page');
    }
  });

  const resourceMenu = document.querySelector('.resource-menu');
  const resourceTrigger = document.querySelector('.resource-trigger');
  const resourceDropdown = document.querySelector('.resource-dropdown');
  function setResourceMenu(open) {
    if (!resourceTrigger || !resourceDropdown) return;
    resourceTrigger.setAttribute('aria-expanded', String(open));
    resourceDropdown.classList.toggle('open', open);
    resourceMenu && resourceMenu.classList.toggle('open', open);
  }
  if (resourceTrigger && resourceDropdown) {
    resourceTrigger.addEventListener('click', function (event) {
      event.stopPropagation();
      setResourceMenu(resourceTrigger.getAttribute('aria-expanded') !== 'true');
    });
    resourceDropdown.querySelectorAll('.resource-city').forEach(function (link) {
      const targetPath = new URL(link.href, window.location.href).pathname.replace(/index\.html$/, '');
      if (currentPath.indexOf(targetPath) === 0) {
        link.classList.add('active');
        link.setAttribute('aria-current', 'page');
        resourceTrigger.classList.add('active');
      }
      link.addEventListener('click', function () { setResourceMenu(false); });
    });
    document.addEventListener('click', function (event) {
      if (resourceMenu && !resourceMenu.contains(event.target)) setResourceMenu(false);
    });
    document.addEventListener('keydown', function (event) {
      if (event.key === 'Escape') {
        setResourceMenu(false);
        resourceTrigger.focus();
      }
    });
  }

  document.querySelectorAll('[data-media-src]').forEach(function (img) {
    const real = img.getAttribute('data-media-src');
    if (!real) return;
    const probe = new Image();
    probe.onload = function () { img.src = real; };
    probe.src = real;
  });

  document.querySelectorAll('[data-gallery]').forEach(function (gallery) {
    const main = gallery.querySelector('.main-photo');
    const caption = gallery.querySelector('figcaption');
    gallery.querySelectorAll('[data-gallery-thumb]').forEach(function (button) {
      button.addEventListener('click', function () {
        const thumb = button.querySelector('img');
        if (!main || !thumb) return;
        main.src = thumb.src;
        main.srcset = thumb.srcset || '';
        main.sizes = thumb.sizes || '';
        main.alt = thumb.alt;
        if (caption) caption.textContent = thumb.alt;
        gallery.querySelectorAll('[data-gallery-thumb]').forEach(function (item) { item.classList.remove('active'); });
        button.classList.add('active');
      });
    });
  });

  document.querySelectorAll('video').forEach(function (video) {
    const note = video.parentElement && video.parentElement.querySelector('.video-note');
    video.addEventListener('loadeddata', function () { if (note) note.hidden = true; });
  });

  document.querySelectorAll('[data-process-tabs]').forEach(function (process) {
    const tabs = Array.from(process.querySelectorAll('[data-process-tab]'));
    const panels = Array.from(process.querySelectorAll('[data-process-panel]'));
    function selectProcess(value, moveFocus) {
      tabs.forEach(function (tab) {
        const selected = tab.getAttribute('data-process-tab') === value;
        tab.classList.toggle('active', selected);
        tab.setAttribute('aria-selected', String(selected));
        tab.setAttribute('tabindex', selected ? '0' : '-1');
        if (selected && moveFocus) tab.focus();
      });
      panels.forEach(function (panel) {
        const selected = panel.getAttribute('data-process-panel') === value;
        panel.classList.toggle('active', selected);
        panel.hidden = !selected;
      });
    }
    tabs.forEach(function (tab, index) {
      tab.addEventListener('click', function () {
        selectProcess(tab.getAttribute('data-process-tab'), false);
      });
      tab.addEventListener('keydown', function (event) {
        if (event.key !== 'ArrowLeft' && event.key !== 'ArrowRight') return;
        event.preventDefault();
        const direction = event.key === 'ArrowRight' ? 1 : -1;
        const next = (index + direction + tabs.length) % tabs.length;
        selectProcess(tabs[next].getAttribute('data-process-tab'), true);
      });
    });
    if (tabs.length) selectProcess(tabs[0].getAttribute('data-process-tab'), false);
  });

  function shuffleProfiles(items) {
    const result = items.slice();
    for (let index = result.length - 1; index > 0; index -= 1) {
      const swapIndex = Math.floor(Math.random() * (index + 1));
      const item = result[index];
      result[index] = result[swapIndex];
      result[swapIndex] = item;
    }
    return result;
  }

  function textElement(tagName, className, text) {
    const element = document.createElement(tagName);
    if (className) element.className = className;
    element.textContent = text;
    return element;
  }

  function createProfileCard(profile) {
    const article = document.createElement('article');
    article.className = 'profile-card';

    const mediaLink = document.createElement('a');
    mediaLink.className = 'card-media';
    mediaLink.href = profile.href;
    const image = document.createElement('img');
    image.src = profile.image;
    if (profile.srcset) {
      image.srcset = profile.srcset;
      image.sizes = '(max-width:760px) 92vw, 800px';
    }
    image.alt = profile.alt;
    image.width = 800;
    image.height = 1000;
    image.loading = 'lazy';
    image.decoding = 'async';
    mediaLink.appendChild(image);

    const body = document.createElement('div');
    body.className = 'card-body';
    const meta = document.createElement('div');
    meta.className = 'card-meta';
    meta.appendChild(textElement('span', '', profile.city + '精选'));
    meta.appendChild(textElement('span', '', profile.tag + '风格'));
    const heading = document.createElement('h3');
    const headingLink = document.createElement('a');
    headingLink.href = profile.href;
    headingLink.textContent = profile.name;
    heading.appendChild(headingLink);
    const summary = textElement('p', '', profile.summary);
    const detailLink = document.createElement('a');
    detailLink.className = 'text-link';
    detailLink.href = profile.href;
    detailLink.textContent = '查看' + profile.name + ' →';
    body.append(meta, heading, summary, detailLink);
    article.append(mediaLink, body);
    return article;
  }

  document.querySelectorAll('[data-random-profiles]').forEach(function (section) {
    const source = section.querySelector('[data-random-source]');
    const grid = section.querySelector('[data-random-grid]');
    if (!source || !grid) return;
    try {
      const items = JSON.parse(source.textContent || '[]');
      const requested = Number.parseInt(section.getAttribute('data-random-count') || '6', 10);
      const selected = shuffleProfiles(items).slice(0, Math.max(1, Math.min(requested, items.length)));
      if (!selected.length) return;
      grid.replaceChildren();
      selected.forEach(function (profile) { grid.appendChild(createProfileCard(profile)); });
    } catch (error) {
      section.setAttribute('data-random-state', 'fallback');
    }
  });

  document.querySelectorAll('[data-home-faq-question]').forEach(function (button) {
    button.addEventListener('click', function () {
      const list = button.closest('.home-faq-list');
      if (!list) return;
      const selectedItem = button.closest('.home-faq-item');
      const willOpen = button.getAttribute('aria-expanded') !== 'true';
      list.querySelectorAll('[data-home-faq-question]').forEach(function (other) {
        const answerId = other.getAttribute('aria-controls');
        const answer = answerId ? document.getElementById(answerId) : null;
        other.setAttribute('aria-expanded', 'false');
        other.closest('.home-faq-item') && other.closest('.home-faq-item').classList.remove('active');
        if (answer) answer.hidden = true;
      });
      if (willOpen) {
        const answer = document.getElementById(button.getAttribute('aria-controls'));
        button.setAttribute('aria-expanded', 'true');
        if (selectedItem) selectedItem.classList.add('active');
        if (answer) answer.hidden = false;
      }
    });
  });


  document.querySelectorAll('[data-chat-open]').forEach(function (button) {
    button.addEventListener('click', function () {
      if (window.HQChatWidget && typeof window.HQChatWidget.toggle === 'function') {
        window.HQChatWidget.toggle();
      } else {
        window.dispatchEvent(new CustomEvent('hq-chat-open'));
      }
    });
  });
})();

/* HQ_SERVER_CHAT_ONLY_RUNTIME_CLEANUP_START */
(() => {
  const cleanupLegacyWebsiteChat = () => {
    document.querySelectorAll('.floating-chat').forEach((node) => {
      node.hidden = true;
      node.style.setProperty('display', 'none', 'important');
      node.style.setProperty('pointer-events', 'none', 'important');
    });

    const host = document.getElementById('hq-chat-widget-host');
    const legacyTheme = host && host.shadowRoot
      ? host.shadowRoot.getElementById('dingshe-chat-widget-theme')
      : null;
    if (legacyTheme) legacyTheme.remove();
  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', cleanupLegacyWebsiteChat, { once: true });
  } else {
    cleanupLegacyWebsiteChat();
  }

  let attempts = 0;
  const timer = window.setInterval(() => {
    cleanupLegacyWebsiteChat();
    attempts += 1;
    if (attempts >= 40) window.clearInterval(timer);
  }, 250);
})();
/* HQ_SERVER_CHAT_ONLY_RUNTIME_CLEANUP_END */
