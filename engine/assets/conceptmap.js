/* The concept map's interactions. Only concepts.html loads this file.
 *
 * The page works without it: core/conceptmap.py draws the map as a static SVG whose leaves and
 * nodes are links, and writes the full text index under it. This script adds selection, the
 * panel, the filters, the finder, and zoom and pan. It reads one JSON block on the page
 * (#cx-data) and the map's own elements. It draws nothing new: it only switches classes and
 * the map's viewBox, so nothing here needs a library or the network. */
(function () {
  'use strict';

  var svg = document.querySelector('[data-cx-svg]');
  var dataEl = document.getElementById('cx-data');
  if (!svg || !dataEl) { return; }

  var MAX_ZOOM = 8;

  var raw;
  try { raw = JSON.parse(dataEl.textContent); } catch (e) { return; }
  var topics = raw.topics;
  /* The words come from the guide's settings: the rank labels from window.GUIDE, the tier names
     from the page's own data. */
  var RANKS = (window.GUIDE && window.GUIDE.ranks) || {};
  var TIERS = raw.tiers || {};

  function all(sel, root) { return Array.prototype.slice.call((root || document).querySelectorAll(sel)); }
  function el(tag, cls, text) {
    var n = document.createElement(tag);
    if (cls) { n.className = cls; }
    if (text != null) { n.textContent = text; }
    return n;
  }
  function link(href, text, cls) {
    var a = el('a', cls, text);
    a.setAttribute('href', href);
    return a;
  }
  function chip(rank) {
    var s = el('span', 'rank rank-' + rank, RANKS[rank] || 'No rank');
    return s;
  }
  function glyph(rank) {
    var s = el('span', 'rank-glyph rank-' + rank);
    s.setAttribute('aria-hidden', 'true');
    return s;
  }

  /* ---------- the data, joined to the page ---------- */
  var concepts = {};
  var order = [];
  raw.concepts.forEach(function (row) {
    var c = {
      id: row[0], name: row[1], home: row[2], anchor: row[3], rank: row[4], def: row[5], aliases: row[6],
      refs: row[7].map(function (r) { return { topic: r[0], anchor: r[1], how: r[2] }; }),
      curves: [], leaf: null, entry: null
    };
    c.find = [c.name].concat(c.aliases, [c.def]).join(' ').toLowerCase();
    concepts[c.id] = c;
    order.push(c);
  });
  var usesOf = {};   // topic id -> [{c, ref}]
  var ownOf = {};    // topic id -> [concept]
  order.forEach(function (c) {
    (ownOf[c.home] = ownOf[c.home] || []).push(c);
    c.refs.forEach(function (r) { (usesOf[r.topic] = usesOf[r.topic] || []).push({ c: c, ref: r }); });
  });
  var leafEls = {};
  all('.cx-leaf', svg).forEach(function (a) {
    var c = concepts[a.getAttribute('data-c')];
    if (c) { c.leaf = a; leafEls[c.id] = a; }
  });
  var topicEls = {};
  all('.cx-topic', svg).forEach(function (a) {
    var id = a.getAttribute('data-t');
    topicEls[id] = a;
    a.setAttribute('data-href0', a.getAttribute('href'));
  });
  var tierEls = all('.cx-tier', svg);
  var curveEls = all('.cx-ref', svg);
  curveEls.forEach(function (p) {
    var c = concepts[p.getAttribute('data-from')];
    if (c) { c.curves.push(p); }
    p.cxTo = p.getAttribute('data-to');
  });
  all('.cx-concept').forEach(function (li) {
    var c = concepts[li.getAttribute('data-c')];
    if (c) { c.entry = li; }
  });
  var fanEls = {};
  all('.cx-fan', svg).forEach(function (p) { fanEls[p.getAttribute('data-c')] = p; });
  var topicSecs = all('.cx-topic-sec');
  var tierSecs = all('.cx-tier-sec');

  /* ---------- show the parts that need the script ---------- */
  var controls = document.querySelector('[data-cx-controls]');
  var panel = document.querySelector('[data-cx-panel]');
  var indexPanel = document.querySelector('[data-cx-index-panel]');
  var floatR = document.querySelector('.cx-float-r');
  var zoomBox = document.querySelector('[data-cx-zoom]');
  var hint = document.querySelector('[data-cx-hint]');
  var status = document.querySelector('[data-cx-status]');
  var live = document.querySelector('[data-cx-live]');
  var input = document.querySelector('[data-cx-input]');
  var resetBtn = document.querySelector('[data-cx-reset]');
  [controls, zoomBox, hint].forEach(function (n) { if (n) { n.hidden = false; } });
  document.documentElement.classList.add('cx-js');

  /* ---------- filters and the finder ---------- */
  var ranksOn = {}, tiersOn = {}, query = '';

  function anyFilter() { return Object.keys(ranksOn).length > 0 || Object.keys(tiersOn).length > 0 || query !== ''; }
  function tierOk(tier) { return !Object.keys(tiersOn).length || !!tiersOn[tier]; }
  function visible(c) {
    var t = topics[c.home];
    if (!t) { return false; }
    if (Object.keys(ranksOn).length && !ranksOn[c.rank]) { return false; }
    if (!tierOk(t[2])) { return false; }
    if (query) {
      var words = query.split(/\s+/);
      for (var i = 0; i < words.length; i++) { if (c.find.indexOf(words[i]) < 0) { return false; } }
    }
    return true;
  }

  /* A tier filter picks the concepts that tier explains. Their curves still run to every topic that
     uses them, in any tier, so the topic nodes of other tiers stay as endpoints. Only the leaves of the
     other tiers fade. */
  function applyFilters() {
    var shown = 0;
    order.forEach(function (c) {
      var ok = visible(c);
      c.ok = ok;
      if (ok) { shown++; }
      if (c.leaf) { c.leaf.classList.toggle('is-off', !ok); }
      if (fanEls[c.id]) { fanEls[c.id].classList.toggle('is-off', !ok); }
      if (c.entry) { c.entry.classList.toggle('is-filtered-out', !ok); }
    });
    curveEls.forEach(function (p) {
      var c = concepts[p.getAttribute('data-from')];
      p.classList.toggle('is-off', !(c && c.ok));
    });
    topicSecs.forEach(function (sec) {
      var hasRows = !!sec.querySelector('li.cx-concept');
      var any = !!sec.querySelector('li.cx-concept:not(.is-filtered-out)');
      sec.classList.toggle('is-filtered-out', hasRows ? !any : anyFilter());
    });
    tierSecs.forEach(function (sec) {
      sec.classList.toggle('is-filtered-out', !sec.querySelector('.cx-topic-sec:not(.is-filtered-out)'));
    });
    if (resetBtn) { resetBtn.hidden = !anyFilter(); }
    status.textContent = anyFilter() ? shown + ' of ' + order.length + ' concepts shown.' : '';
    if (sel && sel.type === 'concept' && !concepts[sel.id].ok) { clearSel(); }
    paintRoving();
  }

  all('[data-cx-rank]').forEach(function (b) {
    b.addEventListener('click', function () {
      var r = b.getAttribute('data-cx-rank');
      var on = b.getAttribute('aria-pressed') !== 'true';
      b.setAttribute('aria-pressed', on ? 'true' : 'false');
      if (on) { ranksOn[r] = true; } else { delete ranksOn[r]; }
      applyFilters();
    });
  });
  all('[data-cx-tier]').forEach(function (b) {
    b.addEventListener('click', function () {
      var t = b.getAttribute('data-cx-tier');
      var on = b.getAttribute('aria-pressed') !== 'true';
      b.setAttribute('aria-pressed', on ? 'true' : 'false');
      if (on) { tiersOn[t] = true; } else { delete tiersOn[t]; }
      applyFilters();
    });
  });
  if (resetBtn) {
    resetBtn.addEventListener('click', function () {
      ranksOn = {}; tiersOn = {}; query = ''; input.value = '';
      all('[data-cx-rank],[data-cx-tier]').forEach(function (b) { b.setAttribute('aria-pressed', 'false'); });
      applyFilters();
    });
  }
  input.addEventListener('input', function () {
    query = input.value.toLowerCase().trim();
    applyFilters();
  });
  input.addEventListener('keydown', function (e) {
    if (e.key === 'Enter') {
      e.preventDefault();
      var first = order.filter(function (c) { return c.ok; })[0];
      if (first && query) { select('concept', first.id); ensureVisible(first.leaf); }
    } else if (e.key === 'Escape' && input.value) {
      e.stopPropagation();
      input.value = ''; query = ''; applyFilters();
    }
  });

  /* ---------- selection ---------- */
  var sel = null;
  var lit = [];   // elements carrying a selection class, so the next change can undo them

  function mark(node, cls) {
    if (!node) { return; }
    node.classList.add(cls);
    lit.push([node, cls]);
  }
  function linkTopic(tid, anchor) {
    var a = topicEls[tid];
    if (!a) { return; }
    a.setAttribute('href', topics[tid][1] + '#' + anchor);
    mark(a, 'is-link');
  }
  function unmark() {
    lit.forEach(function (p) { p[0].classList.remove(p[1]); });
    lit = [];
    Object.keys(topicEls).forEach(function (id) {
      var a = topicEls[id];
      a.setAttribute('href', a.getAttribute('data-href0'));
    });
    all('.cx-leaf[aria-pressed]', svg).forEach(function (a) { a.removeAttribute('aria-pressed'); });
    all('.cx-concept.is-sel').forEach(function (n) { n.classList.remove('is-sel'); });
  }

  function select(type, id) {
    if (sel && sel.type === type && sel.id === id) { clearSel(); return; }
    unmark();
    sel = { type: type, id: id };
    svg.classList.add('has-sel');
    if (type === 'concept') {
      var c = concepts[id];
      mark(c.leaf, 'is-on'); mark(c.leaf, 'is-sel');
      if (c.leaf) { c.leaf.setAttribute('aria-pressed', 'true'); }
      if (c.entry) { mark(c.entry, 'is-sel'); }
      c.curves.forEach(function (p) { mark(p, 'is-on'); });
      mark(topicEls[c.home], 'is-on'); mark(topicEls[c.home], 'is-home');
      linkTopic(c.home, c.anchor);
      c.refs.forEach(function (r) {
        mark(topicEls[r.topic], 'is-on'); mark(topicEls[r.topic], 'is-use');
        linkTopic(r.topic, r.anchor);
      });
      renderConcept(c, panel, true);
      openPanel(c.leaf, c.name.length);
      live.textContent = 'Selected ' + c.name + ', ' + (RANKS[c.rank] || '') + '. Explained in ' + c.home +
        '. Used in ' + c.refs.length + (c.refs.length === 1 ? ' topic.' : ' topics.');
    } else {
      mark(topicEls[id], 'is-on'); mark(topicEls[id], 'is-sel'); mark(topicEls[id], 'is-home');
      (ownOf[id] || []).forEach(function (c) {
        mark(c.leaf, 'is-on');
        c.curves.forEach(function (p) { mark(p, 'is-on'); mark(topicEls[p.cxTo], 'is-on'); });
      });
      (usesOf[id] || []).forEach(function (u) {
        mark(u.c.leaf, 'is-on'); mark(u.c.leaf, 'is-used');
        mark(topicEls[u.c.home], 'is-on');
        u.c.curves.forEach(function (p) { if (p.cxTo === id) { mark(p, 'is-on'); } });
      });
      renderTopic(id);
      openPanel(topicEls[id], 0);
      live.textContent = 'Selected ' + id + ', ' + topics[id][0] + '. It explains ' + (ownOf[id] || []).length +
        ' concepts and uses ' + (usesOf[id] || []).length + ' from other topics.';
    }
  }

  function clearSel() {
    unmark();
    sel = null;
    svg.classList.remove('has-sel');
    closePanel();
    live.textContent = 'Selection cleared.';
  }

  /* ---------- the panel ---------- */
  function clearButton(handler) {
    var b = el('button', 'cx-clear', 'Clear');
    b.type = 'button';
    b.setAttribute('aria-label', 'Clear the selection');
    b.addEventListener('click', handler || clearSel);
    return b;
  }
  function pickButton(id, name) {
    var b = el('button', 'cx-pick', 'Show');
    b.type = 'button';
    b.setAttribute('aria-label', 'Show ' + name + ' on the map');
    b.addEventListener('click', function () {
      if (!(sel && sel.type === 'concept' && sel.id === id)) { select('concept', id); }
    });
    return b;
  }
  function topicLabel(tid) {
    var s = el('span', 'cx-p-topic');
    s.appendChild(el('span', 'cx-tid', tid));
    s.appendChild(document.createTextNode(' ' + topics[tid][0]));
    return s;
  }
  function reset(n) { while (n.firstChild) { n.removeChild(n.firstChild); } }

  /* The panel floats over the map's right edge while something is selected. It never covers the
     selected leaf: opening it pans the leaf clear of it. */
  var inset = 0;
  function openPanel(node, labelChars) {
    panel.hidden = false;
    panel.scrollTop = 0;
    inset = floatR.offsetWidth + 16;
    reveal(node, labelChars);
  }
  function closePanel() {
    panel.hidden = true;
    reset(panel);
    inset = 0;
    setView(view);
  }

  function renderConcept(c, box, onMap) {
    reset(box);
    var panel = box;
    var head = el('div', 'cx-p-head');
    head.appendChild(chip(c.rank));
    head.appendChild(el('span', 'cx-p-kind', 'Concept'));
    head.appendChild(clearButton(onMap ? clearSel : closeIndexPanel));
    panel.appendChild(head);
    panel.appendChild(el('h2', 'cx-p-title', c.name));
    panel.appendChild(el('p', 'cx-p-def', c.def));
    panel.appendChild(el('h3', null, 'Explained in'));
    var p = el('p', 'cx-p-home');
    var a = link(topics[c.home][1] + '#' + c.anchor);
    a.appendChild(topicLabel(c.home));
    p.appendChild(a);
    panel.appendChild(p);
    var h = el('h3', null, 'Used in ');
    h.appendChild(el('span', 'count', String(c.refs.length)));
    panel.appendChild(h);
    if (!c.refs.length) {
      panel.appendChild(el('p', 'cx-none', 'No other topic uses it yet.'));
    } else {
      var ul = el('ul', 'cx-p-list');
      c.refs.forEach(function (r) {
        var li = el('li');
        var l = link(topics[r.topic][1] + '#' + r.anchor);
        l.appendChild(topicLabel(r.topic));
        li.appendChild(l);
        li.appendChild(el('span', 'cx-how', r.how));
        ul.appendChild(li);
      });
      panel.appendChild(ul);
    }
    if (onMap) { panel.appendChild(link('#c-' + c.id, 'See it in the index', 'cx-p-index')); }
  }

  function conceptItem(c, href, extra, how) {
    var li = el('li');
    var row = el('span', 'cx-p-row');
    row.appendChild(glyph(c.rank));
    row.appendChild(link(href, c.name));
    if (extra) { row.appendChild(el('span', 'cx-from', extra)); }
    row.appendChild(pickButton(c.id, c.name));
    li.appendChild(row);
    if (how) { li.appendChild(el('span', 'cx-how', how)); }
    return li;
  }

  function renderTopic(tid) {
    var t = topics[tid];
    reset(panel);
    var head = el('div', 'cx-p-head');
    head.appendChild(chip(t[3]));
    head.appendChild(el('span', 'cx-p-kind', 'Topic, ' + (TIERS[t[2]] || '')));
    head.appendChild(clearButton());
    panel.appendChild(head);
    var h2 = el('h2', 'cx-p-title');
    var a = link(t[1]);
    a.appendChild(topicLabel(tid));
    h2.appendChild(a);
    panel.appendChild(h2);
    var own = ownOf[tid] || [];
    var h = el('h3', null, 'Explains ');
    h.appendChild(el('span', 'count', String(own.length)));
    panel.appendChild(h);
    var ul = el('ul', 'cx-p-list');
    own.forEach(function (c) { ul.appendChild(conceptItem(c, t[1] + '#' + c.anchor, '', '')); });
    panel.appendChild(ul);
    var used = usesOf[tid] || [];
    var h3 = el('h3', null, 'Uses from other topics ');
    h3.appendChild(el('span', 'count', String(used.length)));
    panel.appendChild(h3);
    if (!used.length) {
      panel.appendChild(el('p', 'cx-none', 'It uses no concept from other topics.'));
    } else {
      var ul2 = el('ul', 'cx-p-list');
      used.slice().sort(function (x, y) { return x.c.home < y.c.home ? -1 : x.c.home > y.c.home ? 1 : 0; }).forEach(function (u) {
        ul2.appendChild(conceptItem(u.c, t[1] + '#' + u.ref.anchor, 'from ' + u.c.home, u.ref.how));
      });
      panel.appendChild(ul2);
    }
  }

  /* ---------- zoom and pan ---------- */
  var vb = svg.viewBox.baseVal;
  var full = { x: vb.x, y: vb.y, w: vb.width, h: vb.height };
  var view = { x: full.x, y: full.y, w: full.w, h: full.h };

  function setView(v) {
    var w = Math.max(full.w / MAX_ZOOM, Math.min(full.w, v.w));
    var h = w * full.h / full.w;
    /* While the panel is open, the view can slide left by the panel's width, so the map can clear it. */
    var room = inset ? inset * w / Math.max(1, svg.getBoundingClientRect().width) : 0;
    var x = Math.max(full.x, Math.min(full.x + full.w - w + room, v.x));
    var y = Math.max(full.y, Math.min(full.y + full.h - h, v.y));
    view = { x: x, y: y, w: w, h: h };
    svg.setAttribute('viewBox', [x, y, w, h].map(function (n) { return Math.round(n * 10) / 10; }).join(' '));
    svg.classList.toggle('is-zoomed', w < full.w - 0.5);
  }
  function toSvg(cx, cy) {
    var r = svg.getBoundingClientRect();
    return { x: view.x + (cx - r.left) / r.width * view.w, y: view.y + (cy - r.top) / r.height * view.h };
  }
  function zoomAt(factor, p) {
    var w = Math.max(full.w / MAX_ZOOM, Math.min(full.w, view.w / factor));
    var k = w / view.w;
    setView({ x: p.x - (p.x - view.x) * k, y: p.y - (p.y - view.y) * k, w: w });
  }
  function zoomCentre(factor) { zoomAt(factor, { x: view.x + view.w / 2, y: view.y + view.h / 2 }); }
  function resetView() { setView(full); }
  /* Bring a node into view. With the panel open, the node must also sit clear of it, with room for
     its label when the label runs to the right. */
  function reveal(node, labelChars) {
    if (!node) { return; }
    var x = parseFloat(node.getAttribute('data-x')), y = parseFloat(node.getAttribute('data-y'));
    var perPx = view.w / Math.max(1, svg.getBoundingClientRect().width);
    var pu = inset * perPx;
    var m = 40;
    var right = x > 0 ? m + (labelChars || 0) * 7.2 : m;
    var nx = view.x, ny = view.y;
    if (x > view.x + view.w - pu - right) { nx = x - (view.w - pu - right); }
    if (x < view.x + m) { nx = x - m; }
    if (y < view.y + m || y > view.y + view.h - m) { ny = y - view.h / 2; }
    if (nx !== view.x || ny !== view.y) { setView({ x: nx, y: ny, w: view.w }); }
  }
  function ensureVisible(node) { reveal(node, 0); }

  var zin = document.querySelector('[data-cx-zoom-in]');
  var zout = document.querySelector('[data-cx-zoom-out]');
  var zreset = document.querySelector('[data-cx-zoom-reset]');
  if (zin) { zin.addEventListener('click', function () { zoomCentre(1.5); }); }
  if (zout) { zout.addEventListener('click', function () { zoomCentre(1 / 1.5); }); }
  if (zreset) { zreset.addEventListener('click', resetView); }

  svg.addEventListener('wheel', function (e) {
    if (!(e.ctrlKey || e.metaKey)) { return; }
    e.preventDefault();
    var d = Math.max(-40, Math.min(40, e.deltaY));
    zoomAt(Math.exp(-d * 0.02), toSvg(e.clientX, e.clientY));
  }, { passive: false });

  var pointers = {};
  var moved = false, suppress = false, lastDist = 0;
  function count() { return Object.keys(pointers).length; }
  svg.addEventListener('pointerdown', function (e) {
    if (e.pointerType === 'mouse' && e.button !== 0) { return; }
    pointers[e.pointerId] = { x: e.clientX, y: e.clientY, sx: e.clientX, sy: e.clientY };
    if (count() === 2) {
      var ids = Object.keys(pointers);
      lastDist = Math.hypot(pointers[ids[0]].x - pointers[ids[1]].x, pointers[ids[0]].y - pointers[ids[1]].y);
    }
    moved = false;
  });
  window.addEventListener('pointermove', function (e) {
    var p = pointers[e.pointerId];
    if (!p) { return; }
    if (count() === 2) {
      var ids = Object.keys(pointers);
      p.x = e.clientX; p.y = e.clientY;
      var a = pointers[ids[0]], b = pointers[ids[1]];
      var dist = Math.hypot(a.x - b.x, a.y - b.y);
      if (lastDist > 0 && dist > 0) { zoomAt(dist / lastDist, toSvg((a.x + b.x) / 2, (a.y + b.y) / 2)); }
      lastDist = dist; moved = true;
      return;
    }
    if (!moved && Math.hypot(e.clientX - p.sx, e.clientY - p.sy) < 5) { return; }
    var r = svg.getBoundingClientRect();
    var dx = (e.clientX - p.x) * view.w / r.width, dy = (e.clientY - p.y) * view.h / r.height;
    p.x = e.clientX; p.y = e.clientY;
    if (!moved) { moved = true; svg.classList.add('is-dragging'); dx = 0; dy = 0; }
    setView({ x: view.x - dx, y: view.y - dy, w: view.w });
  });
  function release(e) {
    if (!pointers[e.pointerId]) { return; }
    delete pointers[e.pointerId];
    if (moved) {
      suppress = true;
      setTimeout(function () { suppress = false; }, 0);
    }
    if (!count()) { moved = false; svg.classList.remove('is-dragging'); }
  }
  window.addEventListener('pointerup', release);
  window.addEventListener('pointercancel', release);

  /* ---------- clicks and keys on the map ---------- */
  svg.addEventListener('click', function (e) {
    if (suppress) { e.preventDefault(); e.stopPropagation(); return; }
    var a = e.target.closest ? e.target.closest('a') : null;
    if (!a) { if (sel) { clearSel(); } return; }
    if (e.metaKey || e.ctrlKey || e.shiftKey || e.altKey || e.button) { return; }
    if (a.classList.contains('cx-leaf')) {
      e.preventDefault();
      select('concept', a.getAttribute('data-c'));
    } else if (a.classList.contains('cx-topic')) {
      if (a.classList.contains('is-link')) { return; }
      e.preventDefault();
      select('topic', a.getAttribute('data-t'));
    }
  });

  var items = all('.cx-topic, .cx-leaf', svg);
  var current = null;
  function paintRoving() {
    if (!current || current.classList.contains('is-off')) {
      current = items.filter(function (n) { return !n.classList.contains('is-off'); })[0] || null;
    }
    items.forEach(function (n) { n.setAttribute('tabindex', n === current ? '0' : '-1'); });
  }
  function move(step, from) {
    var i = items.indexOf(from);
    for (var k = i + step; k >= 0 && k < items.length; k += step) {
      if (!items[k].classList.contains('is-off')) { return items[k]; }
    }
    return null;
  }
  svg.addEventListener('focusin', function (e) {
    var a = e.target.closest ? e.target.closest('a.cx-topic, a.cx-leaf') : null;
    if (a && a !== current) { current = a; paintRoving(); }
  });
  svg.addEventListener('keydown', function (e) {
    var a = e.target.closest ? e.target.closest('a.cx-topic, a.cx-leaf') : null;
    var next = null;
    if (e.key === '+' || e.key === '=') { e.preventDefault(); zoomCentre(1.5); return; }
    if (e.key === '-' || e.key === '_') { e.preventDefault(); zoomCentre(1 / 1.5); return; }
    if (e.key === '0') { e.preventDefault(); resetView(); return; }
    if (!a) { return; }
    if (e.key === 'ArrowRight' || e.key === 'ArrowDown') { next = move(1, a); }
    else if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') { next = move(-1, a); }
    else if (e.key === 'Home') { next = items.filter(function (n) { return !n.classList.contains('is-off'); })[0]; }
    else if (e.key === 'End') { var vis = items.filter(function (n) { return !n.classList.contains('is-off'); }); next = vis[vis.length - 1]; }
    else if (e.key === 'Enter' || e.key === ' ') {
      if (e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) { return; }
      e.preventDefault();
      if (a.classList.contains('is-link')) { window.location.href = a.getAttribute('href'); return; }
      a.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true }));
      return;
    } else { return; }
    e.preventDefault();
    if (next) { current = next; paintRoving(); ensureVisible(next); next.focus(); }
  });
  document.addEventListener('keydown', function (e) {
    if (e.key !== 'Escape' || e.target === input) { return; }
    if (sel) { clearSel(); }
    if (activeUse) { closeIndexPanel(); }
  });

  /* ---------- the index: concept cards ---------- */
  /* Each concept's definition and uses sit in a details element, so they show without the script.
     With it, the whole row acts as a card: a click on the name follows the link, and a click
     anywhere else opens the concept. On a wide screen that fills the panel beside the index; on a
     narrow one the details element opens under its row. The summary stays the keyboard control. */
  var activeUse = null;
  var wide = window.matchMedia ? window.matchMedia('(min-width: 64rem)') : { matches: false };
  function placeholder() {
    reset(indexPanel);
    indexPanel.appendChild(el('p', 'cx-none', 'Choose a concept to see where it is explained and where it is used.'));
  }
  function closeIndexPanel() {
    if (activeUse) { activeUse.parentNode.classList.remove('is-open'); }
    activeUse = null;
    if (indexPanel) { placeholder(); }
  }
  function openCard(d) {
    if (!wide.matches) {
      d.open = !d.open;
      d.parentNode.classList.toggle('is-open', d.open);
      return;
    }
    var c = concepts[d.getAttribute('data-c')];
    var same = activeUse === d;
    closeIndexPanel();
    if (same || !c) { return; }
    activeUse = d;
    d.parentNode.classList.add('is-open');
    renderConcept(c, indexPanel, false);
    live.textContent = c.name + ': explained in ' + c.home + ', used in ' + c.refs.length + (c.refs.length === 1 ? ' topic.' : ' topics.');
  }
  if (indexPanel) {
    indexPanel.hidden = false;
    document.documentElement.classList.add('cx-js-index');
    placeholder();
    all('.cx-concept').forEach(function (li) {
      var d = li.querySelector('.cx-uses');
      if (!d) { return; }
      li.classList.add('is-card');
      li.addEventListener('click', function (e) {
        var t = e.target;
        if (t.closest('a')) { return; }
        if (t.closest('summary')) { e.preventDefault(); }
        else if (t.closest('.cx-uses')) { return; }
        if (window.getSelection && String(window.getSelection())) { return; }
        openCard(d);
      });
    });
    /* A details element opened another way, as by find in page, keeps its card in step. */
    wide.addEventListener && wide.addEventListener('change', function () {
      all('.cx-uses[open]').forEach(function (d) { d.open = false; d.parentNode.classList.remove('is-open'); });
      closeIndexPanel();
    });
  }

  applyFilters();
})();
