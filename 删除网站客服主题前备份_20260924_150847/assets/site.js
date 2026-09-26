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

  let nativeChatLauncher = null;
  let chatScriptPromise = null;
  const chatScriptUrl = 'https://chat.hqvip.xyz/widget.js?site=site1&v=20260923a';

  function ensureChatLoaded() {
    if (window.HQChatWidget) return Promise.resolve();
    if (chatScriptPromise) return chatScriptPromise;
    chatScriptPromise = new Promise(function (resolve, reject) {
      const script = document.createElement('script');
      script.src = chatScriptUrl;
      script.async = true;
      script.dataset.color = '#a43f63';
      script.onload = resolve;
      script.onerror = reject;
      document.head.appendChild(script);
    });
    return chatScriptPromise;
  }
  const nativeLauncherSelectors = [
    '[data-hq-chat-launcher]',
    '.hq-chat-launcher',
    '#hq-chat-launcher',
    '[class*="chat-launcher"]',
    '[id*="chat-launcher"]',
    '[class*="chat-widget-button"]',
    '[id*="chat-widget-button"]',
    'button[aria-label*="在线客服"]',
    'button[aria-label*="打开客服"]',
    'button[title*="在线客服"]'
  ];

  function isOurChatControl(element) {
    return !element || element.closest('[data-chat-open]') || element.closest('.floating-chat');
  }

  function isCornerControl(element) {
    if (!(element instanceof HTMLElement)) return false;
    let current = element;
    for (let depth = 0; current && depth < 4; depth += 1, current = current.parentElement) {
      const style = window.getComputedStyle(current);
      const rect = current.getBoundingClientRect();
      const nearCorner = rect.width > 0 && rect.height > 0 && rect.width <= 150 && rect.height <= 150 && rect.right >= window.innerWidth - 170 && rect.bottom >= window.innerHeight - 170;
      if ((style.position === 'fixed' || style.position === 'sticky') && nearCorner) return true;
    }
    return false;
  }

  function isNativeLauncher(element) {
    if (!(element instanceof HTMLElement) || isOurChatControl(element)) return false;
    const identity = [
      element.id,
      typeof element.className === 'string' ? element.className : '',
      element.getAttribute('aria-label') || '',
      element.getAttribute('title') || '',
      element.getAttribute('data-testid') || '',
      element.textContent || ''
    ].join(' ').toLowerCase();
    if (/关闭|close|minimi[sz]e|收起/.test(identity)) return false;
    if (/chat[-_ ]?launcher|chat[-_ ]?widget[-_ ]?button|hq[-_ ]?chat[-_ ]?launcher/.test(identity)) return true;
    return /(在线客服|打开客服|开始咨询|customer service|open chat|kefu)/.test(identity) && isCornerControl(element);
  }

  function hideNativeLauncher(element) {
    if (!isNativeLauncher(element)) return;
    nativeChatLauncher = element;
    element.classList.add('hq-native-launcher-hidden');
    element.style.setProperty('display', 'none', 'important');
    element.style.setProperty('visibility', 'hidden', 'important');
    element.style.setProperty('pointer-events', 'none', 'important');
    element.setAttribute('aria-hidden', 'true');
    element.setAttribute('tabindex', '-1');
  }

  function applyDingsheChatTheme(root) {
    if (!root || typeof root.querySelector !== 'function' || !root.querySelector('.hq-panel')) return;
    if (root.querySelector('#dingshe-chat-widget-theme')) return;
    const theme = document.createElement('style');
    theme.id = 'dingshe-chat-widget-theme';
    theme.textContent = `
      .hq-panel{
        background:#0d070b!important;
        border:1px solid rgba(239,190,137,.52)!important;
        border-radius:10px!important;
        box-shadow:0 28px 85px rgba(0,0,0,.68),0 0 0 1px rgba(164,63,99,.12),0 0 38px rgba(164,63,99,.16)!important;
      }
      .hq-panel::before{
        content:"";
        position:absolute;
        z-index:2;
        left:0;
        right:0;
        top:0;
        height:3px;
        background:linear-gradient(90deg,#7d2948,#d19b67,#7d2948);
        pointer-events:none;
      }
      .hq-frame{background:#0d070b!important}
      @media(max-width:600px){.hq-panel{border-radius:9px!important}}
    `;
    root.appendChild(theme);
  }

  function scanForNativeLauncher(root) {
    if (!root) return;
    if (root instanceof HTMLElement) {
      hideNativeLauncher(root);
      if (root.shadowRoot) scanForNativeLauncher(root.shadowRoot);
    }
    if (typeof root.querySelectorAll !== 'function') return;
    applyDingsheChatTheme(root);
    root.querySelectorAll(nativeLauncherSelectors.join(',')).forEach(hideNativeLauncher);
    root.querySelectorAll('button, [role="button"]').forEach(function (element) {
      hideNativeLauncher(element);
      if (element.shadowRoot) scanForNativeLauncher(element.shadowRoot);
    });
    root.querySelectorAll('*').forEach(function (element) {
      if (element.shadowRoot) scanForNativeLauncher(element.shadowRoot);
    });
  }

  scanForNativeLauncher(document);
  const chatObserver = new MutationObserver(function (mutations) {
    mutations.forEach(function (mutation) {
      mutation.addedNodes.forEach(function (node) {
        if (node.nodeType === 1 || node.nodeType === 11) scanForNativeLauncher(node);
      });
    });
  });
  chatObserver.observe(document.documentElement, { childList: true, subtree: true });

  function dispatchChatOpen() {
    window.dispatchEvent(new CustomEvent('hq-chat-open'));
    window.postMessage({ type: 'hq-chat-open' }, '*');
    document.querySelectorAll('iframe').forEach(function (frame) {
      if (frame.contentWindow) frame.contentWindow.postMessage({ type: 'hq-chat-open' }, '*');
    });
  }

  function openChat() {
    let attempts = 0;
    function attempt() {
      scanForNativeLauncher(document);
      if (window.HQChatWidget && typeof window.HQChatWidget.toggle === 'function') {
        window.HQChatWidget.toggle();
        return;
      }
      if (nativeChatLauncher && nativeChatLauncher.isConnected) {
        nativeChatLauncher.click();
        return;
      }
      attempts += 1;
      if (attempts < 8) {
        window.setTimeout(attempt, 180);
      } else {
        dispatchChatOpen();
      }
    }
    attempt();
  }

  document.querySelectorAll('[data-chat-open]').forEach(function (button) {
    button.addEventListener('click', function () {
      ensureChatLoaded().then(openChat).catch(function () {
        button.setAttribute('aria-label', '在线客服暂时无法加载');
      });
    });
  });

  window.addEventListener('load', function () {
    window.setTimeout(function () { ensureChatLoaded().catch(function () {}); }, 6000);
  }, { once: true });
})();
